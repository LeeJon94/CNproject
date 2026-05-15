# JO ALMERO / 24849627
# THIS FILE CONTAINS THE ETHERNETFRAME, IPPACKET AND UDPSEGMENT
# IT ALSO CONTAINS THE COMPUTERCHECKSUM AND VERIFYCHECKSUM FUNCTION

class UDPSegment:
    def __init__(self, src_port, dst_port, data, segment_type, seq_num):
        self.src_port = src_port
        self.dst_port = dst_port
        self.data = data
        self.segment_type = segment_type
        self.seq_num = seq_num
        self.checksum = self.computeChecksum()
        self.length = 8 + len(data)

    def computeChecksum(self):
        return sum(self.data.encode()) % 256
    
    def verifyChecksum(self):
        return self.computeChecksum() == self.checksum
    
class IPPacket: #contains the sender's address, receiver's address, and the actual data (like an envelope)
    HEADER_SIZE = 12  # bytes: SrcIP(4) + DstIP(4) + TTL(1) + Protocol(1) + TotalLen(2)
    def __init__(self, src_ip, dst_ip, ttl, protocol, payload):
        self.src_ip      = src_ip
        self.dst_ip      = dst_ip
        self.ttl         = ttl
        self.protocol    = protocol
        self.payload     = payload
        self.total_length = self.HEADER_SIZE + payload.length
    def decrement_ttl(self):
        """
        Decrement TTL by 1 (done at each router).
        Returns:
            int: New TTL value after decrement
        """
        self.ttl -= 1
        return self.ttl
    def __repr__(self):
        return (f"IPPacket(src={self.src_ip}, dst={self.dst_ip}, "
                f"ttl={self.ttl}, total_len={self.total_length})")

class EthernetFrame: #package of data sent over a network
    def __init__(self, src_mac, dst_mac, frame_type, payload): #this specific frame being created
        self.src_mac = src_mac #source MAC address (the sender's hardware ID)
        self.dst_mac = dst_mac #destination MAC address (the receiver's hardware ID)
        self.frame_type = frame_type #type of data being carried inside (should always be passed as ETHER_TYPE_IPV4 (0x0800))
        self.payload = payload #the actual data being sent (the contents)
    def __repr__(self): #how the object looks when printed
        #builds and return a text description of the frame
        return (f"EthernetFrame(src={self.src_mac}, dst={self.dst_mac}, "
                f"type=0x{self.frame_type:04X})") #show frame_type as a 4 digit hexadecimal number using uppercase letters