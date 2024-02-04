from datetime import datetime, timedelta
import os
import pickle
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator


from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
import psycopg2

import xgboost as xgb
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.metrics import balanced_accuracy_score, accuracy_score, precision_score, recall_score, f1_score


import pandas as pd 


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def train_model(**kwargs):
    print("Training model")

    conn = psycopg2.connect(
        dbname='medicalmldb',
        user='medicalmladmin',
        password='Qwerty12345',
        host='rdsterraform.cvyu8kkk0p75.eu-west-3.rds.amazonaws.com',
        port='5432'
    )

    bloodDF = pd.read_sql_query('select * from bloodDF',con=conn)

    # apparently SQL 'ALTER COLUMN sex TYPE int using sex::int;' doesn't work
    # finish transformations directly before model training  
    bloodDF['sex'] = pd.to_numeric(bloodDF['sex'])
    bloodDF['target'] = pd.to_numeric(bloodDF['target'])


    X = bloodDF.drop('target', axis=1).copy()
    y = bloodDF['target'].copy()

    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42, stratify=y)



    xgb_clf = xgb.XGBClassifier(objective='multi:softmax', 
                                num_class=3, 
                                missing=1,
                                eval_metric=['merror','mlogloss'], 
                                seed=42)

    param_grid = {
        'learning_rate': [0.01, 0.1, 0.2],
        'max_depth': [3, 4, 5],
        'n_estimators': [50, 100, 200]
    }

    grid_search = GridSearchCV(estimator=xgb_clf, param_grid=param_grid, scoring='accuracy', cv=3, verbose=3)
    grid_search.fit(X_train, y_train)
    print("Best Hyperparameters:", grid_search.best_params_)

    best_xgb_clf = grid_search.best_estimator_
    best_xgb_clf.fit(X_train, y_train)

    X_test.to_csv("X_test", index=False)
    y_test.to_csv("y_test", index=False)

    with open('xgb_blood.pkl', 'wb') as file:
        pickle.dump(best_xgb_clf, file)



def validate_model(**kwargs):
    print("Validating model")
    
    X_test = pd.read_csv("X_test")
    y_test = pd.read_csv("y_test")

    with open("/opt/airflow/xgb_blood.pkl", 'rb') as file:
        
        xgb_clf = pickle.load(file)

        y_pred = xgb_clf.predict(X_test)
        y_pred_df = pd.DataFrame({'target': y_pred})
        y_pred_df.to_csv("y_pred", index=False)

        print('\n------------------ Confusion Matrix -----------------\n')
        print(confusion_matrix(y_test, y_pred))

        print('\n-------------------- Key Metrics --------------------')
        print('\nAccuracy: {:.2f}'.format(accuracy_score(y_test, y_pred)))
        print('Balanced Accuracy: {:.2f}\n'.format(balanced_accuracy_score(y_test, y_pred)))

        print('Micro Precision: {:.2f}'.format(precision_score(y_test, y_pred, average='micro')))
        print('Micro Recall: {:.2f}'.format(recall_score(y_test, y_pred, average='micro')))
        print('Micro F1-score: {:.2f}\n'.format(f1_score(y_test, y_pred, average='micro')))

        print('Macro Precision: {:.2f}'.format(precision_score(y_test, y_pred, average='macro')))
        print('Macro Recall: {:.2f}'.format(recall_score(y_test, y_pred, average='macro')))
        print('Macro F1-score: {:.2f}\n'.format(f1_score(y_test, y_pred, average='macro')))

        print('Weighted Precision: {:.2f}'.format(precision_score(y_test, y_pred, average='weighted')))
        print('Weighted Recall: {:.2f}'.format(recall_score(y_test, y_pred, average='weighted')))
        print('Weighted F1-score: {:.2f}'.format(f1_score(y_test, y_pred, average='weighted')))

        print('\n--------------- Classification Report ---------------\n')
        print(classification_report(y_test, y_pred))
        print('---------------------- RFC ----------------------')
    


def upload_params(**kwargs):
    print("Validating model")
    
    y_test = pd.read_csv("y_test")
    y_pred = pd.read_csv("y_pred")

    with open("/opt/airflow/xgb_blood.pkl", 'rb') as file:

        xgb_clf = pickle.load(file)

        conn = psycopg2.connect(
            dbname='medicalmldb',
            user='medicalmladmin',
            password='Qwerty12345',
            host='rdsterraform.cvyu8kkk0p75.eu-west-3.rds.amazonaws.com',
            port='5432'
        )
        cur = conn.cursor()
        date = datetime.now().strftime("%m_%d_%Y_%H_%M")

        cur.execute("""INSERT INTO public.main_mlmodel (modeltype, traindate, parameters, val_accuracy) 
                    VALUES (%s, %s,%s, %s)""",
                    ('blood', datetime.now(), str(xgb_clf.get_xgb_params()), accuracy_score(y_test, y_pred)))
        
        with open('blood_' + date + '.pkl', 'wb') as file:
            pickle.dump(xgb_clf, file)
            
        conn.commit()
        cur.close()
        conn.close()


def upload_files_to_s3():
    directory_path = '/opt/airflow/'
    matching_files = [file for file in os.listdir(directory_path) if file.startswith('blood_')]
    for file in matching_files:
        upload_task = LocalFilesystemToS3Operator(
            task_id=f'upload_{file}',
            aws_conn_id='AWS_CONN',
            filename=os.path.join(directory_path, file),
            dest_bucket='medicalmlbucket',
            dest_key=f'model/{file}',
            replace=True,
            dag=dag,
        )
        upload_task.execute(dict())


with DAG(
    'train_blood_model',
    start_date=datetime(2023, 3, 21),
    schedule_interval="@weekly",
    catchup=False
) as dag:


    train_task = PythonOperator(
        task_id='train_model',
        python_callable=train_model,
        dag=dag,
    )

    validate_task = PythonOperator(
        task_id='validate_model',
        python_callable=validate_model,
        dag=dag,
    )

    upload_params_task =  PythonOperator(
        task_id='upload_params',
        python_callable=upload_params,
        dag=dag,
    )

    upload_task  = PythonOperator(
        task_id='execute_upload',
        python_callable=upload_files_to_s3,
    )

    remove_blood_csv_task = BashOperator(
        task_id='remove_blood_csv',
        bash_command='rm -f /opt/airflow/blood*.csv',
        dag=dag,
    )

    remove_xgb_blood_pkl_task = BashOperator(
        task_id='remove_xgb_blood_pkl',
        bash_command='rm -f /opt/airflow/xgb_blood.pkl',
        dag=dag,
    )

    remove_blood_pkl_task = BashOperator(
        task_id='remove_blood_pkl',
        bash_command='rm -f /opt/airflow/blood*.pkl',
        dag=dag,
    )

    train_task >> validate_task 
    validate_task >> upload_params_task >> upload_task
    remove_blood_csv_task >> train_task
    remove_xgb_blood_pkl_task >> train_task
    remove_blood_pkl_task >> train_task