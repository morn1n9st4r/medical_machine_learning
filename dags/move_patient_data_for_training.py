

"""
import datetime
from airflow import DAG
import pandas as pd
import psycopg2

def train_model(**kwargs):
    print("Training model")

    conn = psycopg2.connect(
        dbname='medicalmldb',
        user='medicalmladmin',
        password='Qwerty12345',
        host='rdsterraform.cdwy46wiszkf.eu-north-1.rds.amazonaws.com',
        port='5432'
    )

    base_record = pd.read_sql_query('select * from main_patientthyroidtest',con=conn)
    thyroidDF = pd.read_sql_query('select * from main_patientthyroidtest',con=conn)


with DAG(
    'move true patient data for training',
    start_date=datetime(2023, 3, 21),
    schedule_interval="@weekly",
    catchup=False
) as dag:
    pass
# query sick data
# query healthy data same size
# transform???
# load to staging



# db -> s3
"""

