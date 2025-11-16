[server]
vm-chat-server ansible_host=${server_ip} private_ip=${server_private_ip}

[clients]
vm-chat-client-1 ansible_host=${client_1_ip} private_ip=${client_1_private_ip} client_name=Client1
vm-chat-client-2 ansible_host=${client_2_ip} private_ip=${client_2_private_ip} client_name=Client2

[all:vars]
ansible_user=${admin_username}
ansible_python_interpreter=/usr/bin/python3
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
server_private_ip=${server_private_ip}
