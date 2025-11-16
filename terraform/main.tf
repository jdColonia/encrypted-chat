terraform {
  required_version = ">= 1.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

data "local_file" "ssh_public_key" {
  filename = pathexpand(var.ssh_public_key_path)
}

module "resource_group" {
  source = "./modules/resource_group"

  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

module "security" {
  source = "./modules/security"

  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  nsg_name            = "nsg-chat-encrypted"
  tags                = var.tags
}

module "network" {
  source = "./modules/network"

  resource_group_name   = module.resource_group.name
  location              = module.resource_group.location
  vnet_name             = "vnet-chat-encrypted"
  vnet_address_space    = ["10.0.0.0/16"]
  subnet_name           = "subnet-chat"
  subnet_address_prefix = "10.0.1.0/24"
  nsg_id                = module.security.nsg_id
  tags                  = var.tags
}

module "vm_server" {
  source = "./modules/vm"

  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  vm_name             = "vm-chat-server"
  vm_size             = var.vm_size
  subnet_id           = module.network.subnet_id
  admin_username      = var.admin_username
  ssh_public_key      = data.local_file.ssh_public_key.content
  create_public_ip    = true
  tags                = merge(var.tags, { Role = "Server" })
}

module "vm_client_1" {
  source = "./modules/vm"

  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  vm_name             = "vm-chat-client-1"
  vm_size             = var.vm_size
  subnet_id           = module.network.subnet_id
  admin_username      = var.admin_username
  ssh_public_key      = data.local_file.ssh_public_key.content
  create_public_ip    = true
  tags                = merge(var.tags, { Role = "Client" })
}

module "vm_client_2" {
  source = "./modules/vm"

  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  vm_name             = "vm-chat-client-2"
  vm_size             = var.vm_size
  subnet_id           = module.network.subnet_id
  admin_username      = var.admin_username
  ssh_public_key      = data.local_file.ssh_public_key.content
  create_public_ip    = true
  tags                = merge(var.tags, { Role = "Client" })
}

resource "local_file" "ansible_inventory" {
  filename = "${path.module}/../ansible/inventory/hosts.ini"
  content = templatefile("${path.module}/templates/inventory.tpl", {
    server_ip           = module.vm_server.public_ip_address
    server_private_ip   = module.vm_server.private_ip_address
    client_1_ip         = module.vm_client_1.public_ip_address
    client_1_private_ip = module.vm_client_1.private_ip_address
    client_2_ip         = module.vm_client_2.public_ip_address
    client_2_private_ip = module.vm_client_2.private_ip_address
    admin_username      = var.admin_username
  })

  depends_on = [
    module.vm_server,
    module.vm_client_1,
    module.vm_client_2
  ]
}
