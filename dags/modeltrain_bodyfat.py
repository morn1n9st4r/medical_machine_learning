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
from sklearn.ensemble import RandomForestRegressor

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import confusion_matrix, classification_report, mean_absolute_error, mean_squared_error
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


def fetch_data(**kwargs):
    print("Fetching data")

    bodyfatDF = pd.read_csv('/opt/airflow/dags/data/bodyfat.csv')
    bodyfatDF.to_csv("bodyfat", index=False)




def preprocess_data(**kwargs):
    print("Preprocessing data")

    bodyfatDF = pd.read_csv("bodyfat")

    bodyfatDF.drop(columns=['Original'], inplace=True)

    bodyfatDF['Sex'] = bodyfatDF['Sex'].replace({'M': 'Male', 'F': 'Female'})

    print("NaN values:")

    sex_mapping = {'Male': 1, 'Female': 0}

    bodyfatDF['Sex'] = bodyfatDF['Sex'].map(sex_mapping)

    bodyfatDF.to_csv("bodyfatDF", index=False)



def train_model(**kwargs):
    print("Training model")

    bodyfatDF = pd.read_csv("bodyfatDF")


    X = bodyfatDF.drop(columns='BodyFat')
    y = bodyfatDF['BodyFat']

    from sklearn.preprocessing import StandardScaler



    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


    # scale on train data and apply it to test data
    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(X_train)
    x_test_scaled = scaler.transform(X_test)


    model = RandomForestRegressor()

    # Define the parameter grid for GridSearchCV
    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [6, 8, 10],
        'max_samples': [0.6, 0.65, 0.7],
        'random_state': [0]
    }

    # Perform GridSearchCV
    grid_search = GridSearchCV(estimator=model, param_grid=param_grid, scoring='neg_mean_squared_error', cv=5, verbose=2)
    grid_search.fit(x_train_scaled, y_train)

    # Print the best hyperparameters
    print("Best Hyperparameters:", grid_search.best_params_)

    # Get the best model from GridSearchCV
    best_model = grid_search.best_estimator_

    # Fit the best model on the entire training set
    best_model.fit(x_train_scaled, y_train)

    y_pred = best_model.predict(x_test_scaled)
    y_pred_df = pd.DataFrame({'BodyFat': y_pred})
    y_pred_df.to_csv("y_pred", index=False)

    y_test.to_csv("y_test", index=False)

    with open('scaler.pkl', 'wb') as file:
        pickle.dump(scaler, file)

    with open('rfr.pkl', 'wb') as file:
        pickle.dump(best_model, file)


def validate_model(**kwargs):
    print("Validating model")
    
    y_test = pd.read_csv("y_test")
    y_pred = pd.read_csv("y_pred")


    mse_test = mean_squared_error(y_test, y_pred).round(3)
    mae_test = mean_absolute_error(y_test, y_pred).round(3)

    print(f"Test | Mean Squared Error: {mse_test} | Mean Absolute Error: {mae_test}")
    print('---------------------- RandomForestRegressor ----------------------')
    


def upload_params(**kwargs):
    print("Validating model")
    
    y_test = pd.read_csv("y_test")
    y_pred = pd.read_csv("y_pred")

    with open("/opt/airflow/rfr.pkl", 'rb') as file:

        rfr = pickle.load(file)

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
                    ('bodyfat', datetime.now(), str(rfr.get_params()), mean_absolute_error(y_test, y_pred)))
        
        with open('bodyfat_' + date + '.pkl', 'wb') as file:
            pickle.dump(rfr, file)
            
        conn.commit()
        cur.close()
        conn.close()


def upload_files_to_s3():
    # Directory containing the files with the specified pattern
    directory_path = '/opt/airflow/'
    # Find files matching the pattern
    matching_files = [file for file in os.listdir(directory_path) if file.startswith('bodyfat_')]
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
    'train_bodyfat_model',
    start_date=datetime(2023, 3, 21),
    schedule_interval="@daily",
    catchup=False
) as dag:

    # Define tasks
    fetch_task = PythonOperator(
        task_id='fetch_data',
        python_callable=fetch_data,
        dag=dag,
    )

    preprocess_task = PythonOperator(
        task_id='preprocess_data',
        python_callable=preprocess_data,
        dag=dag,
    )

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

    remove_bodyfat_csv_task = BashOperator(
        task_id='remove_bodyfat_csv',
        bash_command='rm -f /opt/airflow/bodyfat*.csv',
        dag=dag,
    )

    remove_bodyfat_pkl_task = BashOperator(
        task_id='remove_bodyfat_pkl',
        bash_command='rm -f /opt/airflow/bodyfat.pkl',
        dag=dag,
    )

    remove_bodyfat_date_pkl = BashOperator(
        task_id='remove_bodyfat_date_pkl',
        bash_command='rm -f /opt/airflow/bodyfat*.pkl',
        dag=dag,
    )

    fetch_task >> preprocess_task >> train_task >> validate_task 
    validate_task >> upload_params_task >> upload_task
    remove_bodyfat_csv_task >> fetch_task
    remove_bodyfat_pkl_task >> fetch_task
    remove_bodyfat_date_pkl >> fetch_task