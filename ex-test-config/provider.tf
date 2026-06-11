terraform {
  required_providers {
    alteon = {
      source = "Radware/alteon"
    }
    vault = {
      source = "hashicorp/vault"
    }    
  }
}

provider "alteon" {
  username="admin"
  password="admin"
  ip="10.2.0.213" 
}

