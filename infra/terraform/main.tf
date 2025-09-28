terraform {
  required_providers {
    google = { source = "hashicorp/google" }
  }
}
provider "google" {
  project = var.project_id
  region  = var.region
}
resource "google_storage_bucket" "pixsell_bucket" {
  name     = "pixsell-artifacts-${var.project_id}"
  location = var.region
  force_destroy = true
}
variable "project_id" {}
variable "region" { default = "us-central1" }
