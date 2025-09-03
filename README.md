# House Assignment Optimization Problem

## Mô tả bài toán

Bài toán phân bổ người vào nhà để tối đa hóa số liên kết:

- **Input**:

  - 3 ngôi nhà với số phòng khác nhau [i, j, k]
  - Tập hợp các mối quan hệ giữa người với người
  - Danh sách người được đề xuất để chọn

- **Output**:
  - Phân bổ người vào từng nhà sao cho tổng số liên kết trong tất cả các nhà là lớn nhất

## Cấu trúc Input File (JSON)

```json
{
  "description": "Mô tả test case",
  "house_capacities": [3, 6, 6],
  "relationships": {
    "Imperial": ["Jingke", "Hanfei", "Han Wu"],
    "Weiqing": ["Qubing", "Han Wu"],
    "Yuhuan": ["Libai", "Longji"]
  },
  "people_to_select": ["Han Wu", "Weiqing", "Qubing", "Imperial"]
}
```

### Giải thích:

- `house_capacities`: Số phòng của từng nhà (3 nhà)
- `relationships`: Mối quan hệ, `"A": ["B", "C"]` có nghĩa là A có liên kết với B và C
- `people_to_select`: Danh sách cụ thể những người được đề xuất để chọn

## Files hiện có

- `game_input_emitiramis.json`: Test case với nhân vật game (mèo characters)
- `house_assignment_solver.py`: Code chính giải bài toán

## Cách chạy

```bash
# Chạy với file mặc định
python house_assignment_solver.py

# Nhập tên file khi được hỏi (enter để dùng game_input_arya.json)
# Hoặc nhập: game_input_emitiramis.json
```

## Thuật toán

### 1. Xử lý người được chọn

- Kiểm tra tất cả người trong `people_to_select` có tồn tại trong `relationships`
- Nếu số người > tổng số phòng, tự động chọn những người có độ ưu tiên cao nhất
- Độ ưu tiên = số liên kết với những người khác trong nhóm được chọn

### 2. Optimization Strategies

- **Fill-first**: Điền đầy nhà đầu tiên trước
- **Balanced**: Phân bổ cân bằng giữa các nhà
- **Local Search**: Cải thiện bằng hoán đổi người giữa các nhà

### 3. Performance

- **Iterations**: 1000 lần mặc định
- **Strategies**: Mix giữa fill-first và balanced
- **Local Search**: Tối đa 100 iterations per solution

## Output Format

```
============================================================
HOUSE ASSIGNMENT OPTIMIZATION
============================================================
Số phòng các nhà: [3, 6, 6]
Tổng số phòng: 15
Người được đề xuất: ['Han Wu', 'Weiqing', 'Qubing', ...]
Số người được đề xuất: 13
------------------------------------------------------------

Kết quả: Đã chọn 13 người từ tổng số 29 người:
  Han Wu: 4 liên kết trong nhóm được chọn với ['Weiqing', 'Shimin', 'Imperial', 'Qubing']
  Weiqing: 2 liên kết trong nhóm được chọn với ['Qubing', 'Han Wu']
  ...

Iteration 156 (balanced): Tìm thấy giải pháp tốt hơn với 8 liên kết

============================================================
KẾT QUẢ PHÂN BỔ CUỐI CÙNG
============================================================
Tổng số liên kết đạt được: 8
------------------------------------------------------------
Nhà 1 (3/3 phòng) - 4 liên kết:
  Han Wu, Weiqing, Qubing

Nhà 2 (6/6 phòng) - 3 liên kết:
  Imperial, Zihuan, Zhen Ji, Dufu, Jikang, Yuhuan

Nhà 3 (4/6 phòng) - 1 liên kết:
  Ruanji, Longji, Xiangyu, Xizhi

============================================================
OUTPUT FORMAT (Copy để sử dụng):
============================================================
Han Wu, Weiqing, Qubing
Imperial, Zihuan, Zhen Ji, Dufu, Jikang, Yuhuan
Ruanji, Longji, Xiangyu, Xizhi
```

## Tạo Input File mới

Để tạo input mới, tạo file JSON theo format:

```json
{
  "description": "Mô tả của bạn",
  "house_capacities": [số_phòng_nhà_1, số_phòng_nhà_2, số_phòng_nhà_3],
  "relationships": {
    "TênNgười1": ["NgườiLiênKết1", "NgườiLiênKết2"],
    "TênNgười2": ["NgườiLiênKết3"]
  },
  "people_to_select": [
    "TênNgười1",
    "TênNgười2",
    "TênNgười3"
  ]
}
```

## Tính năng đặc biệt

### 1. Auto-selection khi quá tải

- Nếu `people_to_select` > tổng số phòng
- Tự động chọn những người có nhiều liên kết nhất trong nhóm

### 2. Validation

- Kiểm tra người trong `people_to_select` có tồn tại trong `relationships`
- Cảnh báo khi có người không hợp lệ

### 3. Strategy mixing

- 1/3 đầu: chỉ dùng fill-first
- 1/3 giữa: chỉ dùng balanced
- 1/3 cuối: mix ngẫu nhiên

### 4. Priority scoring

- Tính điểm ưu tiên cho mỗi người
- Hiển thị chi tiết người được chọn/loại

**Lưu ý**:

- Mối quan hệ là hai chiều (A-B thì B cũng tự động liên kết với A)
- Tên người nên không có ký tự đặc biệt
- File input phải có encoding UTF-8
