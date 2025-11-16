output "resource_group_name" {
  description = "Nombre del resource group"
  value       = module.resource_group.name
}

output "vnet_name" {
  description = "Nombre de la red virtual"
  value       = module.network.vnet_name
}

output "server_public_ip" {
  description = "IP pública del servidor"
  value       = module.vm_server.public_ip_address
}

output "server_private_ip" {
  description = "IP privada del servidor"
  value       = module.vm_server.private_ip_address
}

output "client_1_public_ip" {
  description = "IP pública del cliente 1"
  value       = module.vm_client_1.public_ip_address
}

output "client_1_private_ip" {
  description = "IP privada del cliente 1"
  value       = module.vm_client_1.private_ip_address
}

output "client_2_public_ip" {
  description = "IP pública del cliente 2"
  value       = module.vm_client_2.public_ip_address
}

output "client_2_private_ip" {
  description = "IP privada del cliente 2"
  value       = module.vm_client_2.private_ip_address
}

output "ssh_commands" {
  description = "Comandos SSH"
  value = {
    server   = "ssh ${var.admin_username}@${module.vm_server.public_ip_address}"
    client_1 = "ssh ${var.admin_username}@${module.vm_client_1.public_ip_address}"
    client_2 = "ssh ${var.admin_username}@${module.vm_client_2.public_ip_address}"
  }
}
