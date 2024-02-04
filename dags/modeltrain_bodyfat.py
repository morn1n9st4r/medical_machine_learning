from datetime import datetime, timedelta
import os
import pickle
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator


from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
import psycopg2
from sklearn.ensemble import RandomForestRegressor

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error


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

    bodyfatDF = pd.read_sql_query('select * from bodyfatDF',con=conn)


    X = bodyfatDF.drop(columns='bodyfat')
    y = bodyfatDF['bodyfat']

    from sklearn.preprocessing import StandardScaler

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


    # scale on train data and apply it to test data
    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(X_train)
    x_test_scaled = scaler.transform(X_test)


    model = RandomForestRegressor()

    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [6, 8, 10],
        'max_samples': [0.6, 0.65, 0.7],
        'random_state': [0]
    }

    grid_search = GridSearchCV(estimator=model, param_grid=param_grid, scoring='neg_mean_squared_error', cv=5, verbose=2)
    grid_search.fit(x_train_scaled, y_train)
    
    print("Best Hyperparameters:", grid_search.best_params_)

    best_model = grid_search.best_estimator_
    best_model.fit(x_train_scaled, y_train)

    y_pred = best_model.predict(x_test_scaled)
    y_pred_df = pd.DataFrame({'bodyfat': y_pred})
    y_pred_df.to_csv("y_pred", index=False)

    y_test.to_csv("y_test", index=False)

    with open('bodyfat_scaler.pkl', 'wb') as file:
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
            host='rdsterraform.cvyu8kkk0p75.eu-west-3.rds.amazonaws.com',
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
    directory_path = '/opt/airflow/'
    matching_files = [file for file in os.listdir(directory_path) if file.startswith('bodyfat_')]
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

    train_task >> validate_task 
    validate_task >> upload_params_task >> upload_task
    remove_bodyfat_csv_task >> train_task
    remove_bodyfat_pkl_task >> train_task
    remove_bodyfat_date_pkl >> train_task