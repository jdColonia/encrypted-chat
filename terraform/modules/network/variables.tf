variable "resource_group_name" {
  description = "Nombre del resource group"
  type        = string
}

variable "location" {
  description = "Ubicación de Azure"
  type        = string
}

variable "vnet_name" {
  description = "Nombre de la red virtual"
  type        = string
}

variable "vnet_address_space" {
  description = "Espacio de direcciones de la VNet"
  type        = list(string)
}

variable "subnet_name" {
  description = "Nombre de la subnet"
  type        = string
}

variable "subnet_address_prefix" {
  description = "Prefijo de dirección de la subnet"
  type        = string
}

variable "nsg_id" {
  description = "ID del Network Security Group"
  type        = string
}

variable "tags" {
  description = "Tags para los recursos"
  type        = map(string)
  default     = {}
}
