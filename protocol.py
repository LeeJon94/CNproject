class UDPSegment:
    def __init__(self, src_port, dst_port, data, segment_type, seq_num, checksum, length):
        self.src_port = src_port
        self.dst_port = dst_port
        self.data = data
        self.segment_type = segment_type
        self.seq_num = seq_num
        self.checksum = checksum
        self.length = length
        pass