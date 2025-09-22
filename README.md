# Pet Screen Demo

Ứng dụng Pet Screen Demo cho phép bạn tạo và điều khiển các con vật ảo trên màn hình máy tính.

## Tính năng

### 🐱 Đa dạng loại Pet
- **Mèo**: Hoạt động mặc định là đứng yên
- **Chó**: Hoạt động mặc định là đứng yên  
- **Chim**: Hoạt động mặc định là bay
- **Thỏ**: Hoạt động mặc định là nhảy
- **Chuột Hamster**: Hoạt động mặc định là chạy

### 🎮 Các hoạt động
- **Đứng yên**: Pet đứng yên tại chỗ
- **Đi bộ**: Pet đi bộ từ từ trên màn hình
- **Chạy**: Pet chạy nhanh trên màn hình
- **Nhảy**: Pet nhảy lên cao rồi rơi xuống
- **Bay**: Pet bay lung tung trên màn hình
- **Leo trèo**: Pet leo lên góc màn hình
- **Rơi**: Pet rơi từ trên cao xuống
- **Chết**: Pet chết và dừng mọi hoạt động

### 🎨 Tính năng mới
- **Tự động tạo thư mục**: Khi chọn loại pet mới, hệ thống tự động tạo thư mục và copy ảnh từ thư mục "cat"
- **Thay đổi hành động ngẫu nhiên**: Pet tự động thay đổi hành động trong khoảng 5-10 giây
- **Cài đặt kích thước**: Có thể điều chỉnh độ rộng và chiều cao của pet (50-200px)
- **Hiệu ứng nói**: Pet sẽ nói những câu ngẫu nhiên với bong bóng nói
- **Xử lý lỗi**: Tất cả các chức năng đều có try-catch để tránh ứng dụng bị treo
- **Vị trí cố định**: Pet luôn ở trên mặt đất khi đi lại, không bị lơ lửng

## Cài đặt

### Yêu cầu hệ thống
- Python 3.6+
- PyQt5

### Cài đặt dependencies
```bash
pip install PyQt5
```

## Sử dụng

### Chạy ứng dụng
```bash
python demo.py
```

### Hướng dẫn sử dụng

1. **Chọn loại Pet**: Sử dụng dropdown để chọn loại pet mong muốn
2. **Điều chỉnh kích thước**: Sử dụng slider để thay đổi chiều rộng và chiều cao
3. **Tạo Pet**: Nhấn nút "Tạo Pet" để tạo pet mới
4. **Điều khiển**: Sử dụng nút "Ẩn Pet" và "Hiện Pet" để điều khiển hiển thị

### Cấu trúc thư mục
```
pet_screen_2/
├── assets/
│   └── animations/
│       ├── cat/          # Ảnh mèo (có sẵn)
│       ├── dog/          # Tự động tạo và copy từ cat
│       ├── bird/         # Tự động tạo và copy từ cat
│       ├── rabbit/       # Tự động tạo và copy từ cat
│       └── hamster/      # Tự động tạo và copy từ cat
├── config.py             # Cấu hình ứng dụng
├── pet_python.py         # Class Pet chính
├── demo.py               # Giao diện demo
└── README.md             # Hướng dẫn này
```

## Cấu hình

### Thêm loại pet mới
Chỉnh sửa file `config.py`:

```python
SUPPORTED_PETS = {
    "your_pet": {
        "name": "Tên Pet",
        "animations_path": "assets/animations/your_pet",
        "default_activity": "idle"
    }
}
```

### Thêm câu nói mới
```python
PET_SPEECH = {
    'your_pet': [
        "Câu nói 1! 😊",
        "Câu nói 2! 🎉",
        "Câu nói 3! 🌟"
    ]
}
```

### Điều chỉnh thời gian
```python
DEFAULT_SETTINGS = {
    'activity_change_interval': (5000, 10000),  # 5-10 giây
    'speech_interval': (8000, 15000),           # 8-15 giây
    'speech_duration': 3000                     # 3 giây hiển thị lời nói
}
```

## Tính năng kỹ thuật

### Xử lý lỗi
- Tất cả các hàm đều có try-catch để tránh crash
- Log lỗi chi tiết trong console
- Fallback cho các trường hợp thiếu file

### Hiệu suất
- Animation mượt mà với 60fps
- Tự động dọn dẹp tài nguyên
- Quản lý bộ nhớ hiệu quả

### Tương thích
- Hỗ trợ Windows, macOS, Linux
- Tự động phát hiện độ phân giải màn hình
- Responsive design

## Troubleshooting

### Pet không hiển thị
- Kiểm tra thư mục `assets/animations/` có tồn tại không
- Đảm bảo có file GIF trong thư mục tương ứng
- Kiểm tra console để xem lỗi

### Ứng dụng bị treo
- Tất cả lỗi đã được xử lý với try-catch
- Kiểm tra log trong console
- Restart ứng dụng nếu cần

### Pet không di chuyển
- Kiểm tra file animation có đúng format không
- Đảm bảo tên file bắt đầu với tên hoạt động (ví dụ: `walk_1.gif`)

## Đóng góp

Để đóng góp vào dự án:
1. Fork repository
2. Tạo branch mới cho tính năng
3. Commit thay đổi
4. Tạo Pull Request

## License

Dự án này được phát hành dưới MIT License.
