terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
}
provider "google" {
  project = var.project_id
  region  = var.region
}
provider "google-beta" {
  project = var.project_id
  region  = var.region
}
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com", "sqladmin.googleapis.com", "redis.googleapis.com",
    "storage.googleapis.com", "artifactregistry.googleapis.com", "cloudbuild.googleapis.com",
    "secretmanager.googleapis.com", "servicenetworking.googleapis.com", "compute.googleapis.com",
    "vpcaccess.googleapis.com", "aiplatform.googleapis.com"
  ])
  service            = each.key
  disable_on_destroy = false
}
resource "google_compute_global_address" "private_ip_alloc" {
  provider      = google-beta
  name          = "private-ip-alloc-for-services"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = "projects/${var.project_id}/global/networks/default"
}
resource "google_service_networking_connection" "default" {
  provider                = google-beta
  network                 = "projects/${var.project_id}/global/networks/default"
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_alloc.name]
  depends_on              = [google_project_service.apis["servicenetworking.googleapis.com"]]
}
resource "google_vpc_access_connector" "connector" {
  name          = "vpc-connector-pixsellai"
  region        = var.region
  ip_cidr_range = "10.8.0.0/28"
  network       = "default"
  depends_on    = [google_project_service.apis["vpcaccess.googleapis.com"]]
}
resource "google_sql_database_instance" "postgres" {
  name             = "pixsellai-db-instance"
  database_version = "POSTGRES_14"
  region           = var.region
  settings {
    tier = "db-g1-small"
    ip_configuration {
      ipv4_enabled    = false
      private_network = "projects/${var.project_id}/global/networks/default"
    }
  }
  depends_on = [google_service_networking_connection.default]
}
resource "google_sql_database" "database" {
  name     = "pixsellai_db"
  instance = google_sql_database_instance.postgres.name
}
resource "google_sql_user" "db_user" {
  name     = "pixsell_user"
  instance = google_sql_database_instance.postgres.name
  password = var.db_password
}
resource "google_redis_instance" "queue" {
  name               = "pixsellai-queue"
  tier               = "BASIC"
  memory_size_gb     = 1
  region             = var.region
  connect_mode       = "DIRECT_PEERING"
  authorized_network = "projects/${var.project_id}/global/networks/default"
  depends_on         = [google_service_networking_connection.default]
}
resource "google_storage_bucket" "images_bucket" {
  name                        = "${var.project_id}-pixsellai-images"
  location                    = var.region
  force_destroy               = true
  uniform_bucket_level_access = true
  depends_on                  = [google_project_service.apis["storage.googleapis.com"]]
}
resource "google_artifact_registry_repository" "repo" {
  location      = var.region
  repository_id = "pixsellai-repo"
  format        = "DOCKER"
  description   = "Docker repository for PixSellAI"
  depends_on    = [google_project_service.apis["artifactregistry.googleapis.com"]]
}
resource "google_vertex_ai_endpoint" "sd_endpoint" {
  provider     = google-beta
  name         = "stable-diffusion-endpoint"
  project      = var.project_id
  location     = var.region
  display_name = "Stable Diffusion Endpoint"
  labels = {
    "managed-by" = "terraform"
  }
  depends_on   = [google_project_service.apis["aiplatform.googleapis.com"]]
}
output "vertex_ai_endpoint_id" {
  description = "The numeric ID of the Vertex AI Endpoint"
  value       = regex("endpoints/([0-9]+)", google_vertex_ai_endpoint.sd_endpoint.name)[0]
}
