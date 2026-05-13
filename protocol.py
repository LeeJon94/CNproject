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
    
class IPPacket:
    def __init__(self, src_ip, dst_ip, ttl, protocol, payload):
        self.src_ip      = src_ip
        self.dst_ip      = dst_ip
        self.ttl         = ttl
        self.protocol    = protocol
        self.payload     = payload

class EthernetFrame:
    def __init__(self, src_mac, dst_mac, frame_type, payload):
        self.src_mac = src_mac
        self.dst_mac = dst_mac
        self.frame_type = frame_type
        self.payload = payload