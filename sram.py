import numpy as np

class SRAM:
    def __init__(self, size, ways):
        num_sets = int(np.ceil(size/ways))

        self.size       = size
        self.num_ways   = ways
        self.num_sets   = num_sets
        self.tag_arr    = np.zeros(shape=(ways, num_sets), dtype=int)
        self.valid_arr  = np.zeros(shape=(ways, num_sets), dtype=bool)
        self.dirty_arr  = np.zeros(shape=(ways, num_sets), dtype=bool)
        # History-LRU, currently only valid for 2-ways
        self.hLRU_arr   = np.zeros(shape=(num_sets), dtype=int)
    
    # Find if tag is present, and return corresponding way_addr if so
    # Does NOT check if tag is valid (maybe it makes more sense to do so here?)
    def find_tag(self, addr, set_addr, set_tag):
        way_addr = -1

        # Scan ways for tag match, and valid == True
        if set_tag in self.tag_arr[:, set_addr]:
            if self.valid_arr[way_addr, set_addr]:
                way_addr = np.where(self.tag_arr[:, set_addr] == set_tag)[0][0]
            
        return way_addr

    # Access cache at global (RLDRAM) memory address "addr"
    # @return hit, writeback
    def access(self, addr, rw):
        set_addr = addr % self.num_sets
        set_tag = int(addr / self.num_sets)

        way_addr = self.find_tag(addr, set_addr, set_tag)
        
        # cache hit
        if way_addr != -1:
            self.update_hLRU(way_addr, set_addr)
            return True, False
        # cache miss
        else:
            # decide which way to evict
            way_addr = self.decide_hLRU(set_addr)
            self.update_hLRU(way_addr, set_addr)
            # writes to SRAM cache are abstracted away
            # dirty + read = wb -> load
            # dirty + write = wb -> load -> write
            # not dirty + read = load
            # not dirty + write = load -> write

            # decide whether to writeback or not
            if self.dirty_arr[way_addr, set_addr] == True:
                # writeback, load new cacheline
                self.evict(way_addr, set_addr)
                self.load(way_addr, set_addr, set_tag)
                
                # SRAM Write
                if rw == 1:
                    self.dirty(way_addr, set_addr)
                # Return hit=false, wb=true
                return False, True
            else:
                # no wb necessary, load new $line, read/write
                self.evict(way_addr, set_addr)
                self.load(way_addr, set_addr, set_tag)

                if rw == 1:
                    self.dirty(way_addr, set_addr)
                # Return hit=false, wb=false
                return False, False

    # Abstract write function, logically dirties the cacheline, but no $line is actually written back
    def dirty(self, way_addr, set_addr):
        self.dirty_arr[way_addr, set_addr] = True
        return 0

    # Evict (write) SRAM word back to RLDRAM, currently a dummy function
    def evict(self, way_addr, set_addr):
        # insert delay logic, to signify write to RLDRAM?
        self.valid_arr[way_addr, set_addr] = False
        self.dirty_arr[way_addr, set_addr] = False
        return 0

    # Load (read) SRAM word from RLDRAM
    def load(self, way_addr, set_addr, set_tag):
        # insert delay logic, to signify read from RLDRAM?
        self.tag_arr[way_addr, set_addr] = set_tag
        self.valid_arr[way_addr, set_addr] = True
        self.dirty_arr[way_addr, set_addr] = False
        return 0

    # Helper function to handle updating historyLRU data structures
    # (simple counter for 2-way set assoc, 3 counters in btree for 4-way set assoc)
    def update_hLRU(self, way_addr, set_addr):
        if self.num_ways == 2:
            if way_addr == 0:
                self.hLRU_arr[set_addr] = max(-3, self.hLRU_arr[set_addr] - 1)
            elif way_addr == 1: 
                self.hLRU_arr[set_addr] = min(4, self.hLRU_arr[set_addr] + 1)
        
        # elif self.num_ways == 4:
        #     if way_addr == 0:
        #         # set_addr - 1 is left child counter, set_addr is parent counter
        #         self.hLRU_arr[set_addr - 1] = max(-3, self.hLRU[set_addr - 1] - 1)
        #         self.hLRU_arr[set_addr] = max(-3, self.hLRU[set_addr - 1] - 1)
        #     elif way_addr == 1:
        #         self.hLRU_arr[set_addr - 1] = max(-3, self.hLRU[set_addr - 1] - 1)
        return 0

    def decide_hLRU(self, set_addr):
        if self.num_ways == 2:
            if self.hLRU_arr[set_addr] <= 0:
                way_addr = 1
            else:
                way_addr = 0

        return way_addr