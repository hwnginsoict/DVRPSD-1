from .link import *
from .node import *

class Network():
    def __init__(self, input_path=None):
        self.input_path = input_path
        

        self.N = dict()
        self.L = dict()
        self.adj = dict()
        self.num_nodes = 0
        self.num_links = 0  
        self.total_travel_time = 0      
        
    
    def __init__(self, customers: dict):
        self.depot = customers[0]
        self.num_nodes = len(customers)
        self.calculate_distance(customers)
        self.customers = customers

    def calculate_distance(self, customers): 
        # self.distance = list()    #distance: matran khoang cach giau 2 dinh
        self.links = dict()    #links: dictionary luu cac link
        for i in range(self.num_nodes):
            distance = list()
            for j in range(i, self.num_nodes):
                self.links[(i,j)] = Link(customers[i], customers[j])
                self.links[(j,i)] = Link(customers[j], customers[i])
  
        return 

     
    def build_pheromone(self, num_sfcs = -1):
        self.pheromone = np.zeros((self.num_nodes, self.num_nodes))
        # for links
        for u, adj_u in self.adj.items():
            for v in adj_u.keys():
                self.pheromone[u][v] = 1
        # for nodes
        for node in self.N.values():
            if node.type:
                self.pheromone[node.id][node.id] = 1

        if num_sfcs != -1:
            self.pheromone = np.stack([self.pheromone]*num_sfcs, axis=0)
    
    def create_constraints(self):
        ...
    def calculate_objective(self):
        ...