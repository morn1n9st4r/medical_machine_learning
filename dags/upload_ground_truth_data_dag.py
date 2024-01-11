import os
from airflow import DAG
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python_operator import PythonOperator

from datetime import datetime, timedelta
from airflow.hooks.S3_hook import S3Hook

import psycopg2
from psycopg2.extras import execute_values

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def download_from_s3(filename, **kwargs):
    hook = S3Hook(aws_conn_id='AWS_CONN')  # Specify your AWS connection ID
    downloaded_name = hook.download_file(bucket_name='medicalmlbucket', key=f'model/{filename}', local_path='/opt/airflow/dags/')
    dst = os.path.join('/opt/airflow/dags', filename)
    os.rename(src=downloaded_name, dst=dst)


def upload(table_name):

    # Database connection parameters
    db_params = {
        'dbname': 'medicalmldb',
        'user': 'medicalmladmin',
        'password': 'Qwerty12345',
        'host': 'rdsterraform.cdwy46wiszkf.eu-north-1.rds.amazonaws.com',
        'port': 5432
    }

    csv_file_path = f'/opt/airflow/dags/{table_name}.csv'

    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    with open(csv_file_path, 'r') as file:
        next(file)  # Skip the header row if it exists
        data = [tuple(None if cell == '' else cell for cell in line.strip().split(',')) for line in file]

    target_table = table_name
    insert_sql = f"INSERT INTO {target_table} VALUES %s"
    execute_values(cur, insert_sql, data, page_size=10000) 

    conn.commit()
    cur.close()
    conn.close()

    print(f"CSV data loaded into PostgreSQL table in {db_params['dbname']} database.")


with DAG(
    'move_thyroid_fround_training_data',
    start_date=datetime(2023, 3, 21),
    schedule_interval="@daily",
    catchup=False
) as dag:

    #task thyroid
    download_from_s3_task = PythonOperator(
        task_id = 'download_thyroid_data',
        python_callable = download_from_s3,
        op_kwargs={'filename': 'thyroidDF.csv'},
        dag=dag,
    )

    create_thyroid_table_task = PostgresOperator(
        task_id='create_thyroid_table',
        postgres_conn_id='aws_rds',
        sql = 'create_thyroid_table.sql',
        dag=dag,
    )

    upload_task = PythonOperator(
        task_id = 'upload_thyroid_data',
        python_callable = upload,
        op_kwargs={'table_name': 'thyroidDF'}, 
        dag=dag,
    )

    transform_thyroid_task = PostgresOperator(
        task_id='transform_thyroid',
        postgres_conn_id='aws_rds',
        sql = 'transform_thyroid.sql',
        dag=dag,
    )




    download_from_s3_bodyfat_task = PythonOperator(
        task_id = 'download_from_s3_bodyfat',
        python_callable = download_from_s3,
        op_kwargs={'filename': 'bodyfatDF.csv'},
        dag=dag,
    )

    create_bodyfat_table_task = PostgresOperator(
        task_id='create_bodyfat_table',
        postgres_conn_id='aws_rds',
        sql = 'create_bodyfat_table.sql',
        dag=dag,
    )

    upload_bodyfat_task = PythonOperator(
        task_id = 'upload_bodyfat_data',
        python_callable = upload,
        op_kwargs={'table_name': 'bodyfatDF'}, 
        dag=dag,
    )

    transform_bodyfat_task = PostgresOperator(
        task_id='transform_bodyfat',
        postgres_conn_id='aws_rds',
        sql = 'transform_bodyfat.sql',
        dag=dag,
    )





    download_from_s3_task >> create_thyroid_table_task >> upload_task >> transform_thyroid_task
    download_from_s3_bodyfat_task >> create_bodyfat_table_task >> upload_bodyfat_task >> transform_bodyfat_task
    #>> validateGX
