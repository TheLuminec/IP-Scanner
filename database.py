import socket
import time
import concurrent.futures
import sqlite3
from pythonping import ping

# SQLite connection
def create_database():
    conn = sqlite3.connect('ip_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS ip_info (
                    ip TEXT PRIMARY KEY,
                    response_time REAL,
                    open_ports TEXT
                )''')
    conn.commit()
    return conn

# Function to check response time
def get_response_time(ip):
    try:
        response = ping(ip, count=1, timeout=2)
        if response.success():
            return response.rtt_avg_ms
        else:
            return None
    except Exception as e:
        return None

# Function to scan ports (simple example scanning a few ports)
def scan_ports(ip):
    open_ports = []
    ports = [22, 80, 443]  # Common ports to scan
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        try:
            sock.connect((ip, port))
            open_ports.append(port)
        except socket.error:
            pass
        finally:
            sock.close()
    return open_ports

# Function to process each IP
def process_ip(ip):
    response_time = get_response_time(ip)
    open_ports = scan_ports(ip) if response_time is not None else []
    return (ip, response_time, open_ports)

# Function to save to the database
def save_to_db(conn, ip_data):
    c = conn.cursor()
    c.executemany("INSERT OR REPLACE INTO ip_info (ip, response_time, open_ports) VALUES (?, ?, ?)",
                  [(ip, response_time, ','.join(map(str, open_ports))) for ip, response_time, open_ports in ip_data])
    conn.commit()

# Batch processing of IPs
def process_ip_range(start_ip, end_ip, batch_size=10000):
    conn = create_database()
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        for i in range(start_ip, end_ip, batch_size):
            batch = ['{}.{}.{}.{}'.format((i >> 24) & 0xFF, (i >> 16) & 0xFF, (i >> 8) & 0xFF, i & 0xFF) for i in range(i, min(i + batch_size, end_ip))]
            results = list(executor.map(process_ip, batch))
            save_to_db(conn, results)
    conn.close()

# Example of processing 1 million IPs (from 0.0.0.0 to 0.15.255.255)
process_ip_range(0, 1000000)
