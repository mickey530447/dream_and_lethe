#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
House Assignment Solver for Discord Bot
Simplified version of house_assignment_solver.py for Discord integration
"""

import random
from collections import defaultdict
import sys
from pathlib import Path

# Add constants path
sys.path.append(str(Path(__file__).parent.parent))
from constants.bot_constants import HOUSE_CAPACITIES, RELATIONSHIPS

class HouseAssignmentSolver:
    def __init__(self, house_capacities=None, relationships=None):
        """
        Initialize solver with default constants or custom values
        """
        self.house_capacities = house_capacities or HOUSE_CAPACITIES
        self.relationships = relationships or RELATIONSHIPS
        self.people = set()
        self.connection_graph = defaultdict(set)
        
        # Build bidirectional connection graph
        for person, connections in self.relationships.items():
            self.people.add(person)
            for conn in connections:
                self.people.add(conn)
                self.connection_graph[person].add(conn)
                self.connection_graph[conn].add(person)
    
    def calculate_connections_in_house(self, people_in_house):
        """Calculate total connections within a house"""
        connections = 0
        people_list = list(people_in_house)
        for i in range(len(people_list)):
            for j in range(i + 1, len(people_list)):
                if people_list[j] in self.connection_graph[people_list[i]]:
                    connections += 1
        return connections
    
    def calculate_person_priority(self, person, people_pool):
        """Calculate person priority based on connections in pool"""
        connections_in_pool = 0
        for other in people_pool:
            if other != person and other in self.connection_graph[person]:
                connections_in_pool += 1
        return connections_in_pool
    
    def select_best_people(self, people_to_select, max_people):
        """Select best people when count > capacity"""
        if len(people_to_select) <= max_people:
            return people_to_select
        
        # Calculate priority for each person
        person_scores = []
        for person in people_to_select:
            if person in self.people:
                priority = self.calculate_person_priority(person, people_to_select)
                person_scores.append((person, priority))
        
        # Sort by priority (descending)
        person_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select highest priority people
        selected = [person for person, score in person_scores[:max_people]]
        return selected
    
    def optimize_assignment(self, people_to_select, iterations=500):
        """Optimize house assignment for given people"""
        max_people = sum(self.house_capacities)
        
        # Handle too many people
        if len(people_to_select) > max_people:
            selected_people = self.select_best_people(people_to_select, max_people)
        else:
            # Check if all people exist
            selected_people = []
            for person in people_to_select:
                if person in self.people:
                    selected_people.append(person)
        
        # Always return a valid assignment, even if empty or with few people
        if not selected_people:
            return [[], [], []], 0
        
        best_assignment = None
        best_score = 0
        
        # Try different strategies
        for iteration in range(iterations):
            if iteration < iterations // 2:
                assignment = self._fill_first_assignment(selected_people)
            else:
                assignment = self._balanced_assignment(selected_people)
            
            score = self._calculate_total_score(assignment)
            
            # Local search improvement
            improved_assignment, improved_score = self._local_search(assignment)
            
            if improved_score > best_score:
                best_score = improved_score
                best_assignment = improved_assignment
        
        # If no good assignment found, use simple fill-first strategy
        if best_assignment is None:
            best_assignment = self._fill_first_assignment(selected_people)
            best_score = self._calculate_total_score(best_assignment)
        
        return best_assignment, best_score
    
    def _fill_first_assignment(self, people):
        """Fill first house completely before moving to next"""
        assignment = [[], [], []]
        people_copy = people.copy()
        random.shuffle(people_copy)
        
        current_house = 0
        
        for person in people_copy:
            while current_house < 3:
                if len(assignment[current_house]) < self.house_capacities[current_house]:
                    assignment[current_house].append(person)
                    break
                else:
                    current_house += 1
            else:
                break
        
        return assignment
    
    def _balanced_assignment(self, people):
        """Balanced assignment prioritizing less filled houses"""
        assignment = [[], [], []]
        people_copy = people.copy()
        random.shuffle(people_copy)
        
        for person in people_copy:
            available_houses = []
            for i, house in enumerate(assignment):
                if len(house) < self.house_capacities[i]:
                    available_houses.append((len(house), i))
            
            if available_houses:
                available_houses.sort()
                min_people = available_houses[0][0]
                priority_houses = [house_id for people_count, house_id in available_houses if people_count == min_people]
                house_id = random.choice(priority_houses)
                assignment[house_id].append(person)
        
        return assignment
    
    def _local_search(self, assignment):
        """Improve assignment by swapping people between houses"""
        current_assignment = [house.copy() for house in assignment]
        current_score = self._calculate_total_score(current_assignment)
        
        improved = True
        iterations = 0
        max_iterations = 50
        
        while improved and iterations < max_iterations:
            iterations += 1
            improved = False
            best_swap = None
            best_new_score = current_score
            
            # Try all possible swaps
            for i in range(3):
                for j in range(i + 1, 3):
                    if not current_assignment[i] or not current_assignment[j]:
                        continue
                        
                    for person_i in current_assignment[i]:
                        for person_j in current_assignment[j]:
                            # Check if swap is possible
                            if (len(current_assignment[i]) <= self.house_capacities[i] and
                                len(current_assignment[j]) <= self.house_capacities[j]):
                                
                                # Perform swap
                                current_assignment[i].remove(person_i)
                                current_assignment[j].remove(person_j)
                                current_assignment[i].append(person_j)
                                current_assignment[j].append(person_i)
                                
                                new_score = self._calculate_total_score(current_assignment)
                                
                                if new_score > best_new_score:
                                    best_new_score = new_score
                                    best_swap = (i, j, person_i, person_j)
                                
                                # Undo swap
                                current_assignment[i].remove(person_j)
                                current_assignment[j].remove(person_i)
                                current_assignment[i].append(person_i)
                                current_assignment[j].append(person_j)
            
            if best_swap:
                improved = True
                current_score = best_new_score
                i, j, person_i, person_j = best_swap
                current_assignment[i].remove(person_i)
                current_assignment[j].remove(person_j)
                current_assignment[i].append(person_j)
                current_assignment[j].append(person_i)
        
        return current_assignment, current_score
    
    def _calculate_total_score(self, assignment):
        """Calculate total connections across all houses"""
        total_score = 0
        for house_people in assignment:
            total_score += self.calculate_connections_in_house(house_people)
        return total_score

def solve_house_assignment(people_list, house_capacities=None, relationships=None):
    """
    Main function to solve house assignment for Discord bot
    
    Args:
        people_list: List of character names
        house_capacities: Optional house capacities (uses default if None)
        relationships: Optional relationships dict (uses default if None)
    
    Returns:
        tuple: (assignment_result, total_connections)
        assignment_result: List of 3 lists (one for each house)
        total_connections: Total number of relationships satisfied
    """
    solver = HouseAssignmentSolver(house_capacities, relationships)
    assignment, score = solver.optimize_assignment(people_list)
    
    if assignment is None:
        return None, 0
    
    return assignment, score

def format_assignment_result(assignment, total_connections):
    """
    Format assignment result for Discord output
    
    Args:
        assignment: List of 3 lists (houses)
        total_connections: Total connections count
    
    Returns:
        str: Formatted string for Discord message
    """
    if assignment is None:
        return "❌ Không thể tìm được phương án phân bổ phù hợp!"
    
    result_lines = []
    
    for i, house in enumerate(assignment):
        if house:
            result_lines.append(", ".join(house))
        else:
            result_lines.append("(trống)")
    
    result_lines.append(f"Tổng relationships = {total_connections}")
    
    return "\n".join(result_lines)
