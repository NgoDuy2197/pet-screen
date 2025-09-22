# config.py - Cấu hình cho Pet Screen
import json
import os

# Các loại pet được hỗ trợ
SUPPORTED_PETS = {
    "cat": {
        "name": "Mèo",
        "animations_path": "assets/animations/cat",
        "default_activity": "idle"
    },
    "dog": {
        "name": "Chó", 
        "animations_path": "assets/animations/dog",
        "default_activity": "idle"
    },
    "bird": {
        "name": "Chim",
        "animations_path": "assets/animations/bird", 
        "default_activity": "fly"
    },
    "rabbit": {
        "name": "Thỏ",
        "animations_path": "assets/animations/rabbit",
        "default_activity": "jump"
    },
    "hamster": {
        "name": "Chuột Hamster",
        "animations_path": "assets/animations/hamster",
        "default_activity": "run"
    }
}

# Các loại hoạt động
ACTIVITIES = {
    'idle': {
        'name': 'Đứng yên',
        'description': 'Pet đứng yên tại chỗ'
    },
    'walk': {
        'name': 'Đi bộ',
        'description': 'Pet đi bộ từ từ trên màn hình',
        'speed': 1
    },
    'run': {
        'name': 'Chạy',
        'description': 'Pet chạy nhanh trên màn hình',
        'speed': 3
    },
    'jump': {
        'name': 'Nhảy',
        'description': 'Pet nhảy lên cao rồi rơi xuống',
        'height': 100
    },
    'fly': {
        'name': 'Bay',
        'description': 'Pet bay lung tung trên màn hình',
        'speed': 0.05
    },
    'climb': {
        'name': 'Leo trèo',
        'description': 'Pet leo lên góc màn hình',
        'speed': 0.1
    },
    'fall': {
        'name': 'Rơi',
        'description': 'Pet rơi từ trên cao xuống',
        'speed': 5
    },
    'die': {
        'name': 'Chết',
        'description': 'Pet chết và dừng mọi hoạt động'
    }
}

# Cài đặt mặc định
DEFAULT_SETTINGS = {
    'pet_type': 'cat',
    'activity_change_interval': (10000, 20000),  # 10-20 giây (tăng từ 5-10 giây)
    'animation_fps': 60,
    'window_flags': 'frameless|topmost|tool',
    'background_transparent': True,
    'speech_interval': (8000, 15000),  # 8-15 giây
    'speech_duration': 3000  # 3 giây hiển thị lời nói
}

# Cài đặt hiển thị
DISPLAY_SETTINGS = {
    'initial_position': (100, 200),
    'screen_margin': 50,
    'min_distance': 10,
    'ground_level': 200,  # Mức mặt đất
    'pet_width': 100,     # Chiều rộng mặc định
    'pet_height': 100     # Chiều cao mặc định
}

# Cài đặt kích thước pet
PET_SIZE_SETTINGS = {
    'min_width': 50,
    'max_width': 200,
    'min_height': 50,
    'max_height': 200,
    'default_width': 100,
    'default_height': 100
}

# Các câu nói mẫu cho pet
PET_SPEECH = {
    'cat': [
        "Meo meo! 😺",
        "Mèo muốn ăn cá! 🐟",
        "Mèo buồn ngủ... 😴",
        "Mèo muốn chơi! 🎾",
        "Meo meo meo! 🐱"
    ],
    'dog': [
        "Gâu gâu! 🐕",
        "Chó muốn đi dạo! 🦴",
        "Chó muốn chơi bóng! ⚽",
        "Gâu gâu gâu! 🐶",
        "Chó muốn ăn xương! 🦴"
    ],
    'bird': [
        "Chíp chíp! 🐦",
        "Chim muốn bay! 🕊️",
        "Chim hót hay! 🎵",
        "Chíp chíp chíp! 🐤",
        "Chim muốn ăn hạt! 🌱"
    ],
    'rabbit': [
        "Thỏ nhảy nhảy! 🐰",
        "Thỏ muốn ăn cà rốt! 🥕",
        "Thỏ muốn chơi! 🥬",
        "Thỏ thỏ thỏ! 🐇",
        "Thỏ muốn ngủ! 😴"
    ],
    'hamster': [
        "Chuột chạy chạy! 🐹",
        "Hamster muốn ăn hạt! 🌰",
        "Hamster muốn chơi! 🎪",
        "Chuột chuột chuột! 🐭",
        "Hamster muốn ngủ! 😴"
    ]
}

