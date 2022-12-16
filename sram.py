import numpy as np

class SRAM:
    def __init__(self, size, ways)
        num_sets = int(np.ceil(size/ways))
        
        self.size           = size
        self.num_ways       = ways 
        self.num_sets       = num_sets
        self.data_arr       = np.zeros(shape=(ways, num_sets), dtype=int)
        self.tag_arr        = np.zeros(shape=(ways, num_sets), dtype=int)
        self.valid_arr      = np.zeros(shape=(ways, num_sets), dtype=bool)
        # History-LRU, currently only valid for 2-ways
        self.histLRU_arr    = np.zeros(shape=(num_sets), dtype=int)
    
    def find_tag(addr): 
        set_addr    = addr % self.num_sets
        set_tag     = addr / self.num_sets
        way_addr    = -1

        if set_tag in tag_arr[:, set_addr]:
            way_addr = int(np.where(tag_arr[:, set_addr]==set_tag)[0])
        return way_addr

    def read(addr):
        way_addr = find_tag(addr)

        if way_addr != -1


    def write():

    def evict():

    def load(addr):
        

    def store():