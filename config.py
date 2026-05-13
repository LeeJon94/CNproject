# JO ALMERO / 24849627
# THIS FILE CONTAINS ALL THE CONSTANTS AND DATA FOR THE NETWORK (1P ADDRESSES, MAC ADDRESSES, ROUTING TABLES).

HOST_A_MAC = "AA:AA:AA:AA:AA:AA"

HOST_A_IP       = "10.0.1.10"
R1_IFACE1_IP    = "10.0.1.1"
R1_IFACE2_IP    = "10.0.2.1"
HOST_B_IP       = "10.0.2.20"

# ─── Network Constants ───
DEFAULT_TTL         = 100
MAX_SEGMENT_SIZE    = 500
IPV4_TYPE           = 0x0800
UDP_PROTOCOL        = 17

# ─── Port Numbers ───
SRC_PORT    = 5000
DST_PORT    = 80

HOST_A_ARP_TABLE = {
    R1_IFACE1_IP : R1_IFACE1_MAC
}

R1_ARP_TABLE = {
    HOST_A_IP   : HOST_A_MAC,
    HOST_B_IP   : HOST_B_MAC 
}

HOST_B_ARP_TABLE = {
    R1_IFACE2_IP : R1_IFACE2_MAC 
}

HOST_A_ROUTING_TABLE = {
    HOST_B_IP   : { next_hop: R1_IFACE1_IP, interface: "eth0" }
}

R1_ROUTING_TABLE = {
    HOST_A_IP   : { next_hop: HOST_A_IP,  interface: "Interface 1" },
    HOST_B_IP   : { next_hop: HOST_B_IP,  interface: "Interface 2" }
}

HOST_B_ROUTING_TABLE = {
    HOST_A_IP   : { next_hop: R1_IFACE2_IP, interface: "eth0" }
}