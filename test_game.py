#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script cho game input
"""

import sys
from house_assignment_solver import load_input_from_file, solve_house_assignment

def test_game_input(filename='game_input.json'):
    try:
        print(f"Loading {filename}...")
        house_capacities, relationships, people_to_select = load_input_from_file(filename)
        
        print("File loaded successfully!")
        print(f"House capacities: {house_capacities}")
        print(f"Number of people in relationships: {len(relationships)}")
        print(f"People to select: {people_to_select}")
        
        print("\nStarting optimization...")
        assignment, score = solve_house_assignment(house_capacities, relationships, people_to_select)
        
        return assignment, score
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None, 0

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = 'game_input.json'
        print("No filename provided, using default: game_input.json")
        print("Usage: python test_game.py <filename>")
    
    test_game_input(filename)
