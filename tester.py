import asyncio
import time
import sys
from pythonping import ping

async def async_scan_ports(ip):
    open_ports = []

    response = ping(ip, count=3, timeout=2)
    print(f"Ping response: {response.rtt_max_ms} ms")

    timeout = response.rtt_max * 10

    async def check_port(port):
        try:
            # Attempt to open an async connection to the IP and port
            reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, port), timeout=timeout)
            open_ports.append(port)  # If successful, add the port to the list of open ports
            print(f"Port {port} is open.")
            writer.close()  # Close the writer (connection)
            await writer.wait_closed()  # Ensure the connection is properly closed
        except Exception:
            pass
            # Ignore exceptions, which indicates the port is closed or filtered
    if(timeout < 10):
        for pr in range (0, 65536, 2048):
            tasks = [check_port(port) for port in range(pr, pr+2048)]#65537)]  # Scan all 65,536 ports
            await asyncio.gather(*tasks)

    return open_ports

# Example usage
async def main():
    start_time = time.time()
    
    #ip = "127.0.0.1"
    ip = "8.8.8.8"
    if(sys.argv[1]):
        ip = sys.argv[1]

    print(f"Scanning IP: {ip}")
    open_ports = await async_scan_ports(ip)
    print(f"Open ports: {open_ports}")

    print(f"Scan took {time.time() - start_time} seconds")

# Run the scan
if __name__ == "__main__":
    asyncio.run(main())