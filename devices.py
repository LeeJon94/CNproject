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

    def send_frame(self, packet, next_hop, router):
        dst_mac = self.arp_table[next_hop]
        frame = EthernetFrame(self.mac, dst_mac, IPV4_TYPE, packet)
        print(f"{self.name}: Layer 2: Packet received from Network Layer")
        print(f"{self.name}: Layer 2: Destination MAC lookup for next-hop IP ({next_hop}) → {dst_mac}")
        print(f"{self.name}: Layer 2: Frame created: SRC_MAC={self.mac}, DST_MAC={dst_mac}")
        print(f"{self.name}: Layer 2: Frame sent")
        router.receive_frame(frame, "Interface 1")

    def receive_packet(self, packet):
        print(f"{self.name}: Layer 3: Packet received from Data Link layer: SRC_IP={packet.src_ip}, DST_IP={packet.dst_ip}, TTL+{packet.ttl}")
        print(f"{self.name}: Layer 3: Destination IP read: {packet.dst_ip}")
        print(f"{self.name}: Layer 3: Packet identified as local delivery")
        print(f"{self.name}: Layer 3: Segment delivered to Transport Layer")
        self.receive_segment(packet.payload)

    def receive_segment(self, segment, dst_ip=None, router=None):
        print(f"{self.name}: Layer 4: Segment received from Network Layer")
        if not segment.verify_checksum():
            print(f"{self.name}: Layer 4: Checksum error, segment discarded")
            if self.last_ack:
                router.receive_frame(self.last_ack, "Interface")
            return
        print(f"{self.name}: Layer 4: Checksum verified")

        if segment.segment_type == 0:  # DATA
            print(f"{self.name}: Layer 4: DATA segment delivered to Application Layer. Data size={len(segment.data)}")
            ack = UDPSegment(DST_PORT, SRC_PORT, "", 1, segment.seq_num)
            self.last_ack = ack
            print(f"{self.name}: Layer 4: Segment created by adding transport layer header (ACK, seq={segment.seq_num})")
            print(f"{self.name}: Layer 4: Segment sent to Network Layer")
            self.send_packet(ack, dst_ip, router)

        elif segment.segment_type == 1:  # ACK
            print(f"{self.name}: Layer 4: ACK received: seq={segment.seq_num}")
            self.last_ack = segment

    class Router:

        def __init__(self, name, routing_table, arp_table, interfaces):
            self.name          = name
            self.routing_table = routing_table
            self.arp_table     = arp_table
            self.interfaces    = interfaces  # e.g. {"Interface 1": "BB:BB:BB:BB:BB:BB", "Interface 2": "CC:CC:CC:CC:CC:CC"}
            self.mac_table     = {}          # learned MAC addresses
            self.hosts         = {}          # e.g. {"Interface 1": host_a, "Interface 2": host_b}

        def receive_frame(self, frame, interface):
            # Layer 2
            src_mac = frame.src_mac
            self.mac_table[src_mac] = interface
            print(f"{self.name}: Layer 2: Frame received on {interface}")
            print(f"{self.name}: Layer 2: Source MAC learned: {src_mac} on {interface}")
            print(f"{self.name}: Layer 2: Packet delivered to Network Layer")
            self.forward_packet(frame.payload)

        def forward_packet(self, packet):
            # Layer 3
            print(f"{self.name}: Layer 3: Packet received from Data Link Layer: SRC_IP={packet.src_ip}, DST_IP={packet.dst_ip}, TTL={packet.ttl}")
            print(f"{self.name}: Layer 3: Destination IP read: {packet.dst_ip}")
            packet.ttl -= 1
            if packet.ttl == 0:
                print(f"{self.name}: Layer 3: TTL expired, packet dropped")
                return
            print(f"{self.name}: Layer 3: TTL decremented: {packet.ttl + 1} → {packet.ttl}")
            route    = self.routing_table[packet.dst_ip]
            next_hop = route["next_hop"]
            out_interface = route["interface"]
            print(f"{self.name}: Layer 3: Routing table lookup performed")
            print(f"{self.name}: Layer 3: Next-hop IP determined: {next_hop}")
            print(f"{self.name}: Layer 3: Outgoing interface selected ({out_interface})")
            print(f"{self.name}: Layer 3: Packet forwarded to Data Link Layer")
            self.send_frame(packet, next_hop, out_interface)

        def send_frame(self, packet, next_hop, out_interface):
            # Layer 2
            dst_mac = self.arp_table[next_hop]
            src_mac = self.interfaces[out_interface]
            frame   = EthernetFrame(src_mac, dst_mac, IPV4_TYPE, packet)
            print(f"{self.name}: Layer 2: Packet received from Network Layer")
            print(f"{self.name}: Layer 2: Destination MAC lookup for next-hop IP ({next_hop}) → {dst_mac}")
            print(f"{self.name}: Layer 2: Frame created: SRC_MAC={src_mac}, DST_MAC={dst_mac}")
            print(f"{self.name}: Layer 2: Frame forwarded on {out_interface}")
            destination = self.hosts[out_interface]
            destination.receive_frame(frame)