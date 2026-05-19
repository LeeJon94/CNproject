# JO ALMERO / 24849627
# THIS FILE CONTAINS THE ETHERNETFRAME, IPPACKET AND UDPSEGMENT
# IT ALSO CONTAINS THE COMPUTERCHECKSUM AND VERIFYCHECKSUM FUNCTION

from config import(
    ETHER_TYPE_IPV4, IP_PROTO_UDP, UDP_HEADER_SIZE, IP_HEADER_SIZE,
    DATA, ACK
)

class UDPSegment:
    HEADER_SIZE = 10  #bytes: src_port(2) + dst_port(2) + length(2) + checksum(2) + segment_type(1) + seq_num(1)
    def __init__(self, src_port, dst_port, data, segment_type, seq_num):
        self.src_port = src_port
        self.dst_port = dst_port
        self.data = data
        self.segment_type = segment_type
        self.seq_num = seq_num
        self.length = self.HEADER_SIZE + len(data)
        self.checksum = self.computeChecksum()

    def computeChecksum(self):
        total=(self.src_port + self.dst_port + self.length + self.segment_type + self.seq_num)
        for byte in self.data: #data must be bytes, not str
            total+=byte
        return total%65536 #checksum is 2 bytes per spec
    
    def verifyChecksum(self):
        return self.computeChecksum()==self.checksum
    
    def __repr__(self):
        typeStr="DATA" if self.segment_type == DATA else "ACK"
        return (f"UDPSegment(type={typeStr}, seq={self.seq_num}, "
                f"src_port={self.src_port}, dst_port={self.dst_port}, "
                f"length={self.length}, data_len={len(self.data)})")
    
class IPPacket: #contains the sender's address, receiver's address, and the actual data (like an envelope)
    HEADER_SIZE = 12  #bytes: SrcIP(4) + DstIP(4) + TTL(1) + Protocol(1) + TotalLen(2)
    def __init__(self, src_ip, dst_ip, ttl, protocol, payload):
        self.src_ip      = src_ip #sender's IP address
        self.dst_ip      = dst_ip #receiver's IP address
        self.ttl         = ttl #time to live
        self.protocol    = protocol #type of data inside
        self.payload     = payload #actual data being sent
        self.total_length = self.HEADER_SIZE + payload.length
    def decrement_ttl(self): #count the TTL down by 1, which happens every time the packet passes through a router on its journey
        self.ttl-=1 
        return self.ttl
    def __repr__(self): #how the packet looks when printed
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