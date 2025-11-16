variable "subscription_id" {
  description = "ID de la suscripción de Azure"
  type        = string
}

variable "resource_group_name" {
  description = "Nombre del resource group"
  type        = string
  default     = "rg-chat-encrypted"
}

variable "location" {
  description = "Ubicación de Azure"
  type        = string
  default     = "East US"
}

variable "ssh_public_key_path" {
  description = "Ruta a la clave pública SSH"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

variable "admin_username" {
  description = "Usuario administrador para las VMs"
  type        = string
  default     = "azureuser"
}

variable "vm_size" {
  description = "Tamaño de las VMs"
  type        = string
  default     = "Standard_B1s"
}

variable "tags" {
  description = "Tags para todos los recursos"
  type        = map(string)
  default = {
    Environment = "Demo"
    Project     = "ChatEncrypted"
    ManagedBy   = "Terraform"
  }
}
