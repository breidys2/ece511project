from Packet import *
import random
random.seed(42)


#TODO generate a packet address to try to mimic the memory access patterns
#of in-network computing functions
def gen_pkt_mem_address(n_entries):
    #For now uniform (worst case)
    return int(random.random() * n_entries)


def main():

    #By default we have 16 external ports, one recirculation port, and one cpu port (ignored here)
    n_ports = 16
    n_pkts = 32
    sram_sz = 1310720
    #SRAM entries are 128 bits wide (16 bytes)
    sram_entries = sram_sz/16
    #TODO
    rldram_sz = 301989888    
    rldram_entries = rldram_sz/16    
    #Generate a number of packets and assign them to input ports
    packets = [Packet(int(random.random() * n_ports),gen_pkt_mem_address(rldram_entries)) for _ in range(n_pkts)]

    #Generate simulator events to ingress the pkts into the queues
    input_ports = [[] for _ in range n_ports]
    for pkt in packets:
        input_ports[pkt.inp_port].append(pkt)

    #Create simulator
    sim = EventSimulator()

    #Will feed packets at line rate, RR through the ports
    sim.register(Event(0, 0, EventType.INGRESS))

    cur_inp_port = 1

    #RUN SIM
    while simulator.qsize() > 0:
        cur_ev = simulator.get()

        if cur_ev.ev_type == EventType.INGRESS:
            #Grab the next packet from ingress

            #Create the next ingress event next cycle
        sim.register(Event(cur_ev.ts + 1, cur_inp_port, EventType.INGRESS))
        cur_inp_port = (cur_inp_port + 1) % n_ports




if __name__ == "__main__":
    main()
