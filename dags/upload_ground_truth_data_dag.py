import os
from airflow import DAG
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python_operator import PythonOperator

from datetime import datetime, timedelta
from airflow.hooks.S3_hook import S3Hook

from airflow.providers.amazon.aws.transfers.sql_to_s3 import SqlToS3Operator
from airflow.providers.amazon.aws.operators.s3 import S3CopyObjectOperator

from great_expectations_provider.operators.great_expectations import GreatExpectationsOperator

import psycopg2
from psycopg2.extras import execute_values

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def download_from_s3(filename, **kwargs):
    hook = S3Hook(aws_conn_id='AWS_CONN')
    downloaded_name = hook.download_file(bucket_name='medicalmlbucket', key=f'model/{filename}', local_path='/opt/airflow/dags/')
    dst = os.path.join('/opt/airflow/dags', filename)
    os.rename(src=downloaded_name, dst=dst)


def upload(table_name, filename=None):

    # there is no way to make a one default param equalts to another param, even if it is mandatory one
    # it is used for heardDF table, because it uses _temp table to load data from csv, not main one
    if filename is None:
        filename = table_name

    db_params = {
        'dbname': 'medicalmldb',
        'user': 'medicalmladmin',
        'password': 'Qwerty12345',
        'host': 'rdsterraform.cdwy46wiszkf.eu-north-1.rds.amazonaws.com',
        'port': 5432
    }

    csv_file_path = f'/opt/airflow/dags/{filename}.csv'

    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    with open(csv_file_path, 'r') as file:
        next(file)  # Skip the header row
        data = [tuple(None if cell == '' else cell for cell in line.strip().split(',')) for line in file]

    target_table = table_name
    insert_sql = f"INSERT INTO {target_table} VALUES %s"
    execute_values(cur, insert_sql, data, page_size=10000) 

    conn.commit()
    cur.close()
    conn.close()

    print(f"CSV data loaded into PostgreSQL table in {db_params['dbname']} database.")


