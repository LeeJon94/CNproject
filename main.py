# =============================================================================
# main.py
# Entry point for the Mini Internet Protocol Stack Simulator.
#
# Usage:
#   python main.py <message_size_in_bytes>
#
# Example:
#   python main.py 10     → sends a 10-byte message
#   python main.py 1200   → sends a 1200-byte message (split into 3 segments)
#
# The simulation models:
#   Host A → Router R1 → Host B   (DATA segments)
#   Host B → Router R1 → Host A   (ACK segments)
# =============================================================================

import sys #lets the program read things typed in the terminal
from config import(
    IP, MAC, ARP_A, ARP_R1, ARP_B,
    ROUTING_A, ROUTING_R1, ROUTING_B,
    MAX_SEGMENT_SIZE, DATA, ACK,
)
from devices import Host, Router


# =============================================================================
# Build the simulated network devices
# =============================================================================

def build_network():
    """
    Instantiate Host A, Router R1, and Host B with their configurations.

    Returns:
        tuple: (host_a, router_r1, host_b)
    """

    host_a = Host(
        name          = "Host A",
        ip            = IP["A"],
        mac           = MAC["A"],
        arp_table     = ARP_A,
        routing_table = ROUTING_A,
    )

    router_r1 = Router(
        name       = "Router R1",
        interfaces = {
            "Interface 1": (IP["R1_1"], MAC["R1_1"]),
            "Interface 2": (IP["R1_2"], MAC["R1_2"]),
        },
        arp_table     = ARP_R1,
        routing_table = ROUTING_R1,
    )

    host_b = Host(
        name          = "Host B",
        ip            = IP["B"],
        mac           = MAC["B"],
        arp_table     = ARP_B,
        routing_table = ROUTING_B,
    )

    return host_a, router_r1, host_b


# =============================================================================
# Simulation: deliver one frame through the network (A → R1 → B)
# =============================================================================

def forward_a_to_b(frame, router_r1, host_b):
    """
    Simulate a single frame travelling from Host A through Router R1 to Host B.

    Steps:
      1. Router R1 receives the frame on Interface 1
      2. Router R1 forwards the re-framed packet out Interface 2
      3. Host B receives the frame

    Args:
        frame     (EtherFrame): Frame sent by Host A
        router_r1 (Router):     The router in the middle
        host_b    (Host):       The destination host

    Returns:
        tuple: result from host_b.l2_receive (seg_type, seq, data) or None
    """
    # Router receives on Interface 1, returns a new frame for Interface 2
    forwarded_frame = router_r1.l2_receive(frame, "Interface 1")
    if forwarded_frame is None:
        return None

    # Host B receives the forwarded frame
    return host_b.l2_receive(forwarded_frame)


def forward_b_to_a(frame, router_r1, host_a):
    """
    Simulate an ACK frame travelling from Host B through Router R1 to Host A.

    Args:
        frame     (EtherFrame): Frame sent by Host B
        router_r1 (Router):     The router in the middle
        host_a    (Host):       The original sender (now the ACK receiver)

    Returns:
        tuple: result from host_a.l2_receive (ACK, seq, b"") or None
    """
    # Router receives on Interface 2, returns a new frame for Interface 1
    forwarded_frame = router_r1.l2_receive(frame, "Interface 2")
    if forwarded_frame is None:
        return None

    return host_a.l2_receive(forwarded_frame)


# =============================================================================
# rdt2.2 Sender logic
# =============================================================================

