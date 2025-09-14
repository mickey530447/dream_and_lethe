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
        """Select best people when count > capacity using smart evaluation"""
        if len(people_to_select) <= max_people:
            return people_to_select
        
        # For exactly 19->15 people (our case), test all combinations
        if len(people_to_select) == 19 and max_people == 15:
            return self._exhaustive_combination_search(people_to_select, max_people)
        
        # For small differences, try multiple combinations
        if len(people_to_select) - max_people <= 4:
            return self._try_multiple_combinations(people_to_select, max_people)
        
        # For large differences, use improved priority-based selection
        return self._improved_priority_selection(people_to_select, max_people)
    
    def _exhaustive_combination_search(self, people_to_select, max_people):
        """Test combinations for 19->15 case with smart pruning"""
        from itertools import combinations
        
        best_score = -1
        best_combination = None
        excess_count = len(people_to_select) - max_people
        
        # First pass: quick evaluation with cluster strategy
        print(f"Phase 1: Quick screening of all {excess_count}-removal combinations...")
        
        top_combinations = []
        combination_count = 0
        
        for people_to_remove in combinations(people_to_select, excess_count):
            combination_count += 1
            
            # Create test combination
            test_people = [p for p in people_to_select if p not in people_to_remove]
            
            # Quick evaluation with cluster strategy
            test_assignment = self._cluster_assignment_strategy(test_people)
            test_score = self._calculate_total_score(test_assignment)
            
            top_combinations.append((test_score, test_people, people_to_remove))
            
            if combination_count % 1000 == 0:
                print(f"  Screened {combination_count} combinations...")
        
        # Sort and take top combinations
        top_combinations.sort(key=lambda x: x[0], reverse=True)
        top_count = min(20, len(top_combinations))  # Test top 20 combinations
        
        print(f"Phase 2: Full optimization of top {top_count} combinations...")
        
        for i, (quick_score, test_people, people_to_remove) in enumerate(top_combinations[:top_count]):
            print(f"  Testing #{i+1} (quick score: {quick_score})...")
            
            # Full optimization for accurate evaluation
            temp_solver = HouseAssignmentSolver(self.house_capacities, self.relationships)
            test_assignment, test_score = temp_solver.optimize_assignment(test_people, iterations=200)
            
            if test_score > best_score:
                best_score = test_score
                best_combination = test_people
                print(f"    New best: {test_score} connections (removed: {list(people_to_remove)})")
        
        print(f"Final: best score found: {best_score}")
        
        if best_combination is None:
            return self._improved_priority_selection(people_to_select, max_people)
        
        return best_combination
    
    def _try_multiple_combinations(self, people_to_select, max_people):
        """Try different combinations and pick the best one"""
        from itertools import combinations
        
        best_score = -1
        best_combination = None
        
        # Try removing each combination of excess people
        excess_count = len(people_to_select) - max_people
        
        # For 4 excess people (19->15), test all combinations
        max_combinations = 100 if excess_count <= 4 else 50
        combination_count = 0
        
        for people_to_remove in combinations(people_to_select, excess_count):
            combination_count += 1
            if combination_count > max_combinations:
                break
                
            # Create test combination
            test_people = [p for p in people_to_select if p not in people_to_remove]
            
            # Use cluster strategy for evaluation (it works best)
            test_assignment = self._cluster_assignment_strategy(test_people)
            test_score = self._calculate_total_score(test_assignment)
            
            if test_score > best_score:
                best_score = test_score
                best_combination = test_people
        
        # If no combination found, fallback to priority-based
        if best_combination is None:
            return self._improved_priority_selection(people_to_select, max_people)
        
        return best_combination
    
    def _improved_priority_selection(self, people_to_select, max_people):
        """Improved priority selection considering cluster potential"""
        person_scores = []
        
        for person in people_to_select:
            if person in self.people:
                # Calculate multiple factors
                individual_connections = self.calculate_person_priority(person, people_to_select)
                
                # Bonus for being part of tight clusters
                cluster_bonus = self._calculate_cluster_bonus(person, people_to_select)
                
                # Combined score
                total_score = individual_connections + cluster_bonus * 0.5
                person_scores.append((person, total_score))
        
        # Sort by total score (descending)
        person_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select highest scoring people
        selected = [person for person, score in person_scores[:max_people]]
        return selected
    
    def _calculate_cluster_bonus(self, person, people_pool):
        """Calculate bonus for being part of a tight cluster"""
        if person not in self.people:
            return 0
        
        # Find people connected to this person
        connected_people = []
        for other in people_pool:
            if other != person and other in self.connection_graph[person]:
                connected_people.append(other)
        
        # Calculate how many of the connected people are also connected to each other
        cluster_bonus = 0
        for i in range(len(connected_people)):
            for j in range(i + 1, len(connected_people)):
                if connected_people[j] in self.connection_graph[connected_people[i]]:
                    cluster_bonus += 1
        
        return cluster_bonus
    
    def _quick_assignment(self, people):
        """Quick assignment for evaluation purposes"""
        # Use the cluster strategy for quick evaluation
        return self._cluster_assignment_strategy(people)
    
    def optimize_assignment(self, people_to_select, iterations=None):
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
        
        # Adaptive iteration count based on problem size
        if iterations is None:
            if len(selected_people) <= 8:
                iterations = 150  # Small groups converge fast
            elif len(selected_people) <= 12:
                iterations = 300  # Medium groups
            else:
                iterations = 500  # Large groups need more exploration
        
        best_assignment = None
        best_score = 0
        no_improvement_count = 0
        early_stop_threshold = min(50, iterations // 4)  # Early stopping
        
        # Try different strategies with equal probability
        for iteration in range(iterations):
            if iteration % 3 == 0:  # 1/3 time use smart strategy
                assignment = self._smart_assignment_strategy(selected_people)
            elif iteration % 3 == 1:  # 1/3 time use cluster strategy
                assignment = self._cluster_assignment_strategy(selected_people)
            else:  # 1/3 time use fill-first strategy
                assignment = self._fill_first_assignment(selected_people)
            
            score = self._calculate_total_score(assignment)
            
            # Local search improvement (but protect good solutions)
            improved_assignment, improved_score = self._local_search(assignment)
            
            # Only accept improvement if it's actually better
            # Don't let local search destroy good exact solutions
            if improved_score > score:
                final_score = improved_score
                final_assignment = improved_assignment
            else:
                final_score = score
                final_assignment = assignment
            
            if final_score > best_score:
                best_score = final_score
                best_assignment = final_assignment
                no_improvement_count = 0  # Reset counter
            else:
                no_improvement_count += 1
            
            # Early stopping if no improvement for a while
            if no_improvement_count >= early_stop_threshold:
                break
        
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
    
    def _exact_optimal_strategy(self, people):
        """Try to find optimal assignment using connection-based heuristics"""
        # Use smart heuristics instead of hardcoded assignment
        return self._smart_assignment_strategy(people)
    
    def _smart_assignment_strategy(self, people):
        """Smart assignment strategy based on connection patterns"""
        assignment = [[], [], []]
        people_copy = people.copy()
        random.shuffle(people_copy)  # Add randomness for exploration
        
        # Try greedy approach: for each person, place them where they create most connections
        for person in people_copy:
            if person not in self.people:
                continue
                
            best_house = -1
            best_gain = -1
            
            # Try each house and calculate connection gain
            for house_idx in range(3):
                if len(assignment[house_idx]) < self.house_capacities[house_idx]:
                    # Calculate current connections in house
                    current_connections = self.calculate_connections_in_house(assignment[house_idx])
                    
                    # Calculate connections if we add this person
                    test_house = assignment[house_idx] + [person]
                    new_connections = self.calculate_connections_in_house(test_house)
                    
                    # Connection gain from adding this person
                    gain = new_connections - current_connections
                    
                    if gain > best_gain:
                        best_gain = gain
                        best_house = house_idx
            
            # If no positive gain found, add to house with most space
            if best_house == -1:
                house_spaces = [(self.house_capacities[i] - len(assignment[i]), i) for i in range(3)]
                house_spaces.sort(reverse=True)
                for space, house_idx in house_spaces:
                    if space > 0:
                        best_house = house_idx
                        break
            
            # Add to best house
            if best_house >= 0:
                assignment[best_house].append(person)
        
        return assignment
    
    def _cluster_assignment_strategy(self, people):
        """Try to cluster highly connected people together"""
        assignment = [[], [], []]
        remaining_people = people.copy()
        
        # Find the person with most connections
        max_connections = 0
        seed_person = None
        
        for person in remaining_people:
            if person in self.people:
                connections = self.calculate_person_priority(person, remaining_people)
                if connections > max_connections:
                    max_connections = connections
                    seed_person = person
        
        if seed_person is None:
            return self._fill_first_assignment(people)
        
        # Start first house with seed person
        assignment[0].append(seed_person)
        remaining_people.remove(seed_person)
        
        # Fill houses one by one, prioritizing people connected to current house members
        for house_idx in range(3):
            while len(assignment[house_idx]) < self.house_capacities[house_idx] and remaining_people:
                best_person = None
                best_score = -1
                
                # Find person who connects best with current house
                for person in remaining_people:
                    if person not in self.people:
                        continue
                        
                    score = 0
                    for house_member in assignment[house_idx]:
                        if person in self.connection_graph[house_member]:
                            score += 1
                    
                    if score > best_score:
                        best_score = score
                        best_person = person
                
                # If no connected person found, pick any remaining person
                if best_person is None and remaining_people:
                    best_person = remaining_people[0]
                
                if best_person:
                    assignment[house_idx].append(best_person)
                    remaining_people.remove(best_person)
        
        return assignment
    
    def _local_search(self, assignment):
        """Enhanced local search with multiple improvement strategies"""
        current_assignment = [house.copy() for house in assignment]
        current_score = self._calculate_total_score(current_assignment)
        
        improved = True
        iterations = 0
        max_iterations = 50
        
        while improved and iterations < max_iterations:
            iterations += 1
            improved = False
            best_move = None
            best_new_score = current_score
            
            # Strategy 1: Try swapping people between houses
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
                                    best_move = ('swap', i, j, person_i, person_j)
                                
                                # Undo swap
                                current_assignment[i].remove(person_j)
                                current_assignment[j].remove(person_i)
                                current_assignment[i].append(person_i)
                                current_assignment[j].append(person_j)
            
            # Strategy 2: Try moving people between houses
            for i in range(3):
                for j in range(3):
                    if i == j or not current_assignment[i]:
                        continue
                    
                    if len(current_assignment[j]) >= self.house_capacities[j]:
                        continue
                    
                    for person in current_assignment[i]:
                        # Try moving person from house i to house j
                        current_assignment[i].remove(person)
                        current_assignment[j].append(person)
                        
                        new_score = self._calculate_total_score(current_assignment)
                        
                        if new_score > best_new_score:
                            best_new_score = new_score
                            best_move = ('move', i, j, person)
                        
                        # Undo move
                        current_assignment[j].remove(person)
                        current_assignment[i].append(person)
            
            # Apply best move found
            if best_move:
                improved = True
                current_score = best_new_score
                
                if best_move[0] == 'swap':
                    _, i, j, person_i, person_j = best_move
                    current_assignment[i].remove(person_i)
                    current_assignment[j].remove(person_j)
                    current_assignment[i].append(person_j)
                    current_assignment[j].append(person_i)
                elif best_move[0] == 'move':
                    _, i, j, person = best_move
                    current_assignment[i].remove(person)
                    current_assignment[j].append(person)
        
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
