# Dream & Lethe Discord Bot

Discord bot để xếp character vào nhà tối ưu dựa trên relationships.

## Tính năng

### Commands Cơ Bản:

- `/add [character]` - Thêm character vào danh sách cá nhân
- `/remove [character]` - Xóa character khỏi danh sách
- `/check` - Xem danh sách character của bạn
- `/gen` - Tạo lệnh /rela từ danh sách của bạn
- `/clear` - Xóa toàn bộ danh sách
- `/rela characters: [names]` - Xếp nhà (format: `Han Wu, Libai, Imperial`)

### Cách Dùng Nhanh:

1. **Thêm characters:** `/add Han Wu` rồi `/add Libai` rồi `/add Imperial`
2. **Kiểm tra:** `/check` để xem danh sách
3. **Tạo lệnh:** `/gen` để copy lệnh /rela được tạo sẵn
4. **Xếp nhà:** Paste lệnh vừa copy

### Lưu ý:

- Autocomplete sẽ gợi ý characters khi gõ
- `/add` chỉ hiện characters chưa có trong list
- `/remove` chỉ hiện characters đã có trong list
- Bot xếp nhà tự động theo relationships tối ưu

Chỉ cần 4 bước: Add → Check → Gen → Rela

## Cấu trúc thư mục

```
dream_lethe_bot/
├── src/                    # Source code
│   ├── botdiscord.py      # Bot chính
│   ├── solver.py          # Thuật toán xếp nhà
│   └── user_manager.py    # Quản lý dữ liệu user
├── constants/             # Dữ liệu constants
│   └── bot_constants.py   # Characters và relationships
├── user_data/            # Dữ liệu user cá nhân
├── data/                 # File input test
└── .env                  # Discord token
```

## Cài đặt và chạy

1. **Cài đặt dependencies:**

```bash
pip install discord.py python-dotenv
```

2. **Tạo file .env:**

```
DISCORD_TOKEN=your_discord_bot_token
```

3. **Chạy bot:**

```bash
cd src
python botdiscord.py
```

## Thuật toán xếp nhà

Bot sử dụng thuật toán optimization để:

- Tối đa hóa số relationships trong cùng nhà
- Phân bổ đều characters vào các nhà
- Sử dụng local search để cải thiện kết quả

### Input Format (JSON):

```json
{
  "house_capacities": [3, 6, 6],
  "relationships": {
    "Imperial": ["Jingke", "Hanfei", "Han Wu"],
    "Weiqing": ["Qubing", "Han Wu"]
  }
}
```

### Output Format:

```
🏠 Cách xếp mèo:
Han Wu, Imperial, Jingke
Weiqing, Qubing, Hanfei
(trống)
Tổng relationships = 4
```

## Files test

Các file input có sẵn trong thư mục `data/`:

- `game_input_emitiramis.json` - Dữ liệu characters game chính
- `sample_input_*.json` - Các test case khác

## Development

### House Assignment Solver

File `house_assignment_solver.py` chứa thuật toán optimization gốc có thể chạy standalone:

```bash
python house_assignment_solver.py
```

### Testing

```bash
python test_game.py
```

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
```
