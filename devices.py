# JO ALMERO / 24849627
# THIS FILE WILL IMPLEMENT THE HOST AND ROUTER LAYERS

class Host:
    def __init__(self, name, ID, mac, routing_table, arp_table):
        self.name = name
        self.ID = ID
        self.mac = mac
        self.routing_table = routing_table
        self.arp_table = arp_table

    # WHEN HOST A WANTS TO SEND A MSG TO HOST B
    def send(data, dst_ip, router):
        chunks = [data[i:i+MAX_SEGMENT_SIZE] for i in range(0, len(data), MAX_SEGMENT_SIZE)]

        for chunk in chunks:
            segment = UDPSegment(SRC_PORT, DST_PORT, chunk, 0, seq_num)
            print(f"{self.name}: Layer 4: Data received from Application Layer, Data size={len{chunk}}")
            