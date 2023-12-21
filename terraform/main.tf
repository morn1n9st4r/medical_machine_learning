provider "aws" {
    region = "eu-north-1"
    access_key = ""
    secret_key = ""
}

resource "aws_db_instance" "rds_instance" {
    allocated_storage = 20
    identifier = var.rds_identifier
    storage_type = var.rds_storage_type
    engine = var.rds_engine
    engine_version = var.rds_engine_version
    instance_class = var.rds_instance_class
    name = var.rds_name
    username = var.rds_username
    password = var.rds_password

    publicly_accessible    = true
    skip_final_snapshot    = true


    tags = {
        Name = "MedicalMLProject"
    }
}


resource "aws_s3_bucket" "medicalmlbucket" {

    bucket = var.bucket_name

}