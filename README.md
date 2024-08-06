# wireguard

------------------------------
# Установка
mkdir /etc/create_wireguard
cd /etc/create_wireguard
git clone https://github.com/neo6erd1n/wireguard.git
cd /etc/create_wireguard/wireguard/src
------------------------------
Добавление пользователя
python3 wireguard_manager.py add --user <имя_пользователя> --ip <разрешенный_IP>

Удаление пользователя
python3 wireguard_manager.py remove --user <имя_пользователя>

Просмотр списка пользователей
python3 wireguard_manager.py list

Удаление WireGuard
python3 wireguard_manager.py uninstall
