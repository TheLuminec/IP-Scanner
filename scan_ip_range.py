import nmap

def ipString(ip):
    return '.'.join(map(str, ip))

def ipTraverse(ip, dist, min=0, max=255):
    l = len(ip) - 1
    ip[l] += dist

    while l > 0:
        if(ip[l] > max):
            ip[l-1] += ip[l] // (max+1)
            ip[l] = ip[l]%(max+1) + min
        l -= 1

    if(ip[0] > max):
        ip[0] = min

    return ip