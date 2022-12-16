from packet import *
from event import *
#from SRAM import *
import random
random.seed(42)


#TODO generate a packet address to try to mimic the memory access patterns
#of in-network computing functions
def gen_pkt_mem_address(n_entries):
    #For now uniform (worst case)
    return int(random.random() * n_entries)


def print_percs_str(in_list, header="", percs=[0.5,0.9,0.95,0.99]):
    if len(in_list) == 0:
        return ""
    in_list = sorted(in_list)
    out_str = str(header) + "\n"
    ll = len(in_list)
    out_str += "AVG: " + str(sum(in_list)/ll) + "\n"
    out_str += "MIN: " + str(in_list[0]) + "\n"
    out_str += "MAX: " + str(in_list[-1]) + "\n"
    for perc in percs:
        out_str += "P"+ str(perc * 100) + ": " + str(in_list[int(ll * perc)]) + "\n"
    return out_str


def main():

    #By default we have 16 external ports, one recirculation port, and one cpu port (ignored here)
    n_ports = 16
    n_pkts = 32
    #We are simulating stage 1 of 12 stages
    rem_stage_cycle = 11
    sram_sz = 1310720
    #SRAM entries are 128 bits wide (16 bytes)
    sram_entries = sram_sz/16
    rldram_sz = 301989888    
    rldram_entries = rldram_sz/16    
    #Generate a number of packets and assign them to input ports
    packets = [Packet(int(random.random() * n_ports),gen_pkt_mem_address(rldram_entries)) for _ in range(n_pkts)]

    #Generate simulator events to ingress the pkts into the queues
    input_ports = [[] for _ in range(n_ports)]
    for pkt in packets:
        input_ports[pkt.inp_port].append(pkt)

    print("Qsizes: ")
    for i in range(n_ports):
        print(str(i) + " " + str(len(input_ports[i])))
    #Create simulator
    sim = EventSimulator()

    #TODO integrate with andrew
    #stage_sram = SRAM(sram_entries)

    #Will feed packets at line rate, RR through the ports
    sim.register(Event(1, input_ports[0].pop(), EventType.INGRESS))

    cur_inp_port = 1

    #RUN SIM
    while sim.qsize() > 0:
        cur_ev = sim.get()

        if cur_ev.ev_type == EventType.INGRESS:
            #Grab the next packet from ingress
            cur_pkt = cur_ev.pkt
            #Check SRAM if the packet can be forwarded
            #TODO integrate with andrew
            #if stage_sram.check(pkt.address):
            if True:
                sim.register(Event(cur_ev.timestamp + rem_stage_cycle,cur_pkt,EventType.EGRESS))



            #Create the next ingress event next cycle
            for i in range(n_ports):
                test_port = (cur_inp_port + i) % n_ports
                if len(input_ports[test_port]) > 0:
                    sim.register(Event(cur_ev.timestamp + 1, input_ports[test_port].pop(), EventType.INGRESS))
                    cur_inp_port = (test_port + 1) % n_ports
                    break
        elif cur_ev.ev_type == EventType.EGRESS:
            #Just need this for the timestamping
            pass




    #At the end of the sim, want to collect output stats
    #First print throughput numbers
    tput = n_pkts/sim.timestamp
    print(f"Throughput: Forwarded {n_pkts} packets in {sim.timestamp} cycles for: {tput}")

    #Next, print latencies
    latencies = []
    for pkt in packets:
        latencies.append(pkt.timestamps[-1] - pkt.timestamps[0])

    print(print_percs_str(latencies, "Latencies",
        percs=[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.05,0.99]))

if __name__ == "__main__":
    main()
