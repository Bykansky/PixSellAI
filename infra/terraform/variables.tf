variable "project_id" {
  type        = string
  description = "The GCP project ID"
}

variable "region" {
  type        = string
  description = "The GCP region for resources"
  default     = "us-central1"
}

variable "db_password" {
  type        = string
  description = "The password for the PostgreSQL user"
  sensitive   = true # Помечаем как секрет
}
