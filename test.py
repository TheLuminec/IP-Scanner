import socket
import time
import concurrent.futures
import sqlite3
from pythonping import ping
import asyncio

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

# Function to check response time (synchronous)
def get_response_time(ip):
    try:
        response = ping(ip, count=1, timeout=2)
        if response.success():
            return response.rtt_avg_ms
    except:
        pass    
    return None

# Function to scan ports (synchronous)
def scan_ports(ip):
    open_ports = []
    ports = [22, 80, 443]  # Common ports to scan
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # Set a short timeout
        try:
            sock.connect((ip, port))
            open_ports.append(port)
        except socket.error:
            pass  # Ignore errors
        finally:
            sock.close()
    return open_ports

# Function to process each IP (synchronous)
def process_ip(ip):
    try:
        print(f"Processing IP: {ip}")
        response_time = get_response_time(ip)
        if response_time is not None:
            open_ports = scan_ports(ip)
        else:
            open_ports = [0]
        return (ip, response_time, open_ports)
    except Exception as e:
        print(f"Error processing IP: {ip}, {str(e)}")
        return (ip, None, [])

# Asynchronous version of get_response_time
async def async_get_response_time(ip):
    try:
        response = await asyncio.to_thread(ping, ip, count=1, timeout=2)
        if response.success():
            return response.rtt_avg_ms
        else:
            return None
    except Exception:
        return None

# Asynchronous version of scan_ports
async def async_scan_ports(ip):
    open_ports = []
    ports = [22, 80, 443]
    for port in ports:
        try:
            reader, writer = await asyncio.open_connection(ip, port)
            open_ports.append(port)
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass
    return open_ports

# Asynchronous version of process_ip
async def async_process_ip(ip):
    response_time = await async_get_response_time(ip)
    open_ports = await async_scan_ports(ip) if response_time is not None else []
    return (ip, response_time, open_ports)

# Function to save to the database
def save_to_db(conn, ip_data):
    c = conn.cursor()
    c.executemany("INSERT OR REPLACE INTO ip_info (ip, response_time, open_ports) VALUES (?, ?, ?)",
                  [(ip, response_time, ','.join(map(str, open_ports))) for ip, response_time, open_ports in ip_data])
    conn.commit()

# Batch processing of IPs (synchronous)
def process_ip_range(start_ip, end_ip, batch_size=10000):
    conn = create_database()
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        print('ok')
        for i in range(start_ip, end_ip, batch_size):
            batch = ['{}.{}.{}.{}'.format((i >> 24) & 0xFF, (i >> 16) & 0xFF, (i >> 8) & 0xFF, i & 0xFF) for i in range(i, min(i + batch_size, end_ip))]
            results = list(executor.map(process_ip, batch))
            save_to_db(conn, results)
    conn.close()

# Asynchronous batch processing of IPs
async def async_process_ip_range(start_ip, end_ip, batch_size=10000):
    conn = create_database()
    for i in range(start_ip, end_ip, batch_size):
        batch = ['{}.{}.{}.{}'.format((i >> 24) & 0xFF, (i >> 16) & 0xFF, (i >> 8) & 0xFF, i & 0xFF) for i in range(i, min(i + batch_size, end_ip))]
        tasks = [async_process_ip(ip) for ip in batch]
        results = await asyncio.gather(*tasks)
        save_to_db(conn, results)
    conn.close()

# Main function to choose synchronous or asynchronous processing
def main():
    start_ip = 1000000000
    end_ip = 1000000100  # Example range, adjust as needed
    
    # Choose whether to run the synchronous or asynchronous version
    use_async = False  # Set to True to use async processing
    
    if use_async:
        asyncio.run(async_process_ip_range(start_ip, end_ip))
    else:
        process_ip_range(start_ip, end_ip)

if __name__ == "__main__":
    main()