def send_segment_rdt22(host_a, router_r1, host_b,
                       data_chunk, seq,
                       src_port, dst_port):
    """
    Send one data chunk using the rdt2.2 (Alternating Bit) protocol.

    rdt2.2 rules (assuming no loss, no corruption in this simulation):
      - Sender sends DATA with seq number
      - Receiver sends ACK with same seq number
      - If sender gets wrong ACK → retransmit (won't happen here, but coded in)
      - Sender only advances when it receives the correct ACK

    Args:
        host_a    (Host):   The sending host
        router_r1 (Router): The router
        host_b    (Host):   The receiving host
        data_chunk(bytes):  The chunk of application data to send
        seq       (int):    Current sequence number (0 or 1)
        src_port  (int):    Source port
        dst_port  (int):    Destination port

    Returns:
        int: Next sequence number (flipped: 0→1 or 1→0)
    """
    while True:
        # Drive the full stack send from Layer 4 down and capture the frame
        frame = _send_full_stack(host_a, data_chunk, src_port, dst_port,
                                  IP["B"], seq)

        # --- FORWARD A → R1 → B, receive result at Host B ---
        result = forward_a_to_b(frame, router_r1, host_b)

        if result is None:
            # Packet was dropped (e.g. TTL expired) — retransmit
            print(f"Host A: Layer 4: Segment retransmitted due to packet drop")
            continue

        seg_type, rcv_seq, rcv_data = result

        # Host B received the DATA segment. Now it must send ACK.
        # Print the ACK creation logs (Layer 4 send side at Host B).
        print(f"{host_b.name}: Layer 4: Segment created by adding transport layer "
              f"header (ACK, seq={seq})")
        print(f"{host_b.name}: Layer 4: Segment sent to Network Layer")

        # Build and route the ACK frame (B → R1 → A)
        ack_frame = _capture_ack(host_b, seq, dst_port, src_port, IP["A"])

        # --- FORWARD ACK (B → R1 → A) ---
        ack_result = forward_b_to_a(ack_frame, router_r1, host_a)

        if ack_result is None:
            print(f"Host A: Layer 4: ACK lost — retransmitting segment")
            continue

        ack_type, ack_seq, _ = ack_result

        if ack_type == ACK and ack_seq == seq:
            # Correct ACK received — advance to next sequence number
            return 1 - seq  # Flip: 0→1, 1→0
        else:
            # Wrong ACK — retransmit
            print(f"Host A: Layer 4: Segment retransmitted due to incorrect ACK")
            continue


def _send_full_stack(host: Host, data: bytes, src_port: int, dst_port: int,
                     dst_ip: str, seq: int):
    """
    Drive the full send path (Layer 4 → Layer 3 → Layer 2) on a Host
    and return the resulting Ethernet frame.

    This patches around the fact that l4_send → l3_send → l2_send chain
    doesn't natively return the frame (it's designed to "send" it). We
    intercept the l2_send return value here.

    Args:
        host     (Host):  The sending host
        data     (bytes): Application payload
        src_port (int):   Source port
        dst_port (int):   Destination port
        dst_ip   (str):   Destination IP
        seq      (int):   Sequence number

    Returns:
        EtherFrame: The frame ready to be placed on the wire
    """
    from protocol import UDPSegment, IPPacket, EtherFrame
    from config import DEFAULT_TTL, DATA

    # --- Layer 4 ---
    print(f"{host.name}: Layer 4: Data received from Application Layer. "
          f"Data size={len(data)}")
    segment = UDPSegment(src_port, dst_port, DATA, seq, data)
    print(f"{host.name}: Layer 4: Checksum computed")
    print(f"{host.name}: Layer 4: Segment created by adding transport layer "
          f"header (DATA, seq={seq}) (encapsulation)")
    print(f"{host.name}: Layer 4: Segment sent to Network Layer")

    # --- Layer 3 ---
    print(f"{host.name}: Layer 3: Segment received from Transport Layer: "
          f"SRC_IP={host.ip}, DST_IP={dst_ip}, TTL={DEFAULT_TTL}")
    packet = IPPacket(host.ip, dst_ip, DEFAULT_TTL, segment)
    print(f"{host.name}: Layer 3: Destination IP read: {dst_ip}")
    print(f"{host.name}: Layer 3: Routing table lookup performed")
    next_hop, interface = host._routing_lookup(dst_ip)
    print(f"{host.name}: Layer 3: Next-hop IP determined: {next_hop}")
    print(f"{host.name}: Layer 3: Outgoing interface selected")
    print(f"{host.name}: Layer 3: Packet forwarded to Data Link Layer")

    # --- Layer 2 ---
    frame = host.l2_send(packet, next_hop)
    return frame


