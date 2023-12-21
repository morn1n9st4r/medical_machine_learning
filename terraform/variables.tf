variable "rds_identifier" {
  type    = string
  default = "rdsterraform"
}

variable "rds_storage_type" {
  type    = string
  default = "gp2"
}

variable "rds_engine" {
  type    = string
  default = "postgres"
}

variable "rds_engine_version" {
  type    = string
  default = "14.7"
}

variable "rds_instance_class" {
  type    = string
  default = "db.t3.micro"
}

variable "rds_name" {
  type    = string
  default = "medicalmldb"
}

variable "rds_username" {
  type    = string
  default = "medicalmladmin"
}

variable "rds_password" {
  type    = string
  default = "Qwerty12345"
}

variable "bucket_name" {
  type    = string
  default = "medicalmlbucket"
}

variable "acl_value" {
  type    = string
  default = "public-read-write"
}