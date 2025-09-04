#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
House Assignment Optimization Problem Solver
Giải bài toán phân bổ người vào nhà để tối đa hóa số liên kết

Bài toán:
- Có 3 nhà với số phòng khác nhau
- Mỗi người có các mối liên kết với người khác
- Cần phân bổ người vào nhà sao cho tổng số liên kết trong từng nhà là lớn nhất
"""

import random
from collections import defaultdict
from itertools import combinations
import json

class HouseAssignmentOptimizer:
    def __init__(self, house_capacities, relationships):
        """
        Initialize optimizer
        
        Args:
            house_capacities: List[int] - số phòng của từng nhà [i, j, k]
            relationships: Dict[str, List[str]] - mối quan hệ {person: [connections]}
        """
        self.house_capacities = house_capacities
        self.relationships = relationships
        self.people = set()
        self.connection_graph = defaultdict(set)
        
        # Build bidirectional connection graph
        for person, connections in relationships.items():
            self.people.add(person)
            for conn in connections:
                self.people.add(conn)
                self.connection_graph[person].add(conn)
                self.connection_graph[conn].add(person)
    
    def calculate_connections_in_house(self, people_in_house):
        """Tính tổng số liên kết trong một nhà"""
        connections = 0
        people_list = list(people_in_house)
        for i in range(len(people_list)):
            for j in range(i + 1, len(people_list)):
                if people_list[j] in self.connection_graph[people_list[i]]:
                    connections += 1
        return connections
    
    def calculate_person_priority(self, person, people_pool):
        """Tính độ ưu tiên của một người dựa trên số liên kết trong pool"""
        connections_in_pool = 0
        for other in people_pool:
            if other != person and other in self.connection_graph[person]:
                connections_in_pool += 1
        return connections_in_pool
    
    def select_best_people(self, people_to_select, max_people):
        """Chọn những người tốt nhất khi số người > số phòng"""
        if len(people_to_select) <= max_people:
            return people_to_select
        
        print(f"Cần chọn {max_people} người từ {len(people_to_select)} người được đề xuất...")
        
        # Tính độ ưu tiên cho mỗi người
        person_scores = []
        for person in people_to_select:
            if person in self.people:
                priority = self.calculate_person_priority(person, people_to_select)
                person_scores.append((person, priority))
            else:
                print(f"Cảnh báo: Người '{person}' không tồn tại trong relationships")
        
        # Sắp xếp theo độ ưu tiên giảm dần
        person_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Chọn những người có độ ưu tiên cao nhất
        selected = [person for person, score in person_scores[:max_people]]
        
        print("Danh sách người được chọn (theo độ ưu tiên):")
        for i, (person, score) in enumerate(person_scores[:max_people]):
            print(f"  {i+1}. {person}: {score} liên kết")
        
        if len(person_scores) > max_people:
            print(f"\nNhững người bị loại ({len(person_scores) - max_people} người):")
            for person, score in person_scores[max_people:]:
                print(f"  - {person}: {score} liên kết")
        
        return selected
    
    def greedy_optimize(self, people_to_select, iterations=1000):
        """Fast greedy optimization with local search"""
        max_people = sum(self.house_capacities)
        
        # Xử lý trường hợp quá nhiều người
        if len(people_to_select) > max_people:
            print(f"CẢNH BÁO: Số người được chọn ({len(people_to_select)}) > Tổng số phòng ({max_people})")
            selected_people = self.select_best_people(people_to_select, max_people)
        else:
            # Kiểm tra tất cả người được chọn có tồn tại không
            selected_people = []
            for person in people_to_select:
                if person in self.people:
                    selected_people.append(person)
                else:
                    print(f"Cảnh báo: Người '{person}' không tồn tại trong relationships")
        
        if not selected_people:
            print("Không có người nào hợp lệ để chọn!")
            return None, 0
        
        print(f"\nKết quả: Đã chọn {len(selected_people)} người từ tổng số {len(self.people)} người:")
        for person in selected_people:
            connections = list(self.connection_graph[person])
            connections_in_selected = [c for c in connections if c in selected_people]
            score = len(connections_in_selected)
            print(f"  {person}: {score} liên kết trong nhóm được chọn với {connections_in_selected}")
        
        best_assignment = None
        best_score = 0
        
        # Thử cả hai chiến lược: fill-first và balanced
        strategies = ['fill_first', 'balanced']
        
        for iteration in range(iterations):
            # Chọn strategy
            if iteration < iterations // 3:
                # 1/3 đầu: chỉ dùng fill-first
                strategy = 'fill_first'
            elif iteration < 2 * iterations // 3:
                # 1/3 giữa: chỉ dùng balanced  
                strategy = 'balanced'
            else:
                # 1/3 cuối: mix ngẫu nhiên
                strategy = random.choice(strategies)
            
            if strategy == 'fill_first':
                assignment = self._fill_first_assignment(selected_people)
            else:
                assignment = self._random_assignment(selected_people)
            
            score = self._calculate_total_score(assignment)
            
            # Local search improvement
            improved_assignment, improved_score = self._local_search(assignment)
            
            if improved_score > best_score:
                best_score = improved_score
                best_assignment = improved_assignment
                print(f"Iteration {iteration} ({strategy}): Tìm thấy giải pháp tốt hơn với {best_score} liên kết")
        
        return best_assignment, best_score
    
    def _fill_first_assignment(self, people):
        """Phân bổ theo nguyên tắc fill đầy nhà đầu tiên trước"""
        assignment = [[], [], []]
        people_copy = people.copy()
        random.shuffle(people_copy)
        
        current_house = 0  # Bắt đầu từ nhà đầu tiên
        
        for person in people_copy:
            # Tìm nhà hiện tại có thể nhận thêm người
            while current_house < 3:
                if len(assignment[current_house]) < self.house_capacities[current_house]:
                    assignment[current_house].append(person)
                    break
                else:
                    # Nhà hiện tại đã đầy, chuyển sang nhà tiếp theo
                    current_house += 1
            else:
                # Tất cả nhà đều đầy, không thể phân bổ thêm
                print(f"Cảnh báo: Không thể phân bổ {person} - tất cả nhà đã đầy")
                break
        
        return assignment
    
    def _random_assignment(self, people):
        """Phân bổ người vào nhà với ưu tiên fill đầy từng nhà"""
        assignment = [[], [], []]
        people_copy = people.copy()
        random.shuffle(people_copy)
        
        for person in people_copy:
            # Ưu tiên các nhà có ít người nhất (để fill đầy)
            available_houses = []
            for i, house in enumerate(assignment):
                if len(house) < self.house_capacities[i]:
                    available_houses.append((len(house), i))
            
            if available_houses:
                # Sắp xếp theo số người hiện tại (tăng dần) để ưu tiên nhà có ít người
                available_houses.sort()
                
                # Ưu tiên các nhà có ít người nhất
                min_people = available_houses[0][0]
                priority_houses = [house_id for people_count, house_id in available_houses if people_count == min_people]
                
                # Nếu có nhiều nhà cùng mức độ ưu tiên, chọn ngẫu nhiên
                house_id = random.choice(priority_houses)
                assignment[house_id].append(person)
        
        return assignment
    
    def _local_search(self, assignment):
        """Cải thiện phân bổ bằng cách hoán đổi người giữa các nhà"""
        current_assignment = [house.copy() for house in assignment]
        current_score = self._calculate_total_score(current_assignment)
        
        improved = True
        iterations = 0
        max_iterations = 100  # Tránh vòng lặp vô hạn
        
        while improved and iterations < max_iterations:
            iterations += 1
            improved = False
            best_swap = None
            best_new_score = current_score
            
            # Thử tất cả các hoán đổi có thể
            for i in range(3):
                for j in range(i + 1, 3):
                    if not current_assignment[i] or not current_assignment[j]:
                        continue
                        
                    for person_i in current_assignment[i]:
                        for person_j in current_assignment[j]:
                            # Kiểm tra xem có thể hoán đổi không
                            if (len(current_assignment[i]) <= self.house_capacities[i] and
                                len(current_assignment[j]) <= self.house_capacities[j]):
                                
                                # Thực hiện hoán đổi
                                current_assignment[i].remove(person_i)
                                current_assignment[j].remove(person_j)
                                current_assignment[i].append(person_j)
                                current_assignment[j].append(person_i)
                                
                                new_score = self._calculate_total_score(current_assignment)
                                
                                if new_score > best_new_score:
                                    best_new_score = new_score
                                    best_swap = (i, j, person_i, person_j)
                                
                                # Hoàn tác hoán đổi
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
        """Tính tổng số liên kết trong tất cả các nhà"""
        total_score = 0
        for house_people in assignment:
            total_score += self.calculate_connections_in_house(house_people)
        return total_score

def load_input_from_file(filename):
    """Đọc input từ file JSON"""
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['house_capacities'], data['relationships'], data['people_to_select']

def solve_house_assignment(house_capacities, relationships, people_to_select):
    """Giải bài toán phân bổ nhà"""
    print("="*60)
    print("HOUSE ASSIGNMENT OPTIMIZATION")
    print("="*60)
    print(f"Số phòng các nhà: {house_capacities}")
    print(f"Tổng số phòng: {sum(house_capacities)}")
    print(f"Người được đề xuất: {people_to_select}")
    print(f"Số người được đề xuất: {len(people_to_select)}")
    
    total_capacity = sum(house_capacities)
    if len(people_to_select) > total_capacity:
        print(f"⚠️  SỐ NGƯỜI VƯỢT QUÁ SỨC CHỨA: {len(people_to_select)} > {total_capacity}")
        print("Hệ thống sẽ tự động chọn những người có độ ưu tiên cao nhất...")
    
    print("-"*60)
    
    optimizer = HouseAssignmentOptimizer(house_capacities, relationships)
    assignment, max_score = optimizer.greedy_optimize(people_to_select)
    
    if assignment is None:
        print("KHÔNG THỂ GIẢI: Lỗi trong quá trình tối ưu hóa!")
        return None, 0
    
    # Detailed output
    print(f"\n{'='*60}")
    print("KẾT QUẢ PHÂN BỔ CUỐI CÙNG")
    print(f"{'='*60}")
    print(f"Tổng số liên kết đạt được: {max_score}")
    print("-"*60)
    
    for i, house in enumerate(assignment):
        house_connections = optimizer.calculate_connections_in_house(house) if house else 0
        print(f"Nhà {i+1} ({len(house)}/{house_capacities[i]} phòng) - {house_connections} liên kết:")
        if house:
            print(f"  {', '.join(house)}")
        else:
            print("  (trống)")
    
    print(f"\n{'='*60}")
    print("OUTPUT FORMAT (Copy để sử dụng):")
    print(f"{'='*60}")
    
    # Simple output format
    for i, house in enumerate(assignment):
        if house:
            print(', '.join(house))
        else:
            print("")
    
    return assignment, max_score

def create_sample_inputs():
    """Tạo các file input mẫu"""
    
    # Sample 1: Trường hợp đơn giản - Case 1: [3, 5, 5]
    sample1 = {
        "description": "Trường hợp đơn giản - 1 nhà 3 phòng, 2 nhà 5 phòng",
        "house_capacities": [3, 5, 5],
        "relationships": {
            "A": ["B", "C", "D"],      # A liên kết với B,C,D (3 liên kết)
            "E": ["A", "C"],           # E liên kết với A,C (2 liên kết)  
            "D": ["F"],                # D liên kết với F (1 liên kết)
            "B": ["G"],                # B liên kết với G (1 liên kết)
            "F": ["G", "H"],           # F liên kết với G,H (2 liên kết)
            "H": ["I"]                 # H liên kết với I (1 liên kết)
        },
        "people_to_select": ["A", "B", "C", "D", "E", "F", "G", "H"]
    }
    
    # Sample 2: Trường hợp Case 2 - [3, 3, 3]
    sample2 = {
        "description": "Cả 3 nhà đều có 3 phòng",
        "house_capacities": [3, 3, 3],
        "relationships": {
            "Alice": ["Bob", "Charlie", "David"],
            "Bob": ["Alice", "Eve", "Frank"],
            "Charlie": ["Alice", "Grace", "Henry"],
            "David": ["Alice", "Ivan"],
            "Eve": ["Bob", "Jack"],
            "Frank": ["Bob", "Grace"],
            "Grace": ["Charlie", "Frank", "Henry"],
            "Henry": ["Charlie", "Grace"],
            "Ivan": ["David", "Jack"],
            "Jack": ["Eve", "Ivan", "Kate"],
            "Kate": ["Jack", "Liam"],
            "Liam": ["Kate"]
        },
        "people_to_select": ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Henry", "Ivan"]
    }
    
    # Sample 3: Trường hợp phức tạp
    sample3 = {
        "description": "Trường hợp phức tạp với nhiều người và liên kết",
        "house_capacities": [4, 6, 3],
        "relationships": {
            "P1": ["P2", "P3", "P4", "P5"],
            "P2": ["P1", "P6", "P7"],
            "P3": ["P1", "P8", "P9"],
            "P4": ["P1", "P10"],
            "P5": ["P1", "P11", "P12"],
            "P6": ["P2", "P13"],
            "P7": ["P2", "P14", "P15"],
            "P8": ["P3", "P16"],
            "P9": ["P3", "P17"],
            "P10": ["P4", "P18"],
            "P11": ["P5", "P19"],
            "P12": ["P5", "P20"],
            "P13": ["P6"],
            "P14": ["P7"],
            "P15": ["P7"],
            "P16": ["P8"],
            "P17": ["P9"],
            "P18": ["P10"],
            "P19": ["P11"],
            "P20": ["P12"]
        },
        "people_to_select": ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10", "P11", "P12", "P13"]
    }
    
    # Sample 4: Test case với ít người
    sample4 = {
        "description": "Test case nhỏ để kiểm tra tính đúng đắn",
        "house_capacities": [2, 2, 2],
        "relationships": {
            "X": ["Y", "Z"],
            "Y": ["X", "W"],
            "Z": ["X"],
            "W": ["Y"]
        },
        "people_to_select": ["X", "Y", "Z", "W"]
    }
    
    # Lưu các file mẫu
    samples = [sample1, sample2, sample3, sample4]
    filenames = []
    
    for i, sample in enumerate(samples, 1):
        filename = f"sample_input_{i}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(sample, f, ensure_ascii=False, indent=2)
        filenames.append(filename)
        print(f"Đã tạo file: {filename}")
        print(f"  Mô tả: {sample['description']}")
    
    return filenames

if __name__ == "__main__":
    custom_file = input("Nhập tên file (mặc định: game_input_arya.json): ").strip()
    if not custom_file:
        custom_file = "game_input_arya.json"
    
    try:
        house_capacities, relationships, people_to_select = load_input_from_file(custom_file)
        assignment, score = solve_house_assignment(house_capacities, relationships, people_to_select)
    except Exception as ex:
        print(f"Lỗi khi xử lý file: {ex}")