def _capture_ack(host: Host, seq: int, src_port: int, dst_port: int,
                 dst_ip: str):
    """
    Build and return the ACK frame that Host B sends back to Host A.

    The ACK segment creation log lines were ALREADY printed inside
    host.l4_receive → host.l4_send_ack. Here we silently reconstruct
    the frame object so we can route it through the simulation,
    then print the Layer 3 and Layer 2 forwarding lines.

    Args:
        host     (Host): The ACK-sending host (Host B)
        seq      (int):  Sequence number being ACK'd
        src_port (int):  Source port for ACK (Host B's port)
        dst_port (int):  Destination port for ACK (Host A's port)
        dst_ip   (str):  Destination IP for ACK (Host A)

    Returns:
        EtherFrame: The ACK frame ready to be forwarded
    """
    from protocol import UDPSegment, IPPacket, EtherFrame
    from config import DEFAULT_TTL, ACK

    # Silently reconstruct the ACK segment (logs already printed by l4_send_ack)
    ack_seg = UDPSegment(src_port, dst_port, ACK, seq, b"")

    # Layer 3 — print forwarding logs
    print(f"{host.name}: Layer 3: Segment received from Transport Layer: "
          f"SRC_IP={host.ip}, DST_IP={dst_ip}, TTL={DEFAULT_TTL}")
    packet = IPPacket(host.ip, dst_ip, DEFAULT_TTL, ack_seg)
    print(f"{host.name}: Layer 3: Destination IP read: {dst_ip}")
    print(f"{host.name}: Layer 3: Routing table lookup performed")
    next_hop, interface = host._routing_lookup(dst_ip)
    print(f"{host.name}: Layer 3: Next-hop IP determined: {next_hop}")
    print(f"{host.name}: Layer 3: Outgoing interface selected")
    print(f"{host.name}: Layer 3: Packet forwarded to Data Link Layer")

    # Layer 2 — frame and send
    frame = host.l2_send(packet, next_hop)
    return frame


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """
    Main simulation entry point.

    Reads message size from CLI, builds the network, segments the message
    if needed, then sends each segment using rdt2.2 from Host A to Host B.
    """
    # --- Parse command-line argument ---
    if len(sys.argv) != 2:
        print("Usage: python main.py <message_size_in_bytes>")
        sys.exit(1)

    try:
        msg_size = int(sys.argv[1])
        if msg_size <= 0:
            raise ValueError
    except ValueError:
        print("Error: message size must be a positive integer")
        sys.exit(1)

    # --- Build the simulated application message (msg_size bytes of 'x') ---
    message = b'x' * msg_size

    # --- Instantiate network devices ---
    host_a, router_r1, host_b = build_network()

    # Fixed port numbers for this simulation
    SRC_PORT = 5000
    DST_PORT = 80

    # --- Segment the message ---
    # If message is larger than MAX_SEGMENT_SIZE (500 bytes), split it.
    chunks = [
        message[i:i + MAX_SEGMENT_SIZE]
        for i in range(0, len(message), MAX_SEGMENT_SIZE)
    ]

    total_segments = len(chunks)
    if total_segments > 1:
        print(f"\n=== Message size {msg_size} bytes exceeds {MAX_SEGMENT_SIZE}-byte "
              f"limit. Splitting into {total_segments} segments. ===\n")

    # --- Send each chunk using rdt2.2 ---
    seq = 0  # Start with sequence number 0

    for i, chunk in enumerate(chunks):
        if total_segments > 1:
            print(f"\n{'='*60}")
            print(f"  Sending segment {i+1} of {total_segments} "
                  f"({len(chunk)} bytes, seq={seq})")
            print(f"{'='*60}\n")

        seq = send_segment_rdt22(
            host_a, router_r1, host_b,
            chunk, seq,
            SRC_PORT, DST_PORT,
        )

    print(f"\n=== Transmission complete. {total_segments} segment(s) sent. ===")


if __name__ == "__main__":
    main()
