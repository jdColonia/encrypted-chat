variable "resource_group_name" {
  description = "Nombre del resource group"
  type        = string
}

variable "location" {
  description = "Ubicación de Azure"
  type        = string
}

variable "vm_name" {
  description = "Nombre de la VM"
  type        = string
}

variable "vm_size" {
  description = "Tamaño de la VM"
  type        = string
  default     = "Standard_B1s"
}

variable "subnet_id" {
  description = "ID de la subnet"
  type        = string
}

variable "admin_username" {
  description = "Usuario administrador"
  type        = string
  default     = "azureuser"
}

variable "ssh_public_key" {
  description = "Clave pública SSH"
  type        = string
}

variable "create_public_ip" {
  description = "Crear IP pública"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags para los recursos"
  type        = map(string)
  default     = {}
}
