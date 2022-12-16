import os, sys

class Packet:

    #Self contained method to generate a new "packet"
    def __init__(self, in_port, address):
        #Input port which the packet enters
        self.inp_port = in_port
        #Memory address for the simulated stage that we will be using
        self.address = -1
        #By default no recirculations
        self.recirc = -1
        #No events processed to begin
        self.timestamps = []

