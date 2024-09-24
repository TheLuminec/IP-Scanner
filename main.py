import asyncio
import time
import sqlite3
import random
from pythonping import ping

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

def save_to_db(conn, ip_data):
    c = conn.cursor()
    c.executemany("INSERT OR REPLACE INTO ip_info (ip, response_time, open_ports) VALUES (?, ?, ?)",
                  [(ip_data[0], ip_data[1], ','.join(map(str, ip_data[2])))])
    conn.commit()


async def async_scan_ports(ip):
    open_ports = []

    tmax = 0.5
    try:
        response = ping(ip, count=2, timeout=tmax)
    except:
        return (ip, -2, [])
    print(ip)
    #print(f"Ping response: {response.rtt_max_ms} ms")

    timeout = response.rtt_max * 10
    async def check_port(port):
        try:
            await asyncio.wait_for(asyncio.open_connection(ip, port), timeout=timeout)
            open_ports.append(port)
            #print(f"Port {port} is open.")

        except:
            #print(f"Port {port} is closed.")
            pass

    if(response.rtt_avg < tmax):
        for pr in range (0, 65536, 2048):
            tasks = [check_port(port) for port in range(pr, pr+2048)]#65537)]  # Scan all 65,536 ports
            await asyncio.gather(*tasks)
    else:
        return (ip, -1, [])
    return (ip, response.rtt_avg_ms, open_ports)

async def scan_ip_batch(batch):
    tasks = [async_scan_ports(ip) for ip in batch]
    results = await asyncio.gather(*tasks)
    return results

def scan_ip_range(start_ip, end_ip, batch_size=512):
    conn = create_database()
    for i in range(start_ip, end_ip, batch_size):
        batch = ['{}.{}.{}.{}'.format((i >> 24) & 0xFF, (i >> 16) & 0xFF, (i >> 8) & 0xFF, i & 0xFF) for i in range(i, min(i + batch_size, end_ip))]
        results = asyncio.run(scan_ip_batch(batch))
        print(f"Batch {batch[0]} - {batch[len(batch)-1]} has completed.")
        for ip_data in results:
            save_to_db(conn, ip_data)
    conn.close()

def get_random_ip(start_ip=[0,0,0,0], end_ip=[255,255,255,255]):
    i = random.randint(0, 4294967295)
    ip = '{}.{}.{}.{}'.format((i >> 24) & 0xFF, (i >> 16) & 0xFF, (i >> 8) & 0xFF, i & 0xFF)
    return ip


def scan_random_ips(amount=-1, batch_size=512):
    conn = create_database()
    for i  in range (0, amount, batch_size):
        batch = [get_random_ip() for i in range(batch_size)]
        results = asyncio.run(scan_ip_batch(batch))
        print(f"Batch has completed.")
        for ip_data in results:
            save_to_db(conn, ip_data)
    conn.close()

# Example usage
def main():
    start_time = time.time()

    start_ip = int.from_bytes([71,58,3,0], 'big')
    end_ip = int.from_bytes([71,58,9,0], 'big') + 1

    #scan_ip_range(start_ip, end_ip, batch_size=128)
    scan_random_ips(amount=4096)

    print(f"Scan took {time.time() - start_time} seconds")

# Run the scan
if __name__ == "__main__":
    main()