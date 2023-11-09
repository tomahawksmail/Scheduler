import psutil


def list_eth_connections():
    interfaces = psutil.net_if_stats()

    eth_connections = [interface for interface, stats in interfaces.items() if 'Ethernet' in interface]

    return eth_connections


eth_connections = list_eth_connections()
print("Ethernet Connections:", eth_connections)