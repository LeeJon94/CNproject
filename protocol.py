class UDPSegment:
    def __init__(self, src_port, dst_port, data, segment_type, seq_num, checksum, length):
        self.src_port = src_port
        self.dst_port = dst_port
        self.data = data
        self.segment_type = segment_type
        self.seq_num = seq_num
        self.checksum = checksum
        self.length = length

    def computeChecksum(data):
        return sum(data.encode()) % 256
    
    def verifyChecksum():
        return self.computeChecksum() == self.checksum
    
class IPPacket:
    def __init__(self, src_mac, dst_mac, frame_type, payload):
        self.src_mac = src_mac
        self.dst_mac = dst_mac
        self.frame_type = frame_type
        self.payload = payload