with DAG(
    'move_ground_training_data',
    start_date=datetime(2023, 3, 21),
    schedule_interval="@once",
    catchup=False
) as dag:
    
    save_historical_data_of_thyroid_task = S3CopyObjectOperator(
        task_id = 'save_historical_data_of_thyroid',
        source_bucket_key='model/thyroidDF.csv',
        dest_bucket_key=f'thyroidDF_{str(datetime.now())}.csv',
        source_bucket_name='medicalmlbucket',
        dest_bucket_name='medicalmlbucket',
        aws_conn_id='AWS_CONN',
    )

    # move from sql to s3
    move_thyroid_data_from_sql_to_s3_task = SqlToS3Operator(
        task_id='move_thyroid_data_from_sql_to_s3',
        query="query_all_thyroid_tests_that_are_in_diagnoses.sql",
        sql_conn_id='aws_rds',
        aws_conn_id='AWS_CONN',
        s3_bucket='medicalmlbucket',
        s3_key='model/thyroidDF.csv',
        replace=True,
    )

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


    #bodyfat
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


    #blood
    download_from_s3_blood_task = PythonOperator(
        task_id = 'download_from_s3_blood',
        python_callable = download_from_s3,
        op_kwargs={'filename': 'bloodDF.csv'},
        dag=dag,
    )

    create_blood_table_task = PostgresOperator(
        task_id='create_blood_table',
        postgres_conn_id='aws_rds',
        sql = 'create_blood_table.sql',
        dag=dag,
    )

    upload_blood_task = PythonOperator(
        task_id = 'upload_blood_data',
        python_callable = upload,
        op_kwargs={'table_name': 'bloodDF'}, 
        dag=dag,
    )

    transform_blood_task = PostgresOperator(
        task_id='transform_blood',
        postgres_conn_id='aws_rds',
        sql = 'transform_blood.sql',
        dag=dag,
    )


    #derm
    download_from_s3_derm_task = PythonOperator(
        task_id = 'download_from_s3_derm',
        python_callable = download_from_s3,
        op_kwargs={'filename': 'dermDF.csv'},
        dag=dag,
    )

    create_derm_table_task = PostgresOperator(
        task_id='create_derm_table',
        postgres_conn_id='aws_rds',
        sql = 'create_derm_table.sql',
        dag=dag,
    )

    upload_derm_task = PythonOperator(
        task_id = 'upload_derm_data',
        python_callable = upload,
        op_kwargs={'table_name': 'dermDF'}, 
        dag=dag,
    )

    transform_derm_task = PostgresOperator(
        task_id='transform_derm',
        postgres_conn_id='aws_rds',
        sql = 'transform_derm.sql',
        dag=dag,
    )



    #heart
    download_from_s3_heart_task = PythonOperator(
        task_id = 'download_from_s3_heart',
        python_callable = download_from_s3,
        op_kwargs={'filename': 'heartDF.csv'},
        dag=dag,
    )

    create_heart_table_task = PostgresOperator(
        task_id='create_heart_table',
        postgres_conn_id='aws_rds',
        sql = 'create_heart_table.sql',
        dag=dag,
    )

    upload_heart_task = PythonOperator(
        task_id = 'upload_heart_data',
        python_callable = upload,
        op_kwargs={'table_name': 'heartDF_temp', 'filename': 'heartDF'}, 
        dag=dag,
    )

    transform_heart_task = PostgresOperator(
        task_id='transform_heart',
        postgres_conn_id='aws_rds',
        sql = 'transform_heart.sql',
        dag=dag,
    )
    
    ge_validate_train_blooddf = GreatExpectationsOperator(
        task_id='validate_bloodDF_table',
        data_context_root_dir="/opt/airflow/gx/",
        checkpoint_name = "train_blooddf_checkpoint",
        return_json_dict=True,
        fail_task_on_validation_failure=True
    )

    ge_validate_train_bodyfatdf = GreatExpectationsOperator(
        task_id='validate_bodyfatDF_table',
        data_context_root_dir="/opt/airflow/gx/",
        checkpoint_name = "train_bodyfatdf_checkpoint",
        return_json_dict=True,
        fail_task_on_validation_failure=True
    )

    ge_validate_train_dermdf = GreatExpectationsOperator(
        task_id='validate_dermdf_table',
        data_context_root_dir="/opt/airflow/gx/",
        checkpoint_name = "train_dermdf_checkpoint",
        return_json_dict=True,
        fail_task_on_validation_failure=True
    )

    ge_validate_train_heartdf = GreatExpectationsOperator(
        task_id='validate_heartdf_table',
        data_context_root_dir="/opt/airflow/gx/",
        checkpoint_name = "train_heartdf_checkpoint",
        return_json_dict=True,
        fail_task_on_validation_failure=True
    )

    ge_validate_train_thyroiddf = GreatExpectationsOperator(
        task_id='validate_thyroiddf_table',
        data_context_root_dir="/opt/airflow/gx/",
        checkpoint_name = "train_thyroiddf_checkpoint",
        return_json_dict=True,
        fail_task_on_validation_failure=True
    )

    save_historical_data_of_thyroid_task >> move_thyroid_data_from_sql_to_s3_task >> download_from_s3_task

    download_from_s3_task >> create_thyroid_table_task >> upload_task >> transform_thyroid_task >> ge_validate_train_thyroiddf
    download_from_s3_bodyfat_task >> create_bodyfat_table_task >> upload_bodyfat_task >> transform_bodyfat_task >> ge_validate_train_bodyfatdf
    download_from_s3_blood_task >> create_blood_table_task >> upload_blood_task >> transform_blood_task >> ge_validate_train_blooddf
    download_from_s3_derm_task >> create_derm_table_task >> upload_derm_task >> transform_derm_task >> ge_validate_train_dermdf
    download_from_s3_heart_task >> create_heart_table_task >> upload_heart_task >> transform_heart_task >> ge_validate_train_heartdf

