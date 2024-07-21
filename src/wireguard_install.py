import subprocess
import os
import qrcode

WG_DIR = "/etc/wireguard"
WG_CONFIG = f"{WG_DIR}/wg0.conf"
USER_DIR = f"{WG_DIR}/users"
SERVER_PRIVATE_KEY = f"{WG_DIR}/server_privatekey"
SERVER_PUBLIC_KEY = f"{WG_DIR}/server_publickey"


def run_command(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise Exception(f"Ошибка выполнения команды: {command}\n{result.stderr.decode()}")
    return result.stdout.decode()


def generate_keys(user):
    private_key = run_command(f"wg genkey | tee {USER_DIR}/{user}_privatekey").strip()
    public_key = run_command(f"cat {USER_DIR}/{user}_privatekey | wg pubkey | tee {USER_DIR}/{user}_publickey").strip()
    return private_key, public_key


def generate_server_keys():
    if not os.path.exists(SERVER_PRIVATE_KEY) or not os.path.exists(SERVER_PUBLIC_KEY):
        print("Серверные ключи не найдены, создаем новые...")
        private_key = run_command(f"wg genkey | tee {SERVER_PRIVATE_KEY}").strip()
        public_key = run_command(f"cat {SERVER_PRIVATE_KEY} | wg pubkey | tee {SERVER_PUBLIC_KEY}").strip()
        print(f"Серверные ключи созданы:\nPrivateKey: {private_key}\nPublicKey: {public_key}")
    else:
        print("Серверные ключи уже существуют.")


def get_external_ip():
    try:
        ip = run_command("curl -s ifconfig.me").strip()
        if not ip:
            raise Exception("Не удалось получить внешний IP-адрес")
        return ip
    except Exception as e:
        raise Exception(f"Ошибка получения внешнего IP-адреса: {str(e)}")


def add_user(user, allowed_ip):
    generate_server_keys()
    private_key, public_key = generate_keys(user)
    with open(WG_CONFIG, 'a') as config:
        config.write(f"\n[Peer]\nPublicKey = {public_key}\nAllowedIPs = {allowed_ip}\n")

    external_ip = get_external_ip()
    client_config = f"""
    [Interface]
    PrivateKey = {private_key}
    Address = {allowed_ip}
    DNS = 8.8.8.8

    [Peer]
    PublicKey = {run_command(f'cat {SERVER_PUBLIC_KEY}').strip()}
    Endpoint = {external_ip}:51820
    AllowedIPs = 0.0.0.0/0
    PersistentKeepalive = 20
    """
    with open(f"{USER_DIR}/{user}.conf", 'w') as f:
        f.write(client_config)

    img = qrcode.make(client_config)
    img.save(f"{USER_DIR}/{user}.png")
    print(f"Пользователь {user} добавлен. QR код сохранен в {USER_DIR}/{user}.png")
    run_command("systemctl restart wg-quick@wg0")


def remove_user(user):
    run_command(f"sed -i '/# {user} start/,/# {user} end/d' {WG_CONFIG}")
    run_command("systemctl restart wg-quick@wg0")
    os.remove(f"{USER_DIR}/{user}_privatekey")
    os.remove(f"{USER_DIR}/{user}_publickey")
    os.remove(f"{USER_DIR}/{user}.conf")
    os.remove(f"{USER_DIR}/{user}.png")
    print(f"Пользователь {user} удален")


def list_users():
    with open(WG_CONFIG, 'r') as f:
        lines = f.readlines()
    for line in lines:
        if line.strip().startswith("[Peer]"):
            print(line.strip())


def remove_wireguard():
    run_command("systemctl stop wg-quick@wg0")
    run_command("systemctl disable wg-quick@wg0")
    run_command("apt-get remove --purge -y wireguard")
    os.remove(WG_CONFIG)
    os.rmdir(WG_DIR)
    print("WireGuard удален с сервера")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Скрипт для управления WireGuard")
    parser.add_argument('action', choices=['add', 'remove', 'list', 'uninstall'], help="Действие для выполнения")
    parser.add_argument('--user', help="Имя пользователя для действия")
    parser.add_argument('--ip', help="Разрешенный IP-адрес для пользователя")

    args = parser.parse_args()
    if args.action == 'add':
        if not args.user or not args.ip:
            print("Для добавления пользователя необходимо указать имя и IP-адрес")
        else:
            add_user(args.user, args.ip)
    elif args.action == 'remove':
        if not args.user:
            print("Для удаления пользователя необходимо указать имя")
        else:
            remove_user(args.user)
    elif args.action == 'list':
        list_users()
    elif args.action == 'uninstall':
        remove_wireguard()
