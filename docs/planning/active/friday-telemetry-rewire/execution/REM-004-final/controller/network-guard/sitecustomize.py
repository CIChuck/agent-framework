"""Prevent non-loopback network effects in isolated deterministic checks."""
import ipaddress
import sys


def is_loopback(host):
    if isinstance(host, bytes):
        host = host.decode('ascii', 'strict')
    if host in (None, 'localhost'):
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def guard(event, arguments):
    if event == 'socket.getaddrinfo' and not is_loopback(arguments[0]):
        raise RuntimeError('Non-loopback DNS prohibited by deterministic check profile')
    if event in ('socket.connect', 'socket.sendto'):
        address = arguments[1] if event == 'socket.connect' else arguments[-1]
        if isinstance(address, tuple) and not is_loopback(address[0]):
            raise RuntimeError('Non-loopback transport prohibited by deterministic check profile')


sys.addaudithook(guard)
