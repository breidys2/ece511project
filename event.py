import heapq
from enum import Enum
from packet import *

class EventType(Enum):
    INGRESS=0


class Event:
    def __init__(self,timestamp:int, pkt:Packet, EventType ev_type):
        self.ts = timestamp
        self.pkt = pkt
        self.ev_type = ev_type


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
        if event.request is not None:
            event.request.timestamps.append(self.timestamp)
        self.priority_queue.put(event)

    def get(self) -> Optional[Event]:
        if self.priority_queue.qsize() == 0:
            return None
        r: Event = self.priority_queue.get()
        self.timestamp = max(self.timestamp, r.timestamp)
        if r.request is not None:
            r.request.timestamps.append(self.timestamp)
        return r

    def qsize(self) -> int:
        return self.priority_queue.qsize()
