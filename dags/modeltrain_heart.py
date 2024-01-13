from datetime import datetime, timedelta
import os
import pickle
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator


from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
from lightgbm import LGBMClassifier
import psycopg2
from sklearn.metrics import accuracy_score

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import balanced_accuracy_score, classification_report, confusion_matrix, f1_score, mean_absolute_error, mean_squared_error, precision_score, recall_score


from keras import Sequential #Helps to create Forward and backward propogation
from keras.layers import Dense #Helps to create neurons in ANN
from keras.optimizers import Adam

import tensorflow as tf

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
        host='rdsterraform.cdwy46wiszkf.eu-north-1.rds.amazonaws.com',
        port='5432'
    )

    heartDF = pd.read_sql_query('select * from heartDF',con=conn)


    X = heartDF.drop('heart_disease', axis=1).copy()

    y = heartDF['heart_disease'].copy()

    from sklearn import preprocessing

    heart_label_encoder = preprocessing.LabelEncoder()

    y = heart_label_encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

    
    model = Sequential()

    # Input layer
    model.add(Dense(units=16, activation='relu', input_dim=X_train.shape[1]))
    #model.add(Dropout(0.2))  # Adding dropout for regularization

    # Hidden layers
    #model.add(Dense(units=64, activation='relu'))
    #model.add(Dropout(0.5))  # Adding dropout for regularization

    model.add(Dense(units=8, activation='relu'))
    model.add(Dense(units=4, activation='relu'))
    #model.add(Dropout(0.2))  # Adding dropout for regularization

    # Output layer
    model.add(Dense(units=1, activation='sigmoid'))

    # Compile the model
    model.compile(optimizer=Adam(lr=0.0001), loss='binary_crossentropy', metrics=['accuracy'])
        

    early_stopping=tf.keras.callbacks.EarlyStopping(
        monitor='val_loss',
        min_delta=0.00001,
        patience=20,
        verbose=1,
        mode='auto',
        restore_best_weights=True
    )

    import numpy as np


    X_train=np.asarray(X_train).astype(int)
    y_train=np.asarray(y_train).astype(int)

    model_history = model.fit(
        X_train,
        y_train,
        validation_split=0.33,
        batch_size=10,
        epochs=1000,
        callbacks=[early_stopping]
    )
            
    """lgbm_classifier = LGBMClassifier()

    param_grid = {
        'n_estimators': [50, 100, 200],
        'learning_rate': [0.01, 0.1, 0.2],
        'colsample_bytree' : [0.64, 0.65, 0.66],
        'boosting_type' : ['gbdt', 'dart'], # for better accuracy -> try dart
        'verbose': [-1],
    }

    grid_search = GridSearchCV(lgbm_classifier, param_grid, cv=3, scoring='accuracy', verbose=3)

    grid_search.fit(X_train, y_train)
    
    print("Best Hyperparameters:", grid_search.best_params_)

    best_model = grid_search.best_estimator_
    best_model.fit(X_train, y_train)"""

    y_pred = model.predict(X_test)
    y_pred_bin = np.where(y_pred > 0.5, 1, 0)
    y_pred_unp = y_pred_bin[:, 0]
    
    print(y_pred_unp[:10])
    print(y_test[:10])

    y_pred_df = pd.DataFrame({'heart_disease': y_pred_unp})
    y_pred_df.to_csv("y_pred", index=False)

    y_test_df = pd.DataFrame({'heart_disease': y_test})
    y_test_df.to_csv("y_test", index=False)

    with open('heart_label_encoder.pkl', 'wb') as file:
        pickle.dump(heart_label_encoder, file)

    with open('ann.pkl', 'wb') as file:
        pickle.dump(model, file)


def validate_model(**kwargs):
    print("Validating model")
    
    y_test = pd.read_csv("y_test")
    y_pred = pd.read_csv("y_pred")

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
    print('---------------------- LightGBM ----------------------')
    

def upload_params(**kwargs):
    print("Validating model")
    
    y_test = pd.read_csv("y_test")
    y_pred = pd.read_csv("y_pred")

    with open("/opt/airflow/ann.pkl", 'rb') as file:

        ann = pickle.load(file)

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
                    ('heart', datetime.now(), str(ann.get_weights()), mean_absolute_error(y_test, y_pred)))
        
        with open('heart_' + date + '.pkl', 'wb') as file:
            pickle.dump(ann, file)
            
        conn.commit()
        cur.close()
        conn.close()


def upload_files_to_s3():
    directory_path = '/opt/airflow/'
    matching_files = [file for file in os.listdir(directory_path) if file.startswith('heart_')]
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
    'train_heart_model',
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

    remove_heart_csv_task = BashOperator(
        task_id='remove_heart_csv',
        bash_command='rm -f /opt/airflow/heart*.csv',
        dag=dag,
    )

    remove_heart_pkl_task = BashOperator(
        task_id='remove_heart_pkl',
        bash_command='rm -f /opt/airflow/heart.pkl',
        dag=dag,
    )

    remove_heart_date_pkl = BashOperator(
        task_id='remove_heart_date_pkl',
        bash_command='rm -f /opt/airflow/heart*.pkl',
        dag=dag,
    )

    train_task >> validate_task 
    validate_task >> upload_params_task >> upload_task
    remove_heart_csv_task >> train_task
    remove_heart_pkl_task >> train_task
    remove_heart_date_pkl >> train_task