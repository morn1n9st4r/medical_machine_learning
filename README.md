# MedicalML

## Description
MedicalML is a web-based application that leverages machine learning for medical predictions. It provides a comprehensive platform for doctors and patients to manage medical records and gain insights from predictive models. The application is designed to predict various medical conditions including cardiological disorders, dermatological conditions, thyroid disorders, liver diseases, and body fat percentage.

## Technologies used
- **Python**: The primary programming language used for backend development and machine learning models.
- **SQL**: Used for data transformations and preprocessing.
- **Django**: The web framework used for building the web interface.
- **Docker**: Used for containerizing the application for easy deployment.
- **Airflow**: Used for managing and scheduling data pipelines.
- **Terraform**: Infrastructure as Code (IaC) tool for managing cloud resources.
- **AWS S3**: Used for storing patient records for training and already trained ML models.
- **AWS RDS**: Used for database services.
- **Great Expectations**: Used for testing and validating the data.

## Features
- Patient and doctor record management via web interface.
- Predictive models for various medical conditions like general cardiological disorder, psoriasis, seborrheic dermatitis, lichen planus, pityriasis rosea, chronic dermatitis, pityriasis trichosanthes, hypothyroid, hyperthyroid, hepatitis, fibrosis, cirrhosis and predicting body fat percentage based on circumference of body parts.

## Data validation
Before using data in training we must validate that preprocessing is correct and nothing left behind. Great expections is used to check whether correct types are used, no missing or incorrect (in case of finite number of variants) values and overall tables structure. This is crucial part of training pipeline and tests are done automatically inside of Airflow DAG. These checks are applied for each machine learning model that are being used and trained. 

## Installation and usage
To install and run this project, follow these steps:

1. Clone the repository to your local machine.
2. Build the airflow image with
```
docker build -f Dockerfile.airflow . -t airflow-ml 
```
3. Place your AWS RDS credentials into settings.py file.
4. Migrate database with
```
python3 manage.py makemigrations
python3 manage.py migrate
```
5. Run Apache Airflow with 
```
docker compose up
```
6. Start Django with 
```
python3 manage.py runserver
```

## Future work
- Improve the accuracy of the machine learning models.
- Add more predictive models for other medical conditions.
- Enhance the user interface for better user experience.
- Implement usage of SCD for retaining of past user data.

## Contact
For any queries or suggestions, please feel free to reach out to us at `a.lepilo.soft@gmail.com`.
