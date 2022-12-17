import os, sys

class Packet:

    #Self contained method to generate a new "packet"
    def __init__(self, in_port, address, rw):
        #Input port which the packet enters
        self.inp_port = in_port
        #Memory address for the simulated stage that we will be using
        self.address = address
        #By default no recirculations
        self.recirc = 0
        #0 = read, 1 = write
        self.rw = rw
        #No events processed to begin
        self.timestamps = []

