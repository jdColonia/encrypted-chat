#!/bin/bash

set -e

echo "=========================================="
echo "  Despliegue de Chat Cifrado en Azure"
echo "=========================================="
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if ! command -v az &> /dev/null; then
    echo -e "${RED}Error: Azure CLI no instalado${NC}"
    exit 1
fi

if ! command -v terraform &> /dev/null; then
    echo -e "${RED}Error: Terraform no instalado${NC}"
    exit 1
fi

if ! command -v ansible-playbook &> /dev/null; then
    echo -e "${RED}Error: Ansible no instalado${NC}"
    exit 1
fi

SSH_KEY="${HOME}/.ssh/id_rsa.pub"
if [ ! -f "$SSH_KEY" ]; then
    echo -e "${YELLOW}Generando clave SSH...${NC}"
    ssh-keygen -t rsa -b 4096 -f "${HOME}/.ssh/id_rsa" -N ""
    echo -e "${GREEN}Clave SSH generada${NC}"
fi

echo -e "${YELLOW}Verificando login en Azure...${NC}"
if ! az account show &> /dev/null; then
    az login
fi

SUBSCRIPTION=$(az account show --query name -o tsv)
echo -e "${GREEN}Conectado a: $SUBSCRIPTION${NC}"
echo ""

echo -e "${YELLOW}Desplegando infraestructura con Terraform...${NC}"
cd terraform

terraform init
terraform plan -out=tfplan

echo ""
echo -e "${YELLOW}¿Continuar con el despliegue? (s/n)${NC}"
read -r response
if [[ ! "$response" =~ ^[Ss]$ ]]; then
    echo "Despliegue cancelado"
    exit 0
fi

terraform apply tfplan

echo -e "${GREEN}Infraestructura desplegada${NC}"
echo ""

SERVER_IP=$(terraform output -raw server_public_ip)
CLIENT_1_IP=$(terraform output -raw client_1_public_ip)
CLIENT_2_IP=$(terraform output -raw client_2_public_ip)

echo "Esperando 30 segundos para que las VMs inicien..."
sleep 30

echo -e "${YELLOW}Aprovisionando VMs con Ansible...${NC}"

echo "Verificando conectividad SSH..."
for ip in $SERVER_IP $CLIENT_1_IP $CLIENT_2_IP; do
    echo "Esperando SSH en $ip..."
    timeout 120 bash -c "until nc -z $ip 22; do sleep 2; done" || {
        echo -e "${RED}Timeout esperando SSH en $ip${NC}"
        exit 1
    }
done

echo -e "${GREEN}SSH disponible en todas las VMs${NC}"
sleep 5

cd ..
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i ansible/inventory/hosts.ini ansible/playbook.yml

echo ""
echo -e "${GREEN}==========================================${NC}"
echo "  Despliegue completado exitosamente"
echo -e "${GREEN}==========================================${NC}"
echo ""
echo "Conexiones SSH:"
echo "  Servidor:   ssh azureuser@$SERVER_IP"
echo "  Cliente 1:  ssh azureuser@$CLIENT_1_IP"
echo "  Cliente 2:  ssh azureuser@$CLIENT_2_IP"
echo ""
echo "El servidor ya está corriendo."
echo ""
echo "Para iniciar chat en clientes:"
echo "  ssh azureuser@<client_ip>"
echo "  cd chat && ./run-client.sh"
