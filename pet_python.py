# pet_python_gif.py
import sys
import os
import random
import math
import shutil
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel as QLabelWidget
from PyQt5.QtGui import QMovie, QFont, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, QPoint, QSize
from config import SUPPORTED_PETS, ACTIVITIES, DEFAULT_SETTINGS, DISPLAY_SETTINGS, PET_SIZE_SETTINGS, PET_SPEECH, DEFAULT_SPEECH

class SpeechBubble(QWidget):
    """Widget hiển thị bong bóng nói"""
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.text = text
        self.setFixedSize(200, 60)
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #333;
                border-radius: 10px;
                color: #333;
            }
        """)
        
        layout = QVBoxLayout()
        label = QLabelWidget(text)
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        label.setStyleSheet("font-size: 12px; font-weight: bold;")
        layout.addWidget(label)
        self.setLayout(layout)

class AnimationManager:
    def __init__(self, pet_type="cat"):
        self.pet_type = pet_type
        if pet_type in SUPPORTED_PETS:
            self.animations_path = SUPPORTED_PETS[pet_type]["animations_path"]
        else:
            self.animations_path = f"assets/animations/{pet_type}"
        
        # Tự động tạo thư mục và copy ảnh nếu cần
        self.ensure_animations_exist()
        
        self.animations = {}
        self.load_animations()
    
    def ensure_animations_exist(self):
        """Đảm bảo thư mục animation tồn tại và có ảnh"""
        try:
            # Tạo thư mục nếu chưa tồn tại
            if not os.path.exists(self.animations_path):
                os.makedirs(self.animations_path, exist_ok=True)
                print(f"Đã tạo thư mục: {self.animations_path}")
            
            # Kiểm tra xem thư mục có ảnh không
            if os.path.exists(self.animations_path):
                files = os.listdir(self.animations_path)
                gif_files = [f for f in files if f.endswith('.gif')]
                
                # Nếu không có ảnh, copy từ thư mục cat
                if not gif_files and self.pet_type != "cat":
                    cat_path = "assets/animations/cat"
                    if os.path.exists(cat_path):
                        for file in os.listdir(cat_path):
                            if file.endswith('.gif'):
                                src = os.path.join(cat_path, file)
                                dst = os.path.join(self.animations_path, file)
                                shutil.copy2(src, dst)
                                print(f"Đã copy: {file} -> {self.animations_path}")
        except Exception as e:
            print(f"Lỗi khi tạo thư mục animation: {e}")
    
    def load_animations(self):
        """Load tất cả animation từ thư mục"""
        try:
            if not os.path.exists(self.animations_path):
                print(f"Thư mục {self.animations_path} không tồn tại!")
                return
            
            animation_types = list(ACTIVITIES.keys())
            
            for anim_type in animation_types:
                self.animations[anim_type] = []
                # Tìm tất cả file bắt đầu với tên animation
                for file in os.listdir(self.animations_path):
                    if file.startswith(f"{anim_type}_") and file.endswith('.gif'):
                        self.animations[anim_type].append(os.path.join(self.animations_path, file))
        except Exception as e:
            print(f"Lỗi khi load animations: {e}")
    
    def get_random_animation(self, anim_type):
        """Lấy ngẫu nhiên một animation của loại được chỉ định"""
        try:
            if anim_type in self.animations and self.animations[anim_type]:
                return random.choice(self.animations[anim_type])
            
            # Nếu không tìm thấy animation cho loại này, thử tìm file có tên tương ứng
            if os.path.exists(self.animations_path):
                for file in os.listdir(self.animations_path):
                    if file.startswith(f"{anim_type}_") and file.endswith('.gif'):
                        file_path = os.path.join(self.animations_path, file)
                        if anim_type not in self.animations:
                            self.animations[anim_type] = []
                        self.animations[anim_type].append(file_path)
                        return file_path
            
            return None
        except Exception as e:
            print(f"Lỗi khi lấy animation: {e}")
            return None

class SpeechManager:
    """Quản lý hiệu ứng nói của pet"""
    def __init__(self, pet):
        self.pet = pet
        self.speech_bubble = None
        self.speech_timer = QTimer()
        self.speech_timer.timeout.connect(self.show_random_speech)
        self.speech_duration_timer = QTimer()
        self.speech_duration_timer.timeout.connect(self.hide_speech)
        self.start_speech_timer()
    
    def start_speech_timer(self):
        """Bắt đầu timer cho hiệu ứng nói"""
        try:
            min_interval, max_interval = DEFAULT_SETTINGS['speech_interval']
            interval = random.randint(min_interval, max_interval)
            self.speech_timer.start(interval)
        except Exception as e:
            print(f"Lỗi khi bắt đầu speech timer: {e}")
    
    def show_speech_immediately(self, speech_text):
        """Hiển thị bong bóng nói ngay lập tức"""
        try:
            # Tạo bong bóng nói
            if self.speech_bubble:
                self.speech_bubble.close()
            
            self.speech_bubble = SpeechBubble(speech_text)
            self.speech_bubble.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
            self.speech_bubble.setAttribute(Qt.WA_TranslucentBackground, True)
            
            # Đặt vị trí bong bóng nói
            bubble_x = int(self.pet.x + self.pet.width() // 2 - self.speech_bubble.width() // 2)
            bubble_y = int(self.pet.y - self.speech_bubble.height() - 10)
            self.speech_bubble.move(bubble_x, bubble_y)
            self.speech_bubble.show()
            
            # Đặt timer để ẩn bong bóng
            self.speech_duration_timer.start(DEFAULT_SETTINGS['speech_duration'])
        except Exception as e:
            print(f"Lỗi khi hiển thị speech ngay lập tức: {e}")
    
    def show_random_speech(self):
        """Hiển thị câu nói ngẫu nhiên"""
        try:
            # Lấy câu nói phù hợp với loại pet
            pet_speeches = PET_SPEECH.get(self.pet.pet_type, DEFAULT_SPEECH)
            speech_text = random.choice(pet_speeches)
            
            # Hiển thị bong bóng nói
            self.show_speech_immediately(speech_text)
            
            # Đặt timer cho lần nói tiếp theo
            self.start_speech_timer()
        except Exception as e:
            print(f"Lỗi khi hiển thị speech: {e}")
    
    def hide_speech(self):
        """Ẩn bong bóng nói"""
        try:
            if self.speech_bubble:
                self.speech_bubble.close()
                self.speech_bubble = None
        except Exception as e:
            print(f"Lỗi khi ẩn speech: {e}")

class ActivityManager:
    def __init__(self, pet):
        self.pet = pet
        self.current_activity = 'idle'
        self.activities = {
            'idle': self.idle_activity,
            'walk': self.walk_activity,
            'run': self.run_activity,
            'jump': self.jump_activity,
            'fly': self.fly_activity,
            'climb': self.climb_activity,
            'fall': self.fall_activity,
            'die': self.die_activity
        }
        self.activity_timer = QTimer()
        self.activity_timer.timeout.connect(self.change_activity)
        
        # Các thuộc tính cho hoạt động
        self.is_jumping = False
        self.is_flying = False
        self.is_climbing = False
        self.jump_height = 0
        self.fly_target_x = 0
        self.fly_target_y = 0
        self.climb_target_x = 0
        self.climb_target_y = 0
        
        # Bắt đầu timer ngay lập tức
        self.start_activity_timer()
        
    def start_activity_timer(self):
        """Bắt đầu timer để thay đổi hoạt động ngẫu nhiên"""
        try:
            # Dừng timer cũ nếu đang chạy
            if self.activity_timer.isActive():
                self.activity_timer.stop()
            
            min_interval, max_interval = DEFAULT_SETTINGS['activity_change_interval']
            interval = random.randint(min_interval, max_interval)
            self.activity_timer.start(interval)
            print(f"Timer hoạt động đã bắt đầu với interval: {interval}ms cho hoạt động: {self.current_activity}")
        except Exception as e:
            print(f"Lỗi khi bắt đầu activity timer: {e}")
    
    def change_activity(self):
        """Thay đổi hoạt động ngẫu nhiên"""
        try:
            if self.current_activity == 'die':
                return  # Không thay đổi nếu đang chết
                
            # Dừng hoạt động hiện tại
            self.stop_current_activity()
            
            # Chọn hoạt động mới
            available_activities = list(self.activities.keys())
            if self.current_activity in available_activities:
                available_activities.remove(self.current_activity)
            
            # Giảm khả năng chọn "die" (chỉ 5% cơ hội)
            if 'die' in available_activities and random.random() > 0.05:
                available_activities.remove('die')
            
            # Nếu không còn hoạt động nào, thêm lại "die"
            if not available_activities:
                available_activities = ['idle', 'walk', 'run', 'jump', 'fly', 'climb', 'fall']
            
            new_activity = random.choice(available_activities)
            print(f"Thay đổi hoạt động từ {self.current_activity} sang {new_activity}")
            
            # Nói khi thay đổi hành động
            self.speak_on_activity_change(new_activity)
            
            self.start_activity(new_activity)
            
            # Đặt timer cho lần thay đổi tiếp theo
            self.start_activity_timer()
        except Exception as e:
            print(f"Lỗi khi thay đổi activity: {e}")
    
    def speak_on_activity_change(self, new_activity):
        """Nói khi thay đổi hành động"""
        try:
            # Lấy emoji cho hoạt động
            if hasattr(self.pet, 'config_manager'):
                emoji = self.pet.config_manager.get_activity_emoji(new_activity)
            else:
                emoji = '😊'  # Emoji mặc định
            
            # Lấy câu nói phù hợp với hoạt động mới
            activity_speeches = {
                'idle': [f"Tôi sẽ nghỉ ngơi một chút... {emoji}", f"Thật thoải mái! {emoji}"],
                'walk': [f"Tôi sẽ đi dạo một chút! {emoji}", f"Đi bộ thật vui! {emoji}"],
                'run': [f"Chạy thật thú vị! {emoji}", f"Tôi thích chạy! {emoji}"],
                'jump': [f"Nhảy lên nào! {emoji}", f"Wheee! Tôi đang bay! {emoji}"],
                'fly': [f"Bay lượn thật tự do! {emoji}", f"Tôi là chim! {emoji}"],
                'climb': [f"Leo trèo thật thú vị! {emoji}", f"Tôi sẽ leo lên cao! {emoji}"],
                'fall': [f"Ối! Tôi đang rơi! {emoji}", f"Ai cứu tôi! {emoji}"],
                'die': [f"Tôi mệt rồi... {emoji}", f"Tạm biệt... {emoji}"]
            }
            
            # Lấy câu nói cho hoạt động hoặc dùng câu nói chung
            if new_activity in activity_speeches:
                speech_text = random.choice(activity_speeches[new_activity])
            else:
                # Dùng câu nói chung từ config hoặc DEFAULT_SPEECH
                if hasattr(self.pet, 'config_manager'):
                    custom_speeches = self.pet.config_manager.get_custom_speeches()
                    speech_text = random.choice(custom_speeches)
                else:
                    speech_text = random.choice(DEFAULT_SPEECH)
            
            # Hiển thị bong bóng nói
            if hasattr(self.pet, 'speech_manager'):
                self.pet.speech_manager.show_speech_immediately(speech_text)
                
        except Exception as e:
            print(f"Lỗi khi nói khi thay đổi hoạt động: {e}")
    
    def stop_current_activity(self):
        """Dừng hoạt động hiện tại"""
        try:
            if self.is_jumping:
                self.is_jumping = False
                self.jump_height = 0
            if self.is_flying:
                self.is_flying = False
            if self.is_climbing:
                self.is_climbing = False
                # Xóa phase nếu có
                if hasattr(self, 'climb_phase'):
                    delattr(self, 'climb_phase')
        except Exception as e:
            print(f"Lỗi khi dừng activity: {e}")
    
    def start_activity(self, activity_name):
        """Bắt đầu hoạt động mới"""
        try:
            self.current_activity = activity_name
            animation_file = self.pet.animation_manager.get_random_animation(activity_name)
            
            # Nếu không tìm thấy file animation cho hoạt động này, dùng idle_1.gif
            if not animation_file:
                idle_animation = self.pet.animation_manager.get_random_animation('idle')
                if idle_animation:
                    animation_file = idle_animation
                    print(f"Không tìm thấy animation cho {activity_name}, sử dụng idle animation")
            
            if animation_file:
                self.pet.load_animation(animation_file)
                if activity_name in self.activities:
                    self.activities[activity_name]()
        except Exception as e:
            print(f"Lỗi khi bắt đầu activity: {e}")
    
    def idle_activity(self):
        """Hoạt động đứng yên"""
        pass
    
    def walk_activity(self):
        """Hoạt động đi bộ - chậm và ở mặt đất"""
        try:
            self.pet.dx = ACTIVITIES['walk']['speed']
            self.pet.is_on_ground = True
            self.pet.y = self.pet.ground_y
            self.pet.movement_timer.start()
        except Exception as e:
            print(f"Lỗi khi bắt đầu walk: {e}")
    
    def run_activity(self):
        """Hoạt động chạy - nhanh hơn và ở mặt đất"""
        try:
            self.pet.dx = ACTIVITIES['run']['speed']
            self.pet.is_on_ground = True
            self.pet.y = self.pet.ground_y
            self.pet.movement_timer.start()
        except Exception as e:
            print(f"Lỗi khi bắt đầu run: {e}")
    
    def jump_activity(self):
        """Hoạt động nhảy"""
        try:
            self.is_jumping = True
            self.jump_height = 0
            self.pet.is_on_ground = False
            
            # Thêm hướng nhảy ngẫu nhiên
            self.jump_direction = random.choice([-1, 1])  # -1: trái, 1: phải
            self.jump_speed = 2  # Tốc độ di chuyển ngang khi nhảy
            
            self.pet.jump_timer.start()
        except Exception as e:
            print(f"Lỗi khi bắt đầu jump: {e}")
    
    def fly_activity(self):
        """Hoạt động bay - xuất hiện ở cạnh màn hình rồi bay đường cong xuống đất"""
        try:
            self.is_flying = True
            self.pet.is_on_ground = False
            
            # Xuất hiện ở một trong hai cạnh màn hình với độ cao >50% (nửa trên màn hình)
            side = random.choice(['left', 'right'])
            if side == 'left':
                self.pet.x = 0
            else:
                self.pet.x = self.pet.screen_width - 100
            
            # Độ cao từ 10% đến 50% màn hình (nửa trên màn hình)
            min_height = int(self.pet.screen_height * 0.1)  # 10% từ trên xuống
            max_height = int(self.pet.screen_height * 0.5)  # 50% từ trên xuống
            self.pet.y = random.randint(min_height, max_height)
            
            # Target là mặt đất (bay xuống)
            self.fly_target_x = random.randint(0, self.pet.screen_width - 100)
            self.fly_target_y = self.pet.ground_y
            
            # Bắt đầu bay đường cong
            self.fly_phase = 'flying_down'
            self.pet.fly_timer.start()
        except Exception as e:
            print(f"Lỗi khi bắt đầu fly: {e}")
    
    def climb_activity(self):
        """Hoạt động leo trèo - đi đến cạnh màn hình rồi leo lên cao"""
        try:
            self.is_climbing = True
            self.pet.is_on_ground = False
            # Chọn cạnh màn hình (trái hoặc phải)
            self.climb_target_x = 0 if random.random() < 0.5 else self.pet.screen_width - 100
            # Độ cao mục tiêu từ 10% đến 40% màn hình (nửa trên màn hình)
            self.climb_target_y = random.randint(
                int(self.pet.screen_height * 0.1),  # 10% từ trên xuống
                int(self.pet.screen_height * 0.4)   # 40% từ trên xuống
            )
            # Bắt đầu ở giai đoạn di chuyển đến cạnh
            self.climb_phase = 'moving_to_side'
            self.pet.climb_timer.start()
        except Exception as e:
            print(f"Lỗi khi bắt đầu climb: {e}")
    
    def fall_activity(self):
        """Hoạt động rơi - áp dụng trọng lực"""
        try:
            if self.is_climbing:
                self.is_climbing = False
                self.pet.is_on_ground = False
                self.pet.fall_timer.start()
        except Exception as e:
            print(f"Lỗi khi bắt đầu fall: {e}")
    
    def die_activity(self):
        """Hoạt động chết"""
        try:
            # Dừng tất cả timers
            self.pet.movement_timer.stop()
            self.pet.jump_timer.stop()
            self.pet.fly_timer.stop()
            self.pet.climb_timer.stop()
            self.pet.fall_timer.stop()
            
            # Sau 3 giây, pet sẽ "hồi sinh" và chuyển sang hoạt động khác
            QTimer.singleShot(3000, self.resurrect_pet)
        except Exception as e:
            print(f"Lỗi khi bắt đầu die: {e}")
    
    def resurrect_pet(self):
        """Hồi sinh pet và chuyển sang hoạt động khác"""
        try:
            print("Pet đã hồi sinh! 🎉")
            # Khởi động lại tất cả timers
            self.pet.movement_timer.start(16)
            self.pet.jump_timer.start(16)
            self.pet.fly_timer.start(16)
            self.pet.climb_timer.start(16)
            self.pet.fall_timer.start(16)
            
            # Đặt lại trạng thái
            self.current_activity = 'idle'  # Reset về idle
            self.pet.is_on_ground = True
            self.pet.y = self.pet.ground_y
            
            # Chuyển sang hoạt động khác
            self.change_activity()
        except Exception as e:
            print(f"Lỗi khi hồi sinh pet: {e}")

class Pet(QLabel):
    def __init__(self, pet_type="cat", width=None, height=None):
        super().__init__()
        self.pet_type = pet_type
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # Khởi tạo config manager
        from config import ConfigManager
        self.config_manager = ConfigManager()
        
        # Khởi tạo animation manager
        self.animation_manager = AnimationManager(pet_type)
        
        # Vị trí & hướng di chuyển
        self.x, self.y = DISPLAY_SETTINGS['initial_position']
        self.dx = 0
        self.dy = 0  # Thêm dy cho trọng lực
        self.screen_width = QApplication.primaryScreen().size().width()
        self.screen_height = QApplication.primaryScreen().size().height()
        
        # Kích thước pet
        self.pet_width = width or PET_SIZE_SETTINGS['default_width']
        self.pet_height = height or PET_SIZE_SETTINGS['default_height']
        
        # Trọng lực và mặt đất
        self.gravity = 0.5
        self.ground_y = self.screen_height - self.pet_height - 50  # Mặt đất ở dưới màn hình
        self.is_on_ground = False
        
        # Load animation mặc định
        try:
            default_activity = SUPPORTED_PETS.get(pet_type, {}).get('default_activity', 'idle')
            default_animation = self.animation_manager.get_random_animation(default_activity)
            if default_animation:
                self.load_animation(default_animation)
            else:
                # Fallback nếu không có file animation
                self.movie = QMovie("pet.gif")
                self.setMovie(self.movie)
                self.movie.start()
        except Exception as e:
            print(f"Lỗi khi load animation mặc định: {e}")
            # Tạo movie rỗng để tránh lỗi
            self.movie = QMovie()
            self.setMovie(self.movie)
        
        # Đặt kích thước và vị trí
        self.resize(self.pet_width, self.pet_height)
        self.move(self.x, self.y)
        
        # Timers cho các hoạt động
        self.movement_timer = QTimer()
        self.movement_timer.timeout.connect(self.move_pet)
        self.movement_timer.start(16)  # ~60fps
        
        self.jump_timer = QTimer()
        self.jump_timer.timeout.connect(self.jump_animation)
        self.jump_timer.start(16)
        
        self.fly_timer = QTimer()
        self.fly_timer.timeout.connect(self.fly_animation)
        self.fly_timer.start(16)
        
        self.climb_timer = QTimer()
        self.climb_timer.timeout.connect(self.climb_animation)
        self.climb_timer.start(16)
        
        self.fall_timer = QTimer()
        self.fall_timer.timeout.connect(self.fall_animation)
        self.fall_timer.start(16)
        
        # Khởi tạo activity manager
        self.activity_manager = ActivityManager(self)
        
        # Khởi tạo speech manager
        self.speech_manager = SpeechManager(self)
        
        # Bắt đầu hoạt động mặc định
        self.activity_manager.start_activity('idle')
    
    def load_animation(self, animation_file):
        """Load animation từ file"""
        try:
            if os.path.exists(animation_file):
                self.movie = QMovie(animation_file)
                # Scale ảnh theo kích thước hiện tại
                self.movie.setScaledSize(QSize(self.pet_width, self.pet_height))
                self.setMovie(self.movie)
                self.movie.start()
                # Giữ nguyên kích thước đã set
                self.resize(self.pet_width, self.pet_height)
        except Exception as e:
            print(f"Lỗi khi load animation: {e}")
    
    def apply_gravity(self):
        """Áp dụng trọng lực"""
        # Không áp dụng trọng lực khi đang leo
        if hasattr(self.activity_manager, 'is_climbing') and self.activity_manager.is_climbing:
            return
            
        if not self.is_on_ground:
            self.dy += self.gravity
            self.y += self.dy
            
            # Kiểm tra va chạm với mặt đất
            if self.y >= self.ground_y:
                self.y = self.ground_y
                self.dy = 0
                self.is_on_ground = True
    
    def move_pet(self):
        """Di chuyển pet cơ bản với trọng lực"""
        try:
            # Áp dụng trọng lực
            self.apply_gravity()
            
            if self.activity_manager.current_activity in ['walk', 'run']:
                # Di chuyển theo hướng ngang
                self.x += self.dx
                
                # Đảm bảo pet không đi ra ngoài màn hình
                if self.x <= 0:
                    self.x = 0
                    self.dx *= -1
                elif self.x + self.width() >= self.screen_width:
                    self.x = self.screen_width - self.width()
                    self.dx *= -1
                
                # Đảm bảo pet ở trên mặt đất khi đi bộ/chạy
                if self.is_on_ground:
                    self.y = self.ground_y
            
            # Chuyển đổi sang int để tránh lỗi
            self.move(int(self.x), int(self.y))
        except Exception as e:
            print(f"Lỗi khi di chuyển pet: {e}")
    
    def jump_animation(self):
        """Animation nhảy với đường cong và rơi từ từ"""
        try:
            if self.activity_manager.is_jumping:
                jump_height = ACTIVITIES['jump']['height']
                
                if self.activity_manager.jump_height < jump_height:  # Nhảy lên
                    # Tăng độ cao nhảy chậm hơn
                    self.activity_manager.jump_height += 1.5  # Giảm từ 2 xuống 1.5
                    self.y = self.ground_y - self.activity_manager.jump_height
                    self.is_on_ground = False
                    
                    # Di chuyển ngang khi nhảy lên (tạo đường cong)
                    self.x += self.activity_manager.jump_direction * self.activity_manager.jump_speed
                    
                else:  # Rơi xuống
                    # Rơi chậm hơn và từ từ
                    self.activity_manager.jump_height -= 1.0  # Giảm từ 2 xuống 1.0 để rơi chậm hơn
                    self.y = self.ground_y - self.activity_manager.jump_height
                    
                    # Di chuyển ngang khi rơi (tiếp tục đường cong)
                    self.x += self.activity_manager.jump_direction * (self.activity_manager.jump_speed * 0.5)
                    
                    if self.activity_manager.jump_height <= 0:
                        self.activity_manager.is_jumping = False
                        self.y = self.ground_y
                        self.is_on_ground = True
                        # KHÔNG gọi change_activity() ngay lập tức - để timer tự động thay đổi
                
                # Đảm bảo không đi ra ngoài màn hình
                self.x = max(0, min(self.x, self.screen_width - self.width()))
                
                # Chuyển đổi sang int để tránh lỗi
                self.move(int(self.x), int(self.y))
        except Exception as e:
            print(f"Lỗi khi nhảy: {e}")
    
    def fly_animation(self):
        """Animation bay - bay đường cong xuống đất"""
        try:
            if self.activity_manager.is_flying:
                fly_speed = ACTIVITIES['fly']['speed']
                
                # Bay đường cong xuống đất
                dx = (self.activity_manager.fly_target_x - self.x) * fly_speed
                dy = (self.activity_manager.fly_target_y - self.y) * fly_speed
                
                # Thêm chuyển động đường cong (parabolic)
                progress = 1 - (self.y - self.activity_manager.fly_target_y) / (self.y - self.activity_manager.fly_target_y + 1)
                curve_offset = math.sin(progress * math.pi) * 50  # Độ cong
                
                self.x += dx + curve_offset
                self.y += dy
                
                # Đảm bảo không bay ra ngoài màn hình
                self.x = max(0, min(self.x, self.screen_width - self.width()))
                
                # Nếu đã chạm đất, kết thúc bay
                if self.y >= self.ground_y:
                    self.y = self.ground_y
                    self.activity_manager.is_flying = False
                    print("Đã bay xuống đất!")
                
                # Chuyển đổi sang int để tránh lỗi
                self.move(int(self.x), int(self.y))
        except Exception as e:
            print(f"Lỗi khi bay: {e}")
    
    def climb_animation(self):
        """Animation leo trèo - đi đến cạnh rồi leo lên cao và rơi xuống"""
        try:
            if self.activity_manager.is_climbing:
                if self.activity_manager.climb_phase == 'moving_to_side':
                    # Giai đoạn 1: Di chuyển đến cạnh màn hình
                    climb_speed = ACTIVITIES['climb']['speed']
                    dx = (self.activity_manager.climb_target_x - self.x) * climb_speed
                    
                    self.x += dx
                    # Đảm bảo ở trên mặt đất khi di chuyển
                    self.y = self.ground_y
                    self.is_on_ground = True  # Đảm bảo không bị trọng lực kéo
                    
                    # Nếu đã đến cạnh, bắt đầu leo
                    min_distance = DISPLAY_SETTINGS['min_distance']
                    if abs(self.x - self.activity_manager.climb_target_x) < min_distance:
                        self.activity_manager.climb_phase = 'climbing_up'
                        self.is_on_ground = False  # Bắt đầu leo, tắt trọng lực
                        # Load animation leo
                        climb_animation = self.animation_manager.get_random_animation('climb')
                        if climb_animation:
                            self.load_animation(climb_animation)
                        print("Bắt đầu leo lên!")
                
                elif self.activity_manager.climb_phase == 'climbing_up':
                    # Giai đoạn 2: Leo lên đến độ cao mục tiêu
                    self.y -= 4  # Tăng tốc độ leo từ 3 lên 4 để mượt hơn
                    if self.y <= self.activity_manager.climb_target_y:
                        self.y = self.activity_manager.climb_target_y
                        self.activity_manager.climb_phase = 'falling_down'
                        print(f"Đã leo lên độ cao {self.activity_manager.climb_target_y}!")
                
                elif self.activity_manager.climb_phase == 'falling_down':
                    # Giai đoạn 3: Rơi xuống đất
                    self.y += 6  # Tăng tốc độ rơi từ 5 lên 6
                    if self.y >= self.ground_y:
                        self.y = self.ground_y
                        self.is_on_ground = True  # Đặt lại trạng thái mặt đất
                        # Hoàn thành leo, chuyển sang hoạt động khác
                        self.activity_manager.is_climbing = False
                        delattr(self.activity_manager, 'climb_phase')
                        print("Đã rơi xuống đất!")
                
                # Chuyển đổi sang int để tránh lỗi
                self.move(int(self.x), int(self.y))
        except Exception as e:
            print(f"Lỗi khi leo: {e}")
    
    def fall_animation(self):
        """Animation rơi - áp dụng trọng lực"""
        try:
            # Áp dụng trọng lực
            self.apply_gravity()
            
            # Nếu đã chạm đất, KHÔNG chuyển hoạt động ngay - để timer tự động thay đổi
            # Chỉ đảm bảo pet ở trên mặt đất
            if self.is_on_ground:
                self.y = self.ground_y
            
            # Chuyển đổi sang int để tránh lỗi
            self.move(int(self.x), int(self.y))
        except Exception as e:
            print(f"Lỗi khi rơi: {e}")
    
    def set_size(self, width, height):
        """Thay đổi kích thước pet"""
        try:
            # Giới hạn kích thước
            width = max(PET_SIZE_SETTINGS['min_width'], 
                       min(width, PET_SIZE_SETTINGS['max_width']))
            height = max(PET_SIZE_SETTINGS['min_height'], 
                        min(height, PET_SIZE_SETTINGS['max_height']))
            
            self.pet_width = width
            self.pet_height = height
            
            # Cập nhật vị trí mặt đất
            self.ground_y = self.screen_height - self.pet_height - 50
            
            # Scale ảnh theo kích thước mới
            if hasattr(self, 'movie') and self.movie:
                # Tạo QMovie mới với kích thước đã scale
                current_file = self.movie.fileName()
                if current_file and os.path.exists(current_file):
                    self.movie = QMovie(current_file)
                    self.movie.setScaledSize(QSize(width, height))
                    self.setMovie(self.movie)
                    self.movie.start()
            
            self.resize(width, height)
        except Exception as e:
            print(f"Lỗi khi thay đổi kích thước: {e}")

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        pet = Pet("cat")  # Có thể thay đổi thành "dog", "bird", etc.
        pet.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Lỗi khởi động ứng dụng: {e}")
