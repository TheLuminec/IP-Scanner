from pythonping import ping
import socket
import asyncio

ip = '108.174.10.10'

response = ping(ip, count=1, timeout=2)
print(response)

open_ports = []

t = (response.rtt_avg_ms / 1000) * 2

async def async_scan_ports(ip, timeout):
    open_ports = []
    async def check_port(port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((ip, port))
            open_ports.append(port)
            print(f"Port {port} is open.")
        except Exception:
            print(f"Port {port} is closed.")
            pass  # Ignore exceptions

    tasks = [check_port(port) for port in range(0, 1000)]  # Scan all 65,536 ports
    await asyncio.gather(*tasks)
    return open_ports

open_ports = asyncio.run(async_scan_ports(ip, t))
open_ports = asyncio.run(async_scan_ports('127.0.0.1', t))
        
print(f'Open ports for {ip}: {open_ports}')