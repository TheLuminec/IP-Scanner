import nmap
import random

def addToFile(ip, open_ports):
    with open('ips.txt', 'a') as file:
        file.write(f'{ip} - [{", ".join(map(str, open_ports))}]\n')

def scan_network(ip):
    nm = nmap.PortScanner()
    
    nm.scan(ip, '80,443')
    
    if ip in nm.all_hosts():
        print(f'Scan result for {ip}:')
        
        open_ports = []
        if nm[ip].has_tcp(80) and nm[ip]['tcp'][80]['state'] == 'open':
            print('80: open')
            open_ports.append(80)
        
        if nm[ip].has_tcp(443) and nm[ip]['tcp'][443]['state'] == 'open':
            print('443: open')
            open_ports.append(443)
        
        if open_ports:
            addToFile(ip, open_ports)


while True:
    r1 = random.randint(0, 255)
    r2 = random.randint(0, 255)
    r3 = random.randint(0, 255)
    r4 = random.randint(0, 255)

    ip = f'{r1}.{r2}.{r3}.{r4}'
    
    scan_network(ip)