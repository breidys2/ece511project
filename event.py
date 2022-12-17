import heapq
from enum import Enum
from packet import *

class EventType(Enum):
    INGRESS=0
    EGRESS = 1
    RECIRC = 2



class Event:
    def __init__(self,timestamp:int, pkt:Packet, ev_type:EventType):
        self.timestamp = timestamp
        self.pkt = pkt
        self.ev_type = ev_type

    # define proiority based on timestamp order
    def __lt__(self, other: "Event"):
        return self.timestamp < other.timestamp
    
    def __le__(self, other: "Event"):
        return self.timestamp <= other.timestamp
    
    def __eq__(self, other: "Event"):
        return self.timestamp == other.timestamp

    def __ne__(self, other: "Event"):
        return self.timestamp != other.timestamp

    def __gt__(self, other: "Event"):
        return self.timestamp > other.timestamp
    
    def __ge__(self, other: "Event"):
        return self.timestamp >= other.timestamp

class PriorityQueue: 
    def __init__(self):
        self._queue = []
    
    def qsize(self) -> int:
        return len(self._queue)

    def put(self, item):
        heapq.heappush(self._queue, item)
    
    def get(self):
        return heapq.heappop(self._queue)

# The basic discrete event simulator    
class EventSimulator:
    def __init__(self, DEBUG: bool = False):
        self.DEBUG: bool = DEBUG

        self.priority_queue: PriorityQueue[Event] = PriorityQueue()
        self.timestamp: int = 0
    
    def __str__(self):
        return f'EventQueue with length {self.priority_queue.qsize()}'
    
    def register(self, event: Event):
        if event.pkt is not None:
            event.pkt.timestamps.append(self.timestamp)
        self.priority_queue.put(event)

    def get(self):
        if self.priority_queue.qsize() == 0:
            return None
        ev = self.priority_queue.get()
        self.timestamp = max(self.timestamp, ev.timestamp)
        if ev.pkt is not None:
            ev.pkt.timestamps.append(self.timestamp)
        return ev

    def qsize(self) -> int:
        return self.priority_queue.qsize()
