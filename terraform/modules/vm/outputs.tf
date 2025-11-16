output "vm_id" {
  description = "ID de la VM"
  value       = azurerm_linux_virtual_machine.vm.id
}

output "vm_name" {
  description = "Nombre de la VM"
  value       = azurerm_linux_virtual_machine.vm.name
}

output "private_ip_address" {
  description = "Dirección IP privada"
  value       = azurerm_network_interface.nic.private_ip_address
}

output "public_ip_address" {
  description = "Dirección IP pública"
  value       = var.create_public_ip ? azurerm_public_ip.public_ip[0].ip_address : null
}

output "admin_username" {
  description = "Usuario administrador"
  value       = var.admin_username
}
