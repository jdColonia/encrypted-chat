variable "name" {
  description = "Nombre del resource group"
  type        = string
}

variable "location" {
  description = "Ubicación de Azure"
  type        = string
}

variable "tags" {
  description = "Tags para el resource group"
  type        = map(string)
  default     = {}
}
