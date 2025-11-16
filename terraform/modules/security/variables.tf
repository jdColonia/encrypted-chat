variable "resource_group_name" {
  description = "Nombre del resource group"
  type        = string
}

variable "location" {
  description = "Ubicación de Azure"
  type        = string
}

variable "nsg_name" {
  description = "Nombre del Network Security Group"
  type        = string
}

variable "tags" {
  description = "Tags para los recursos"
  type        = map(string)
  default     = {}
}
