import numpy as np

class SRAM:
    def __init__(self, size, ways):
        num_sets = int(np.ceil(size/ways))

        self.size           = size
        self.num_ways       = ways
        self.num_sets       = num_sets
        self.tag_arr        = np.zeros(shape=(ways, num_sets), dtype=int)
        self.valid_arr      = np.zeros(shape=(ways, num_sets), dtype=bool)
        # History-LRU, currently only valid for 2-ways
        self.histLRU_arr    = np.zeros(shape=(num_sets), dtype=int)
    
    # Find if tag is present, and return corresponding way_addr if so
    def find_tag(self, addr, set_addr, set_tag):
        way_addr    = -1

        if set_tag in self.tag_arr[:, set_addr] and True in self.valid_arr[:, set_addr]:
            way_addr = np.where(self.tag_arr[:, set_addr] == set_tag)[0][0]
            
            if self.valid_arr[way_addr, set_addr] == True:
                if way_addr == 0:
                    self.histLRU_arr[set_addr] = max(-3, self.histLRU_arr[set_addr] - 1)
                elif way_addr == 1: 
                    self.histLRU_arr[set_addr] = min(4, self.histLRU_arr[set_addr] + 1)
            
        return way_addr

    # Access cache (read/write disambiguation) at global (RLDRAM) memory address "addr"
    def access(self, addr):
        set_addr = addr % self.num_sets
        set_tag = int(addr / self.num_sets)

        way_addr = self.find_tag(addr, set_addr, set_tag)
        # print("way_addr: ", way_addr, " set_addr: ", set_addr, "set_tag: ", set_tag, "\n")
        
        # cache hit
        if way_addr != -1:
            return True
        # cache miss
        else:
            # evict, load
            if self.histLRU_arr[set_addr] <= 0:
                way_addr = 1
            else:
                way_addr = 0

            self.evict(way_addr, set_addr)
            self.load(way_addr, set_addr, set_tag)
            return False

    # Evict (write) SRAM word back to RLDRAM, currently a dummy function
    def evict(self, way_addr, set_addr):
        # insert delay logic, to signify write to RLDRAM?
        self.valid_arr[way_addr, set_addr] = False
        return 0

    # Load (read) SRAM word from RLDRAM
    def load(self, way_addr, set_addr, set_tag):
        # insert delay logic, to signify read from RLDRAM?
        self.tag_arr[way_addr, set_addr] = set_tag
        self.valid_arr[way_addr, set_addr] = True
        return 0