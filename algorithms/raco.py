import numpy as np
import sys
np.set_printoptions(threshold=sys.maxsize)

from graph.network import Network
from graph.node import Node

from problem import Problem

from algorithms.ls.search2 import Search2
from algorithms.ls.search1 import Search1

from algorithms.insertion import Insertion

import random
import copy

class RACO:
    def __init__(self, network, requests, max_capacity):
        self.network = network
        self.split_requests(requests)
        self.max_capacity = max_capacity
        self.set_parameter()

        self.generate_pheromone()
        
        self.static_routing()
        

    def set_parameter(self):
        self.num_ants = 50
        self.max_iteration = 50

        self.alpha = 1
        self.beta = 2
        self.rho = 0.6
        self.q = 100

        self.best_distance = float('inf')
        self.best_solution = None

    def split_requests(self, requests): #tach request tinh, dong
        self.sta_requests = list()
        self.dyn_requests = list()
        for request in requests:
            if request.time == 0:
                self.sta_requests.append(request)
            else: self.dyn_requests.append(request)


    def static_routing(self):
        for i in range (self.max_iteration):
            solutions = list()
            candidate_list = list()
            for request in self.sta_requests:
                candidate_list.append(request)

            for request in self.dyn_requests: #test aco, remove later
                candidate_list.append(request)

            self.depot = candidate_list.pop(0)   #bo depot ra khoi candidate list

            print("hello this is", self.depot.node)



            for ant in range(self.num_ants):
                solution = [[self.depot]] #start from depot
                pointer = 0 #index of current
                remain_capacity = self.max_capacity
                visited = set()

                solution_time = 0
                current_node = self.depot

                while len(visited) < len(self.sta_requests) + len(self.dyn_requests) -1:  # Visit all customers
                    probability = self.generate_probability(current_node, candidate_list, visited, remain_capacity, solution_time)

                    if len(probability) == 0:  # Check capacity constraint for vehicle
                        solution[pointer].append(self.depot)
                        pointer += 1
                        solution.append([self.depot])
                        current_node = self.depot
                        remain_capacity = self.max_capacity
                        solution_time = 0
                        continue

                    next_node = self.choose_next_node(probability)

                    # print("capa ", remain_capacity)
                    # print(next_node.node)

                    solution[pointer].append(next_node)
                    visited.add(next_node.node)
                    remain_capacity -= next_node.demand

                    solution_time += self.network.links[(current_node.node, next_node.node)].distance
                    solution_time = max(solution_time, next_node.start) #neu den som thi doi

                    if remain_capacity < 0:  # Check capacity constraint for vehicle
                        solution[pointer].pop()
                        solution[pointer].append(self.depot)
                        pointer += 1
                        solution.append([self.depot])
                        current_node = self.depot
                        remain_capacity = self.max_capacity
                        solution_time = 0
                        continue

                    current_node = next_node

                    # print(solution)


                solution[pointer].append(self.depot)  # Return to depot


                # test insertion

                # if True:
                #     n1 = int(random.random()*(len(solution)-1))
                #     n2 = int(random.random()*(len(solution)-1))
                #     while n2 == n1:
                #         n2 = int(random.random()*(len(solution)-1))
                #     if len(solution[n1]) < len(solution[n2]):
                #         n1, n2 = n2, n1

                #     n = int(random.random()*(len(solution[n2])-1))
                #     temp, cd = Insertion(route = solution[n1], max_capacity = self.max_capacity, network = self.network).insert_node(node = solution[n2][n])
                #     if cd == True:
                #         del solution[n2][n]
                #         solution[n1] = temp

                if True:
                    n1 = int(random.random()*(len(solution)-1))
                    n2 = int(random.random()*(len(solution)-1))
                    while n2 == n1:
                        n2 = int(random.random()*(len(solution)-1))
                    if len(solution[n1]) < len(solution[n2]):
                        n1, n2 = n2, n1

                    temp, cd = Insertion(route = solution[n1], max_capacity = self.max_capacity, network = self.network).insert_route(solution[n2])
                    if cd == True:
                        del solution[n2]
                        solution[n1] = temp

                #sua sau
                """
                n = random.random()
                if n > 0.8:
                    solution = Search1(solution,self.max_capacity,self.network).search1()

                for i in range(len(solution)):
                    print(solution[i].node, end= " ")
                print()
                """

                solutions.append(solution)
                

                #test local search
                # n = random.random()
                # if n > 0.8 and len(solutions) > 3:
                #     n1 = int(random.random()*(len(solutions)-1))
                #     n2 = int(random.random()*(len(solutions)-1))
                #     # print(n1, n2)
                #     while n2 == n1:
                #         n2 = int(random.random()*(len(solutions)-1))
                #         # print(n2)
                #     search2 = Search2(solutions[n1],solutions[n2])
                #     temp1, temp2 = search2.swap()
                #     solutions[n1] = temp1
                #     solutions[n2] = temp2


            # print(solutions)
            
            self.update_pheromone(solutions)
        
            for solution in solutions:
                distance = self.calculate_solution_distance(solution)
                print(distance)
                if distance < self.best_distance:
                    self.best_distance = distance
                    self.best_solution = solution

            # self.best_solution = best_solution
            # self.best_distance = best_distance


            print("Best: ", self.best_distance)
            self.print_route(self.best_solution)

        # print(self.pheromone)


    def generate_probability(self, current_node, candidate_list, visited, remain_capacity, solution_time):
        probability = list()
        total = 0
        for request in candidate_list: 
            if request.node not in visited:
                # if remain_capacity >= request.demand:
                if solution_time + self.network.links[(current_node.node, request.node)].distance < request.end:
                    if solution_time + self.network.links[(current_node.node, request.node)].distance >= request.start:
                        total += (self.pheromone[(current_node.node,request.node)]**self.alpha)/(self.network.links[(current_node.node,request.node)].distance)  #cong thuc toan hoc cua haco
                        probability.append((request,total))
                    else:
                        total += (self.pheromone[(current_node.node,request.node)]**self.alpha)/(self.network.links[(current_node.node,request.node)].distance 
                                                                                                 + request.end - (self.network.links[(current_node.node,request.node)].distance + solution_time))  #doi request bat dau
                        probability.append((request,total))

        probability = [(node, prob / total) for node, prob in probability]

        # if len(probability) == 0:
        #     return [(self.depot, 1)]

        return probability
    
    def choose_next_node(self, probability):
        r = np.random.rand()
        for node, prob in probability:
            if r <= prob:
                return node


    def generate_pheromone(self):
        self.pheromone = np.ones((self.network.num_nodes, self.network.num_nodes))

    def update_pheromone(self, solutions):
        delta_pheromone = np.zeros_like(self.pheromone)
        for solution in solutions:
            for i in range(len(solution)):
                for j in range(len(solution[i])-1):
                    current_node = solution[i][j]
                    next_node = solution[i][j+1]
                    delta_pheromone[current_node.node][next_node.node] += self.q / self.calculate_solution_distance(solution)

        self.pheromone = (1 - self.rho) * self.pheromone + delta_pheromone

        # self.pheromone =  (self.pheromone + delta_pheromone)

    def calculate_solution_distance(self, solution):
        if self.check_capacity(solution, self.max_capacity) and self.check_time(solution): return float('inf')
        distance = 0
        for i in range(len(solution)):
            for j in range(len(solution[i])-1):
                distance += self.network.links[(solution[i][j].node,solution[i][j+1].node)].distance
        return distance
    
    
    def check_capacity(self, route: list, max_capacity):
        #check capacity
        for i in range(len(route)):
            cap = 0
            for request in route[i]:
                # print(request)
                cap += request.demand
            if cap > max_capacity:
                return False
        return True
        
    def check_time(self, route: list):
        #check time window
        time = 0
        for i in range(len(route)):
            for j in range(len(route[i])-1):
                time = time + 0 + self.network.links[(route[i][j].node, route[i][j+1].node)].distance
                if time < route[i][j+1].start:
                    time = route[i][j+1].start
                if time > route[i][j+1].end:
                    return False
        return True
    
    def print_route(self, route):
        #lam 1 function rieng
        for i in range(len(route)):
            for j in range(len(route[i])):
                print(route[i][j].node, end = ' ')
            print()


if __name__ == "__main__":
    np.random.seed()
    problem1 = Problem("data/C100/C101.TXT")
    network = problem1.network
    requests = problem1.requests
    for request in requests:
        print(request.node)
    max_capacity = problem1.capacity
    haco = RACO(network = network, requests = requests, max_capacity = max_capacity)

    


