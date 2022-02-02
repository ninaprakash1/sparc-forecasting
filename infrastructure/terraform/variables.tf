variable "billing_account_name" {
  default = "Griffin Tarpenning"
}

variable "user" {
  default = "gtarpenning@gmail.com"
}

locals {
  project_name = "cloud-runner"
  project      = "${local.project_name}-${random_id.id.hex}"
  region       = "us-west1"

  service_name  = "cloud-runner-service"
  input_bucket  = "cloud-runner-input-bucket"
  output_bucket = "cloud-runner-output-bucket"

  image_name = "gcr.io/${local.project}/cloud-runner"
  image_tag  = "latest"
  image_uri  = "${local.image_name}:${local.image_tag}"
}

resource "random_id" "id" {
  byte_length = 2
}
