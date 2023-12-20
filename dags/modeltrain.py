from datetime import datetime, timedelta
import os
import pickle
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator


from airflow.providers.amazon.aws.operators.s3 import S3CreateObjectOperator
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator

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

def fetch_data(**kwargs):
    print("Fetching data")

    thyroidDF = pd.read_csv('/opt/airflow/dags/data/thyroidDF.csv')
    
    thyroidDF.to_csv("thyroidDF", index=False)

def preprocess_data(**kwargs):
    print("Preprocessing data")

    thyroidDF = pd.read_csv("thyroidDF")

    # dropping redundant attributes from thyroidDF dataset
    thyroidDF.drop(['TSH_measured', 'T3_measured', 'TT4_measured', 'T4U_measured', 'FTI_measured', 'TBG_measured', 'patient_id', 'referral_source'], axis=1, inplace=True)

    # re-mapping target vaues to diagnostic groups
    diagnoses = {'-': 'negative',
                'A': 'hyperthyroid', 
                'B': 'hyperthyroid', 
                'C': 'hyperthyroid', 
                'D': 'hyperthyroid',
                'E': 'hypothyroid', 
                'F': 'hypothyroid', 
                'G': 'hypothyroid', 
                'H': 'hypothyroid'}

    thyroidDF['target'] = thyroidDF['target'].map(diagnoses) # re-mapping

    # dropping observations with 'target' null after re-mapping
    thyroidDF.dropna(subset=['target'], inplace=True) 

    # dataset initial summary
    thyroidDF.info()
    # changing age of observations with ('age' > 100) to null
    thyroidDF['age'] = np.where((thyroidDF.age > 100), np.nan, thyroidDF.age)

    missingness = thyroidDF.isnull().sum().sum() / thyroidDF.count().sum()
    print('Overall Missingness of thyroidDF is: {:.2f}%'.format(missingness * 100))

    # Create table for missing data analysis
    def missing_table(df):
        total = df.isnull().sum().sort_values(ascending=False)
        percent = (df.isnull().sum()/df.isnull().count()).sort_values(ascending=False)
        missing_data = pd.concat([total, percent], axis=1, keys=['Total', 'Percent'])
        return missing_data

    # Analyze missing data
    missing_table(thyroidDF).head(10)

    thyroidDF.drop(['TBG'], axis=1, inplace=True)
    thyroidDF.dropna(subset=['age'], inplace=True)
    thyroidDF['sex'] = np.where((thyroidDF.sex.isnull()) & (thyroidDF.pregnant == 't'), 'F', thyroidDF.sex)


    missingness = thyroidDF.isnull().sum().sum() / thyroidDF.count().sum()
    thyroidDF['n_missing'] = thyroidDF.isnull().sum(axis=1)
    thyroidDF.drop(thyroidDF.index[thyroidDF['n_missing'] > 2], inplace=True)


    thyroidDF = thyroidDF[['T3', 'TSH','FTI','T4U','TT4','goitre', 'target', 'sex', 'age']]

    thyroidDF.to_csv("thyroidDF", index=False)





def train_model(**kwargs):
    print("Training model")


    thyroidDF = pd.read_csv("thyroidDF")

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
                                early_stopping_rounds=10, 
                                eval_metric=['merror','mlogloss'], 
                                seed=42)
    xgb_clf.fit(X_train, 
                y_train,
                verbose=0,
                eval_set=[(X_train, y_train), (X_test, y_test)])


    X_test.to_csv("X_test", index=False)
    y_test.to_csv("y_test", index=False)

    with open('xgb_thyroid.pkl', 'wb') as file:
        pickle.dump(xgb_clf, file)


def validate_model(**kwargs):
    print("Validating model")
    
    X_test = pd.read_csv("X_test")
    y_test = pd.read_csv("y_test")

    with open("/opt/airflow/xgb_thyroid.pkl", 'rb') as file:
        
        xgb_clf = pickle.load(file)

        y_pred = xgb_clf.predict(X_test)
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



def upload_to_s3(**kwargs):
    print("Uploading to S3")





with DAG(
    'train_model',
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

    upload_task = upload_task = LocalFilesystemToS3Operator(
    task_id='upload_to_s3',
    aws_conn_id='AWS_CONN',
    filename='/opt/airflow/xgb_thyroid.pkl',
    dest_bucket='medicalmlbucket',
    dest_key='model/xgb_thyroid.pkl',
    dag=dag,
)

    fetch_task >> preprocess_task >> train_task >> validate_task >> upload_task