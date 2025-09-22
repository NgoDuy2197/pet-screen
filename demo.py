# demo.py - Demo ứng dụng Pet Screen
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QComboBox, QSlider, QGroupBox, QGridLayout, QTextEdit, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from pet_python import Pet
from config import SUPPORTED_PETS, ACTIVITIES, PET_SIZE_SETTINGS, ConfigManager

class PetDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pet Screen Demo")
        self.setGeometry(100, 100, 500, 600)
        
        # Khởi tạo config manager
        self.config_manager = ConfigManager()
        
        # Khởi tạo pet
        self.pet = None
        
        # Tải cấu hình từ file
        pet_settings = self.config_manager.get_pet_settings()
        self.current_pet_type = pet_settings['pet_type']
        self.current_width = pet_settings['width']
        self.current_height = pet_settings['height']
        
        # Khởi tạo system tray
        self.tray_icon = None
        self.init_system_tray()
        
        self.init_ui()
        self.create_pet()
    
    def init_system_tray(self):
        """Khởi tạo system tray icon"""
        try:
            # Kiểm tra xem system tray có được hỗ trợ không
            if not QSystemTrayIcon.isSystemTrayAvailable():
                print("System tray không được hỗ trợ trên hệ thống này")
                self.tray_icon = None
                return
            
            # Tạo system tray icon
            self.tray_icon = QSystemTrayIcon(self)
            
            # Tạo icon đơn giản từ style
            from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont
            from PyQt5.QtCore import QSize
            
            # Tạo icon 16x16 pixel với chữ "P" màu trắng trên nền xanh
            pixmap = QPixmap(16, 16)
            pixmap.fill(QColor(52, 152, 219))  # Màu xanh
            
            painter = QPainter(pixmap)
            painter.setPen(QColor(255, 255, 255))  # Màu trắng
            font = QFont()
            font.setBold(True)
            font.setPointSize(10)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), Qt.AlignCenter, "P")
            painter.end()
            
            # Set icon cho system tray
            self.tray_icon.setIcon(QIcon(pixmap))
            self.tray_icon.setToolTip("Pet Screen Demo")
            
            # Tạo context menu cho system tray
            tray_menu = QMenu()
            
            # Action hiện cửa sổ
            show_action = QAction("Hiện cửa sổ", self)
            show_action.triggered.connect(self.show_window)
            tray_menu.addAction(show_action)
            
            # Action ẩn cửa sổ
            hide_action = QAction("Ẩn cửa sổ", self)
            hide_action.triggered.connect(self.hide_window)
            tray_menu.addAction(hide_action)
            
            tray_menu.addSeparator()
            
            # Action hiện/ẩn pet (sẽ được cập nhật sau khi tạo pet)
            # Không thêm action này ở đây vì pet chưa được tạo
            
            tray_menu.addSeparator()
            
            # Action thoát
            quit_action = QAction("Thoát", self)
            quit_action.triggered.connect(self.quit_application)
            tray_menu.addAction(quit_action)
            
            # Gán menu cho tray icon
            self.tray_icon.setContextMenu(tray_menu)
            
            # Kết nối sự kiện click vào tray icon
            self.tray_icon.activated.connect(self.tray_icon_activated)
            
            # Hiển thị tray icon
            self.tray_icon.show()
            
        except Exception as e:
            print(f"Lỗi khi khởi tạo system tray: {e}")
    
    def show_window(self):
        """Hiện cửa sổ từ system tray"""
        try:
            self.show()
            self.activateWindow()
            self.raise_()
        except Exception as e:
            print(f"Lỗi khi hiện cửa sổ: {e}")
    
    def hide_window(self):
        """Ẩn cửa sổ xuống system tray"""
        try:
            self.hide()
            # Hiển thị thông báo trong system tray nếu có
            if self.tray_icon:
                self.tray_icon.showMessage(
                    "Pet Screen Demo",
                    "Ứng dụng đã được minimize xuống system tray. Double-click để hiện lại.",
                    QSystemTrayIcon.Information,
                    3000  # Hiển thị 3 giây
                )
        except Exception as e:
            print(f"Lỗi khi ẩn cửa sổ: {e}")
    
    def toggle_pet(self):
        """Chuyển đổi hiện/ẩn pet"""
        try:
            if self.pet and self.tray_icon:
                if self.pet.isVisible():
                    self.pet.hide()
                    # Cập nhật text của action
                    for action in self.tray_icon.contextMenu().actions():
                        if action.text() in ["Hiện Pet", "Ẩn Pet"]:
                            action.setText("Hiện Pet")
                            break
                else:
                    self.pet.show()
                    # Cập nhật text của action
                    for action in self.tray_icon.contextMenu().actions():
                        if action.text() in ["Hiện Pet", "Ẩn Pet"]:
                            action.setText("Ẩn Pet")
                            break
        except Exception as e:
            print(f"Lỗi khi chuyển đổi pet: {e}")
    
    def quit_application(self):
        """Thoát ứng dụng"""
        try:
            self.save_settings()
            if self.pet:
                self.pet.close()
            if self.tray_icon:
                self.tray_icon.hide()
            QApplication.quit()
        except Exception as e:
            print(f"Lỗi khi thoát ứng dụng: {e}")
    
    def tray_icon_activated(self, reason):
        """Xử lý sự kiện click vào tray icon"""
        try:
            if reason == QSystemTrayIcon.DoubleClick:
                # Double click để hiện cửa sổ
                self.show_window()
        except Exception as e:
            print(f"Lỗi khi xử lý sự kiện tray icon: {e}")
    
    def init_ui(self):
        """Khởi tạo giao diện"""
        try:
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            layout = QVBoxLayout()
            
            # Tiêu đề
            title = QLabel("Pet Screen Demo")
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px; color: #2c3e50;")
            layout.addWidget(title)
            
            # Chọn loại pet
            pet_group = QGroupBox("Chọn Loại Pet")
            pet_layout = QHBoxLayout()
            pet_layout.addWidget(QLabel("Loại Pet:"))
            
            self.pet_combo = QComboBox()
            for pet_type, pet_info in SUPPORTED_PETS.items():
                self.pet_combo.addItem(pet_info['name'], pet_type)
            self.pet_combo.currentTextChanged.connect(self.change_pet_type)
            pet_layout.addWidget(self.pet_combo)
            
            # Đặt giá trị hiện tại cho combo box
            for i in range(self.pet_combo.count()):
                if self.pet_combo.itemData(i) == self.current_pet_type:
                    self.pet_combo.setCurrentIndex(i)
                    break
            
            pet_group.setLayout(pet_layout)
            layout.addWidget(pet_group)
            
            # Cài đặt kích thước
            size_group = QGroupBox("Cài Đặt Kích Thước")
            size_layout = QGridLayout()
            
            # Slider chiều rộng
            size_layout.addWidget(QLabel("Chiều rộng:"), 0, 0)
            self.width_slider = QSlider(Qt.Horizontal)
            self.width_slider.setMinimum(PET_SIZE_SETTINGS['min_width'])
            self.width_slider.setMaximum(PET_SIZE_SETTINGS['max_width'])
            self.width_slider.setValue(self.current_width)
            self.width_slider.valueChanged.connect(self.change_width)
            size_layout.addWidget(self.width_slider, 0, 1)
            
            self.width_label = QLabel(f"{self.current_width}px")
            size_layout.addWidget(self.width_label, 0, 2)
            
            # Slider chiều cao
            size_layout.addWidget(QLabel("Chiều cao:"), 1, 0)
            self.height_slider = QSlider(Qt.Horizontal)
            self.height_slider.setMinimum(PET_SIZE_SETTINGS['min_height'])
            self.height_slider.setMaximum(PET_SIZE_SETTINGS['max_height'])
            self.height_slider.setValue(self.current_height)
            self.height_slider.valueChanged.connect(self.change_height)
            size_layout.addWidget(self.height_slider, 1, 1)
            
            self.height_label = QLabel(f"{self.current_height}px")
            size_layout.addWidget(self.height_label, 1, 2)
            
            size_group.setLayout(size_layout)
            layout.addWidget(size_group)
            
            # Nút điều khiển
            control_group = QGroupBox("Điều Khiển")
            control_layout = QHBoxLayout()
            
            self.create_btn = QPushButton("Tạo Pet")
            self.create_btn.clicked.connect(self.create_pet)
            self.create_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
            """)
            control_layout.addWidget(self.create_btn)
            
            self.hide_btn = QPushButton("Ẩn Pet")
            self.hide_btn.clicked.connect(self.hide_pet)
            self.hide_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            control_layout.addWidget(self.hide_btn)
            
            self.show_btn = QPushButton("Hiện Pet")
            self.show_btn.clicked.connect(self.show_pet)
            self.show_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            control_layout.addWidget(self.show_btn)
            
            # Nút lưu cấu hình
            self.save_btn = QPushButton("Lưu Cấu Hình")
            self.save_btn.clicked.connect(self.save_settings)
            self.save_btn.setStyleSheet("""
                QPushButton {
                    background-color: #9b59b6;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #8e44ad;
                }
            """)
            control_layout.addWidget(self.save_btn)
            
            # Nút minimize to tray
            self.minimize_btn = QPushButton("Minimize to Tray")
            self.minimize_btn.clicked.connect(self.hide_window)
            self.minimize_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f39c12;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #e67e22;
                }
            """)
            control_layout.addWidget(self.minimize_btn)
            
            control_group.setLayout(control_layout)
            layout.addWidget(control_group)
            
            # Thông tin hoạt động
            info_group = QGroupBox("Thông Tin")
            info_layout = QVBoxLayout()
            
            self.activity_label = QLabel("Hoạt động hiện tại: Idle")
            self.activity_label.setAlignment(Qt.AlignCenter)
            self.activity_label.setStyleSheet("""
                margin: 10px; 
                padding: 10px; 
                background-color: #ecf0f1; 
                border-radius: 5px;
                font-weight: bold;
                color: #2c3e50;
            """)
            info_layout.addWidget(self.activity_label)
            
            # Danh sách hoạt động
            activities_text = "Các hoạt động có sẵn:\n"
            for activity, info in ACTIVITIES.items():
                activities_text += f"• {info['name']}: {info['description']}\n"
            
            activities_label = QLabel(activities_text)
            activities_label.setStyleSheet("""
                font-size: 12px; 
                margin: 10px; 
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 5px;
                color: #495057;
            """)
            info_layout.addWidget(activities_label)
            
            info_group.setLayout(info_layout)
            layout.addWidget(info_group)
            
            # Nhóm cài đặt câu nói
            speech_group = QGroupBox("Cấu hình câu nói")
            speech_layout = QVBoxLayout()
            
            # Text area cho câu nói tùy chỉnh
            self.speech_label = QLabel("Câu nói tùy chỉnh (mỗi dòng một câu):")
            self.speech_text_edit = QTextEdit()
            self.speech_text_edit.setMaximumHeight(100)
            
            # Load câu nói hiện tại
            current_speeches = self.config_manager.get_custom_speeches()
            self.speech_text_edit.setPlainText('\n'.join(current_speeches))
            
            # Nút lưu câu nói
            self.save_speeches_button = QPushButton("Lưu câu nói")
            self.save_speeches_button.clicked.connect(self.save_speeches)
            
            speech_layout.addWidget(self.speech_label)
            speech_layout.addWidget(self.speech_text_edit)
            speech_layout.addWidget(self.save_speeches_button)
            speech_group.setLayout(speech_layout)
            
            # Thêm vào layout chính
            layout.addWidget(speech_group)
            
            central_widget.setLayout(layout)
            
        except Exception as e:
            print(f"Lỗi khi khởi tạo giao diện: {e}")
    
    def change_pet_type(self, pet_name):
        """Thay đổi loại pet"""
        try:
            for pet_type, pet_info in SUPPORTED_PETS.items():
                if pet_info['name'] == pet_name:
                    self.current_pet_type = pet_type
                    break
        except Exception as e:
            print(f"Lỗi khi thay đổi loại pet: {e}")
    
    def change_width(self, value):
        """Thay đổi chiều rộng"""
        try:
            self.current_width = value
            self.width_label.setText(f"{value}px")
            if self.pet:
                self.pet.set_size(self.current_width, self.current_height)
        except Exception as e:
            print(f"Lỗi khi thay đổi chiều rộng: {e}")
    
    def change_height(self, value):
        """Thay đổi chiều cao"""
        try:
            self.current_height = value
            self.height_label.setText(f"{value}px")
            if self.pet:
                self.pet.set_size(self.current_width, self.current_height)
        except Exception as e:
            print(f"Lỗi khi thay đổi chiều cao: {e}")
    
    def save_settings(self):
        """Lưu cấu hình hiện tại"""
        try:
            self.config_manager.update_pet_settings(
                self.current_pet_type, 
                self.current_width, 
                self.current_height
            )
            print("Đã lưu cấu hình thành công!")
        except Exception as e:
            print(f"Lỗi khi lưu cấu hình: {e}")
    
    def create_pet(self):
        """Tạo pet mới"""
        try:
            if self.pet:
                self.pet.close()
            
            self.pet = Pet(self.current_pet_type, self.current_width, self.current_height)
            self.pet.show()
            
            # Cập nhật label hoạt động
            self.update_activity_label()
            
            # Cập nhật system tray menu với action toggle pet
            self.update_tray_menu()
            
            print(f"Đã tạo pet {self.current_pet_type} với kích thước {self.current_width}x{self.current_height}")
        except Exception as e:
            print(f"Lỗi khi tạo pet: {e}")
    
    def update_tray_menu(self):
        """Cập nhật menu system tray"""
        try:
            if self.tray_icon and self.tray_icon.contextMenu() and self.pet:
                menu = self.tray_icon.contextMenu()
                
                # Xóa action toggle pet cũ nếu có
                for action in menu.actions():
                    if action.text() in ["Hiện Pet", "Ẩn Pet"]:
                        menu.removeAction(action)
                        break
                
                # Thêm action toggle pet mới
                toggle_pet_action = QAction("Ẩn Pet", self)
                toggle_pet_action.triggered.connect(self.toggle_pet)
                
                # Thêm action vào sau separator đầu tiên
                separator_count = 0
                insert_index = -1
                for i, action in enumerate(menu.actions()):
                    if action.isSeparator():
                        separator_count += 1
                        if separator_count == 1:  # Sau separator đầu tiên
                            insert_index = i + 1
                            break
                
                if insert_index >= 0:
                    menu.insertAction(menu.actions()[insert_index], toggle_pet_action)
                else:
                    # Nếu không tìm thấy separator, thêm vào cuối
                    menu.addAction(toggle_pet_action)
        except Exception as e:
            print(f"Lỗi khi cập nhật tray menu: {e}")
    
    def hide_pet(self):
        """Ẩn pet"""
        try:
            if self.pet:
                self.pet.hide()
                print("Đã ẩn pet")
        except Exception as e:
            print(f"Lỗi khi ẩn pet: {e}")
    
    def show_pet(self):
        """Hiện pet"""
        try:
            if self.pet:
                self.pet.show()
                print("Đã hiện pet")
        except Exception as e:
            print(f"Lỗi khi hiện pet: {e}")
    
    def update_activity_label(self):
        """Cập nhật label hiển thị hoạt động hiện tại"""
        try:
            if self.pet and hasattr(self.pet, 'activity_manager'):
                current_activity = self.pet.activity_manager.current_activity
                activity_name = ACTIVITIES.get(current_activity, {}).get('name', current_activity)
                self.activity_label.setText(f"Hoạt động hiện tại: {activity_name}")
        except Exception as e:
            print(f"Lỗi khi cập nhật activity label: {e}")
    
    def save_speeches(self):
        """Lưu câu nói tùy chỉnh"""
        try:
            custom_speeches = self.speech_text_edit.toPlainText().split('\n')
            self.config_manager.update_custom_speeches(custom_speeches)
            print("Đã lưu câu nói tùy chỉnh thành công!")
        except Exception as e:
            print(f"Lỗi khi lưu câu nói tùy chỉnh: {e}")
    
    def closeEvent(self, event):
        """Sự kiện khi đóng ứng dụng"""
        try:
            # Thay vì đóng hoàn toàn, minimize xuống system tray
            self.hide()
            event.ignore()  # Ngăn không cho đóng cửa sổ
            
            # Hiển thị thông báo trong system tray
            if self.tray_icon:
                self.tray_icon.showMessage(
                    "Pet Screen Demo",
                    "Ứng dụng đã được minimize xuống system tray. Double-click để hiện lại.",
                    QSystemTrayIcon.Information,
                    3000  # Hiển thị 3 giây
                )
        except Exception as e:
            print(f"Lỗi khi đóng ứng dụng: {e}")
            event.accept()

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        
        # Áp dụng style cho toàn bộ ứng dụng
        app.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2c3e50;
            }
            QLabel {
                color: #2c3e50;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
            }
            QSlider::groove:horizontal {
                border: 1px solid #bdc3c7;
                height: 8px;
                background: #ecf0f1;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #3498db;
                border: 1px solid #2980b9;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
        """)
        
        demo = PetDemo()
        demo.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Lỗi khởi động ứng dụng: {e}")