# Cài đặt mặc định cho speech
DEFAULT_SPEECH = [
    "Xin chào! 👋",
    "Tôi đang chơi! 🎮",
    "Thật vui! 😊",
    "Tôi muốn chơi! 🎯",
    "Tôi buồn ngủ... 😴",
    "Hôm nay thật đẹp! 🌟",
    "Tôi thích chơi đùa! 🎪",
    "Có ai muốn chơi không? 🤗",
    "Tôi đói rồi! 🍕",
    "Thời tiết thật tuyệt! ☀️",
    "Tôi muốn đi dạo! 🚶‍♂️",
    "Có gì mới không? 🤔",
    "Tôi thích âm nhạc! 🎵",
    "Hãy cùng vui vẻ! 🎉",
    "Tôi yêu cuộc sống! ❤️"
]

class ConfigManager:
    """Quản lý cấu hình và lưu/tải từ file"""
    
    def __init__(self, config_file="pet_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """Tải cấu hình từ file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    print(f"Đã tải cấu hình từ {self.config_file}")
                    return config
            else:
                print(f"File cấu hình {self.config_file} không tồn tại, tạo cấu hình mặc định")
                return self.get_default_config()
        except Exception as e:
            print(f"Lỗi khi tải cấu hình: {e}")
            return self.get_default_config()
    
    def save_config(self):
        """Lưu cấu hình vào file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"Đã lưu cấu hình vào {self.config_file}")
        except Exception as e:
            print(f"Lỗi khi lưu cấu hình: {e}")
    
    def get_default_config(self):
        """Lấy cấu hình mặc định"""
        return {
            'pet_type': 'cat',
            'pet_width': PET_SIZE_SETTINGS['default_width'],
            'pet_height': PET_SIZE_SETTINGS['default_height'],
            'activity_change_interval': DEFAULT_SETTINGS['activity_change_interval'],
            'speech_interval': DEFAULT_SETTINGS['speech_interval'],
            'speech_duration': DEFAULT_SETTINGS['speech_duration'],
            'custom_speeches': DEFAULT_SPEECH,  # Thêm câu nói tùy chỉnh
            'activity_emojis': {  # Emoji cho từng hoạt động
                'idle': '😊',
                'walk': '🚶‍♂️',
                'run': '🏃‍♂️',
                'jump': '🦘',
                'fly': '🕊️',
                'climb': '🧗‍♂️',
                'fall': '😱',
                'die': '💀'
            }
        }
    
    def get(self, key, default=None):
        """Lấy giá trị cấu hình"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Đặt giá trị cấu hình"""
        self.config[key] = value
    
    def update_pet_settings(self, pet_type, width, height):
        """Cập nhật cài đặt pet"""
        self.set('pet_type', pet_type)
        self.set('pet_width', width)
        self.set('pet_height', height)
        self.save_config()
    
    def update_custom_speeches(self, speeches):
        """Cập nhật câu nói tùy chỉnh"""
        self.set('custom_speeches', speeches)
        self.save_config()
    
    def get_custom_speeches(self):
        """Lấy câu nói tùy chỉnh"""
        return self.get('custom_speeches', DEFAULT_SPEECH)
    
    def get_activity_emoji(self, activity):
        """Lấy emoji cho hoạt động"""
        activity_emojis = self.get('activity_emojis', {
            'idle': '😊',
            'walk': '🚶‍♂️',
            'run': '🏃‍♂️',
            'jump': '🦘',
            'fly': '🕊️',
            'climb': '🧗‍♂️',
            'fall': '😱',
            'die': '💀'
        })
        return activity_emojis.get(activity, '😊')
    
    def get_pet_settings(self):
        """Lấy cài đặt pet"""
        return {
            'pet_type': self.get('pet_type', 'cat'),
            'width': self.get('pet_width', PET_SIZE_SETTINGS['default_width']),
            'height': self.get('pet_height', PET_SIZE_SETTINGS['default_height'])
        }
