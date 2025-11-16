output "name" {
  description = "Nombre del resource group"
  value       = azurerm_resource_group.rg.name
}

output "location" {
  description = "Ubicación del resource group"
  value       = azurerm_resource_group.rg.location
}

output "id" {
  description = "ID del resource group"
  value       = azurerm_resource_group.rg.id
}
