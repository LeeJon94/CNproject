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
            print(f"{self.name}: Layer 4: Data received from Application Layer, Data size={len(chunk)}")
            print(f"{self.name}: Layer 4: Checksum computed")
            print(f"{self.name}: Layer 4: Segment created by adding transport layer header (DATA, seq={seq_num}) (encapsulation)")
            print(f"{self.name}: Layer 4: Segment sent to Network Layer")

            ackReceived = False
            while not ackReceived:
                self.send_packet(segment, dst_ip, router)
                ack = self.last_ack
                if ack is not None and ack.seq_num == seq_num:
                    ackReceived = True
                    seq_num = 1 - seq_num
                else:
                    print(f"{self.name}: Layer 4: Incorrect ACK received, retransmit segment (seq={seq_num})")
    
    def send_packet(self, segment, dst_ip, router):
        route = self.routing_table[dst_ip]
        next_hop = route["next_hop"]
        interface = route["interface"]
        packet = IPPacket(self.ip, dst_ip, DEFAULT_TTL, UDP_PROTOCOL, segment)
        print(f"{self.name}: Layer 3: Segment received from Transport Layer: SRC_IP={self.ip}, DST_IP={dst_ip}, TTL={DEFAULT_TTL}")
        print(f"{self.name}: Layer 3: Destination IP read: {dst_ip}")
        print(f"{self.name}: Layer 3: Routing table lookup performed")
        print(f"{self.name}: Layer 3: Next-hop IP determined: {next_hop}")
        print(f"{self.name}: Layer 3: Outgoing interface selected")
        print(f"{self.name}: Layer 3: Packet forwarded to Data Link Layer")
        self.send_frame(packet, next_hop, router)

    