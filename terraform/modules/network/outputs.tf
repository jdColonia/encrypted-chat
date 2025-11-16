output "vnet_id" {
  description = "ID de la red virtual"
  value       = azurerm_virtual_network.vnet.id
}

output "vnet_name" {
  description = "Nombre de la red virtual"
  value       = azurerm_virtual_network.vnet.name
}

output "subnet_id" {
  description = "ID de la subnet"
  value       = azurerm_subnet.subnet.id
}
