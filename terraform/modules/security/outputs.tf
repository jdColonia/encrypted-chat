output "nsg_id" {
  description = "ID del Network Security Group"
  value       = azurerm_network_security_group.nsg.id
}

output "nsg_name" {
  description = "Nombre del Network Security Group"
  value       = azurerm_network_security_group.nsg.name
}
