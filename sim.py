from packet import *
from event import *
from sram import *
import random
from numpy.random import zipf
from numpy.random import uniform
random.seed(42)


#Using zipf to simulate real workloads based on FB SIGCOMM '15 Paper
def gen_pkt_mem_address(n_entries:int):
    n_entries = int(n_entries)
    #Normal case (zipfian)
    #v = zipf(1.1, n_entries)
    #Worst case (uniform)
    v = uniform(high=n_entries, size=n_entries).astype(int)
    return v

    #For now uniform (worst case)
    #return int(random.random() * n_entries)



def print_percs_str(in_list, header="", percs=[0.5,0.9,0.95,0.99]):
    if len(in_list) == 0:
        return headers + ": N/A"
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
    #Normalizing to increase sim speed
    norm = 10
    #By default we have 16 external ports, one recirculation port, and one cpu port (ignored here)
    n_ports = 16
    sram_sz = int(1310720//norm)
    #SRAM entries are 128 bits wide (16 bytes)
    sram_entries = int(sram_sz//16)
    rldram_sz = int(301989888//norm)    
    rldram_entries = int(rldram_sz//16)   
    rldram_lat = 10
    recirc_port = 16
    #We are simulating stage 1 of 12 stages
    rem_stage_cycle = 11
    n_pkts = int(sram_sz * 4)
    #n_pkts = 200
            
    warmup = int(0.0 * n_pkts)

    addresses = gen_pkt_mem_address(rldram_entries)

    #Generate a number of packets and assign them to input ports
    packets = [Packet(int(random.random() * n_ports),addresses[i], 1 if random.random() < 0.1 else 0) for i in range(n_pkts)]

    #Generate simulator events to ingress the pkts into the queues
    input_ports = [[] for _ in range(n_ports + 1)]
    for pkt in packets:
        input_ports[pkt.inp_port].append(pkt)

    print("Done creating packets " + str(len(packets)))

    #print("Qsizes: ")
    #for i in range(n_ports + 1):
        #print(str(i) + " " + str(len(input_ports[i])))

    #Create simulator
    sim = EventSimulator()

    stage_sram = SRAM(sram_entries, 2)

    #Will feed packets at line rate, RR through the ports
    sim.register(Event(1, input_ports[0].pop(), EventType.INGRESS))

    cur_inp_port = 1

    #RUN SIM
    while sim.qsize() > 0:
        cur_ev = sim.get()
        if cur_ev.pkt.recirc > 1000:
            raise ValueError(cur_ev.pkt.recirc)

        if cur_ev.ev_type == EventType.INGRESS:
            #Grab the next packet from ingress
            cur_pkt = cur_ev.pkt
            #Check SRAM if the packet can be forwarded
            hit, wb = stage_sram.access(cur_pkt.address, cur_pkt.rw)
            if cur_pkt.recirc > 0 and not hit:
                print(f"{cur_pkt.address} miss #{cur_pkt.recirc+1}")
            #if random.random() < 0.5:
            if hit:
                sim.register(Event(cur_ev.timestamp + rem_stage_cycle,cur_pkt,EventType.EGRESS))
            else:
                #Check for eviction in the cache
                cur_ev.pkt.recirc += 1
                if not wb:
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
