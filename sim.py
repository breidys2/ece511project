from packet import *
from event import *
#from SRAM import *
import random
from numpy.random import zipf
random.seed(42)


#Using zipf to simulate real workloads based on FB SIGCOMM '15 Paper
def gen_pkt_mem_address(n_entries:int):
    #For now uniform (worst case)
    v = zipf(1.1, 100000) 
    return v
    #test = [0 for _ in range(int(n_entries))]
    #for vv in v:
    #    vvv  = int(vv)
    #    print(vvv)
    #    print(n_entries)
    #    if vvv >= 0 and vvv < int(n_entries):
    #        test[vvv]+=1
    #print(test[0:100])

    #return int(random.random() * n_entries)



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
    n_pkts = 1000
    warmup = int(0.4 * n_pkts)
    #We are simulating stage 1 of 12 stages
    rem_stage_cycle = 11
    sram_sz = 1310720
    #SRAM entries are 128 bits wide (16 bytes)
    sram_entries = sram_sz/16
    rldram_sz = 301989888    
    rldram_entries = rldram_sz/16    
    rldram_lat = 10
    recirc_port = 16

    addresses = gen_pkt_mem_address(rldram_entries)

    #Generate a number of packets and assign them to input ports
    packets = [Packet(int(random.random() * n_ports),addresses[i]) for i in range(n_pkts)]

    #Generate simulator events to ingress the pkts into the queues
    input_ports = [[] for _ in range(n_ports + 1)]
    for pkt in packets:
        input_ports[pkt.inp_port].append(pkt)

    
    print("Qsizes: ")
    for i in range(n_ports + 1):
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
            if random.random() < 0.5:
                sim.register(Event(cur_ev.timestamp + rem_stage_cycle,cur_pkt,EventType.EGRESS))
            else:
                #Check for eviction in the cache
                #If need to first writeback
                #TODO
                cur_ev.pkt.recirc += 1
                if True:
                    sim.register(Event(cur_ev.timestamp + rldram_lat, cur_ev.pkt, EventType.RECIRC))
                else:
                    sim.register(Event(cur_ev.timestamp + 2*rldram_lat, cur_ev.pkt, EventType.RECIRC))



            #Create the next ingress event next cycle
            #First checking recirc port
            if len(input_ports[recirc_port]) > 0:
                sim.register(Event(cur_ev.timestamp + 1, input_ports[recirc_port].pop(), EventType.INGRESS))
            else:
                #Then check another port
                for i in range(n_ports):
                    test_port = (cur_inp_port + i) % n_ports
                    if len(input_ports[test_port]) > 0:
                        sim.register(Event(cur_ev.timestamp + 1, input_ports[test_port].pop(), EventType.INGRESS))
                        cur_inp_port = (test_port + 1) % n_ports
                        break
        elif cur_ev.ev_type == EventType.EGRESS:
            #Just need this for the timestamping
            pass
        elif cur_ev.ev_type == EventType.RECIRC:
            #Just make this packet available for recirculation
            input_ports[recirc_port].append(cur_ev.pkt)




    #At the end of the sim, want to collect output stats
    #First print throughput numbers
    tput = n_pkts/sim.timestamp
    print(f"Throughput: Forwarded {n_pkts} packets in {sim.timestamp} cycles for: {tput}")

    #Next, print latencies
    latencies = []
    recircs = []
    n_recirc = 0 
    for pkt in packets[warmup:]:
        latencies.append(pkt.timestamps[-1] - pkt.timestamps[0])
        if pkt.recirc > 0:
            n_recirc += 1
            recircs.append(pkt.recirc)

    print(f"pkt recirculated: {n_recirc}")
    print(print_percs_str(latencies, "Latencies",
        percs=[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.95,0.99]))
    print(print_percs_str(recircs, "Recircs",
        percs=[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.95,0.99]))

if __name__ == "__main__":
    main()
