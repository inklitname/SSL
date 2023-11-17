import socket
import ssl
import sqlite3


def get_ssl_version(host, port):
    """Функция для получения версии SSL"""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port)) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                return ssock.version()
    except Exception as e:
        return str(e)


def get_ssl_domains(host, port):
    """Функция для получения доменов из SSL сертификата"""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port)) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                if 'subjectAltName' in cert:
                    return [name[1] for name in cert['subjectAltName'] if name[0].lower() == 'dns']
                else:
                    return []
    except Exception as e:
        return str(e)


def write_to_database(data):
    """Функция для записи результатов в базу данных"""
    conn = sqlite3.connect('ssl_info.db')
    cursor = conn.cursor()

    # Создаем таблицу, если ее нет
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ssl_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            host TEXT,
            port INTEGER,
            ssl_version TEXT,
            domains TEXT
        )
    ''')

    # Вставляем данные в таблицу
    cursor.executemany('''
        INSERT INTO ssl_info (host, port, ssl_version, domains) VALUES (?, ?, ?, ?)
    ''', data)

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()


def get_hosts():
    """Чтение списка хостов и портов из файла"""
    with open('hosts.txt', 'r') as file:
        hosts = [line.strip().split(':') for line in file]
    return hosts


def init_ssl():
    """Формирование данных"""
    result_data=[]
    for host, port in get_hosts():
        ssl_version = get_ssl_version(host, int(port))
        ssl_domains = get_ssl_domains(host, int(port))
        result_data.append((host, int(port), ssl_version, ', '.join(ssl_domains)))
    return result_data


if __name__ == "__main__":
    result_data = init_ssl()
    write_to_database(result_data)
