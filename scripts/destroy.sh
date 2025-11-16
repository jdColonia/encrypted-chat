#!/bin/bash

set -e

echo "=========================================="
echo "  Destruir Infraestructura en Azure"
echo "=========================================="
echo ""

RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd terraform

echo -e "${YELLOW}ADVERTENCIA: Esto eliminará TODOS los recursos en Azure${NC}"
echo -e "${YELLOW}¿Estás seguro? (escribe 'yes' para confirmar)${NC}"
read -r response

if [ "$response" != "yes" ]; then
    echo "Operación cancelada"
    exit 0
fi

terraform destroy -auto-approve

echo ""
echo -e "${RED}Infraestructura eliminada${NC}"

cd ../ansible
if [ -f "inventory/hosts.ini" ]; then
    rm -f inventory/hosts.ini
    echo "Inventario de Ansible limpiado"
fi
