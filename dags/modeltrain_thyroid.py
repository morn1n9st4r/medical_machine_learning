from datetime import datetime, timedelta
import os
import pickle
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator


from airflow.providers.amazon.aws.operators.s3 import S3CreateObjectOperator
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
import psycopg2

import xgboost as xgb
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.metrics import balanced_accuracy_score, accuracy_score, precision_score, recall_score, f1_score
from sklearn.utils.class_weight import compute_sample_weight


import numpy as np
import pandas as pd 


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def train_model(**kwargs):
    print("Training model")

    #thyroidDF = pd.read_csv("thyroidDF")

    conn = psycopg2.connect(
        dbname='medicalmldb',
        user='medicalmladmin',
        password='Qwerty12345',
        host='rdsterraform.cdwy46wiszkf.eu-north-1.rds.amazonaws.com',
        port='5432'
    )

    thyroidDF = pd.read_sql_query('select * from thyroidDF',con=conn)

    thyroidDF.replace('f', 0, inplace=True)
    thyroidDF.replace('t', 1, inplace=True)

    thyroidDF.replace('M', 0, inplace=True)
    thyroidDF.replace('F', 1, inplace=True)

    xgbDF = thyroidDF.replace(np.nan, 0)

    diagnoses = {'negative': 0,
                'hypothyroid': 1, 
                'hyperthyroid': 2}

    xgbDF['target'] = xgbDF['target'].map(diagnoses) # re-mapping

    # train and test split --> stratified
    X = xgbDF.drop('target', axis=1).copy()
    y = xgbDF['target'].copy()

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

    with open('xgb_thyroid.pkl', 'wb') as file:
        pickle.dump(best_xgb_clf, file)



def validate_model(**kwargs):
    print("Validating model")
    
    X_test = pd.read_csv("X_test")
    y_test = pd.read_csv("y_test")

    with open("/opt/airflow/xgb_thyroid.pkl", 'rb') as file:
        
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
        print('---------------------- XGBoost ----------------------')
    


def upload_params(**kwargs):
    print("Validating model")
    
    y_test = pd.read_csv("y_test")
    y_pred = pd.read_csv("y_pred")

    with open("/opt/airflow/xgb_thyroid.pkl", 'rb') as file:

        xgb_clf = pickle.load(file)

        conn = psycopg2.connect(
            dbname='medicalmldb',
            user='medicalmladmin',
            password='Qwerty12345',
            host='rdsterraform.cdwy46wiszkf.eu-north-1.rds.amazonaws.com',
            port='5432'
        )
        cur = conn.cursor()
        date = datetime.now().strftime("%m_%d_%Y_%H_%M")

        cur.execute("""INSERT INTO public.main_mlmodel (modeltype, traindate, parameters, val_accuracy) 
                    VALUES (%s, %s,%s, %s)""",
                    ('thyroid', datetime.now(), str(xgb_clf.get_xgb_params()), accuracy_score(y_test, y_pred)))
        
        with open('thyroid_' + date + '.pkl', 'wb') as file:
            pickle.dump(xgb_clf, file)
            
        conn.commit()
        cur.close()
        conn.close()


def upload_files_to_s3():
    # Directory containing the files with the specified pattern
    directory_path = '/opt/airflow/'
    # Find files matching the pattern
    matching_files = [file for file in os.listdir(directory_path) if file.startswith('thyroid_')]
    # Upload matching files to S3
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
    'train_thyroid_model',
    start_date=datetime(2023, 3, 21),
    schedule_interval="@daily",
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

    remove_thyroid_csv_task = BashOperator(
        task_id='remove_thyroid_csv',
        bash_command='rm -f /opt/airflow/thyroid*.csv',
        dag=dag,
    )

    remove_xgb_thyroid_pkl_task = BashOperator(
        task_id='remove_xgb_thyroid_pkl',
        bash_command='rm -f /opt/airflow/xgb_thyroid.pkl',
        dag=dag,
    )

    remove_thyroid_pkl_task = BashOperator(
        task_id='remove_thyroid_pkl',
        bash_command='rm -f /opt/airflow/thyroid*.pkl',
        dag=dag,
    )

    train_task >> validate_task 
    validate_task >> upload_params_task >> upload_task
    remove_thyroid_csv_task >> train_task
    remove_xgb_thyroid_pkl_task >> train_task
    remove_thyroid_pkl_task >> train_task