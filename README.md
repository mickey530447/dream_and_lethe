# House Assignment Optimization Problem

## Mô tả bài toán

Bài toán phân bổ người vào nhà để tối đa hóa số liên kết:

- **Input**:

  - 3 ngôi nhà với số phòng khác nhau (i, j, k)
  - Tập hợp các mối quan hệ giữa người với người
  - Số người cần chọn và phân bổ

- **Output**:
  - Phân bổ người vào từng nhà sao cho tổng số liên kết trong tất cả các nhà là lớn nhất

## Cấu trúc Input File (JSON)

```json
{
  "description": "Mô tả test case",
  "house_capacities": [3, 5, 5],
  "relationships": {
    "A": ["B", "C", "D"],
    "E": ["A", "C"],
    "D": ["F"]
  },
  "num_people_to_select": 8
}
```

### Giải thích:

- `house_capacities`: Số phòng của từng nhà (3 nhà)
- `relationships`: Mối quan hệ, `"A": ["B", "C"]` có nghĩa là A có liên kết với B và C
- `num_people_to_select`: Số người cần chọn từ tập hợp tất cả người có trong relationships

## Các trường hợp test

### Case 1: [3, 5, 5] - 1 nhà 3 phòng, 2 nhà 5 phòng

- File: `sample_input_1.json`

### Case 2: [3, 3, 3] - Cả 3 nhà đều 3 phòng

- File: `sample_input_2.json`

### Case 3: Phức tạp [4, 6, 3]

- File: `sample_input_3.json`

### Case 4: Test nhỏ [2, 2, 2]

- File: `sample_input_4.json`

## Cách chạy

```bash
# Chạy với tất cả sample
python house_assignment_solver.py

# Hoặc chạy với file cụ thể
python -c "
from house_assignment_solver import load_input_from_file, solve_house_assignment
house_capacities, relationships, num_people = load_input_from_file('sample_input_1.json')
solve_house_assignment(house_capacities, relationships, num_people)
"
```

## Thuật toán

### 1. Greedy Selection

- Chọn những người có nhiều liên kết nhất trước

### 2. Random Assignment + Local Search

- Phân bổ ngẫu nhiên ban đầu
- Cải thiện bằng hoán đổi người giữa các nhà
- Lặp lại nhiều lần để tìm giải pháp tốt nhất

### 3. Performance

- **Time Complexity**: O(iterations × people² × houses²)
- **Space Complexity**: O(people + relationships)
- **Khuyến nghị**: 1000 iterations cho kết quả tốt

## Output Format

```
============================================================
HOUSE ASSIGNMENT OPTIMIZATION
============================================================
Số phòng các nhà: [3, 5, 5]
Tổng số phòng: 13
Số người cần chọn: 8
------------------------------------------------------------

Đã chọn 8 người từ tổng số 9 người:
  A: 3 liên kết với ['B', 'C', 'D']
  E: 2 liên kết với ['A', 'C']
  F: 2 liên kết với ['D', 'G', 'H']
  ...

============================================================
KẾT QUẢ TỐI ƯU
============================================================
Tổng số liên kết đạt được: 4

Phân bổ theo nhà:

Nhà 1 (3 phòng): 3 người
  Người: A, B, C
  Liên kết trong nhà: 2
  Chi tiết: A-B, A-C

Nhà 2 (5 phòng): 3 người
  Người: E, F, D
  Liên kết trong nhà: 2
  Chi tiết: E-A, D-F

Nhà 3 (5 phòng): 2 người
  Người: G, H
  Liên kết trong nhà: 0

Tổng người được phân bổ: 8/8
```

## Tùy chỉnh Input

Để tạo input mới, tạo file JSON theo format:

```json
{
  "description": "Mô tả của bạn",
  "house_capacities": [số_phòng_nhà_1, số_phòng_nhà_2, số_phòng_nhà_3],
  "relationships": {
    "TênNgười1": ["NgườiLiênKết1", "NgườiLiênKết2"],
    "TênNgười2": ["NgườiLiênKết3"]
  },
  "num_people_to_select": số_người_cần_chọn
}
```

**Lưu ý**:

- Mối quan hệ là hai chiều (A-B thì B cũng liên kết với A)
- Số người chọn không được vượt quá tổng số phòng
- Tên người nên là chuỗi không có ký tự đặc biệt
