#!/usr/bin/env python3
import socket

def test_port(host, port, timeout=3):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

host = "smtp.163.com"
ports = [465, 587, 25]

print(f"Testing connectivity to {host}...")
for port in ports:
    if test_port(host, port):
        print(f"  Port {port}: ✅ OPEN")
    else:
        print(f"  Port {port}: ❌ CLOSED/TIMEOUT")