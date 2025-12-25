import sys
import os
import shutil
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QComboBox, QSlider, QGroupBox, QGridLayout, QTextEdit, QSystemTrayIcon, QMenu, QAction, QCheckBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from pet_python import Pet
from config import SUPPORTED_PETS, ACTIVITIES, PET_SIZE_SETTINGS, ConfigManager

class PetCharacter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pet Screen")
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
        
        # Đồng bộ trạng thái auto-start với Windows Startup
        self.sync_auto_start_status()
        
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
            self.tray_icon.setToolTip("Pet Screen")
            
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
                    "Pet Screen",
                    "Ứng dụng đang chạy ngầm vs ICON chữ P",
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
            title = QLabel("Pet Screen")
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
            
            # Nhóm cài đặt tự động khởi động
            startup_group = QGroupBox("Cài Đặt Khởi Động")
            startup_layout = QVBoxLayout()
            
            self.auto_start_checkbox = QCheckBox("Tự động chạy khi khởi động Windows")
            # Load trạng thái auto-start từ config (sẽ được cập nhật trong sync_auto_start_status)
            self.auto_start_checkbox.stateChanged.connect(self.toggle_auto_start)
            startup_layout.addWidget(self.auto_start_checkbox)
            startup_group.setLayout(startup_layout)
            layout.addWidget(startup_group)
            
            # Thông tin tác giả
            author_label = QLabel("Tác giả: DuyNQ2197@gmail.com")
            author_label.setAlignment(Qt.AlignCenter)
            author_label.setStyleSheet("""
                color: #34495e;
                font-size: 11px;
                padding: 5px;
                margin-top: 5px;
            """)
            layout.addWidget(author_label)
            
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
    
    def save_speeches(self):
        """Lưu câu nói tùy chỉnh"""
        try:
            custom_speeches = self.speech_text_edit.toPlainText().split('\n')
            # Lọc bỏ các dòng trống
            custom_speeches = [s.strip() for s in custom_speeches if s.strip()]
            self.config_manager.update_custom_speeches(custom_speeches)
            
            # Reload config của pet nếu pet đã được tạo
            if self.pet and hasattr(self.pet, 'config_manager'):
                self.pet.config_manager.reload_config()
                print("Đã reload cấu hình cho pet!")
            
            print("Đã lưu câu nói tùy chỉnh thành công!")
        except Exception as e:
            print(f"Lỗi khi lưu câu nói tùy chỉnh: {e}")
    
    def toggle_auto_start(self, state):
        """Bật/tắt tự động khởi động cùng Windows"""
        try:
            enabled = state == Qt.Checked
            success = False
            
            if enabled:
                # Thêm shortcut vào Startup folder
                success = self.add_to_startup()
            else:
                # Xóa shortcut từ Startup folder
                success = self.remove_from_startup()
            
            if success:
                # Lưu trạng thái vào config
                self.config_manager.set_auto_start(enabled)
                
                if enabled:
                    print("Đã bật tự động khởi động cùng Windows!")
                else:
                    print("Đã tắt tự động khởi động cùng Windows!")
            else:
                # Khôi phục lại checkbox nếu thất bại
                self.auto_start_checkbox.blockSignals(True)
                self.auto_start_checkbox.setChecked(not enabled)
                self.auto_start_checkbox.blockSignals(False)
                print("Không thể thay đổi cài đặt auto-start!")
        except Exception as e:
            print(f"Lỗi khi thay đổi cài đặt auto-start: {e}")
            # Khôi phục lại checkbox nếu có lỗi
            self.auto_start_checkbox.blockSignals(True)
            self.auto_start_checkbox.setChecked(not enabled)
            self.auto_start_checkbox.blockSignals(False)
    
    def get_startup_folder(self):
        """Lấy đường dẫn đến thư mục Startup của Windows"""
        try:
            appdata = os.getenv('APPDATA')
            startup_folder = os.path.join(appdata, r'Microsoft\Windows\Start Menu\Programs\Startup')
            return startup_folder
        except Exception as e:
            print(f"Lỗi khi lấy đường dẫn Startup folder: {e}")
            return None
    
    def get_app_path(self):
        """Lấy đường dẫn đến file thực thi của ứng dụng"""
        try:
            # Nếu chạy từ file .exe
            if getattr(sys, 'frozen', False):
                # Chạy từ PyInstaller bundle
                app_path = sys.executable
            else:
                # Chạy từ Python script
                app_path = os.path.abspath(__file__)
            return app_path
        except Exception as e:
            print(f"Lỗi khi lấy đường dẫn ứng dụng: {e}")
            return None
    
    def add_to_startup(self):
        """Thêm ứng dụng vào Startup folder"""
        try:
            startup_folder = self.get_startup_folder()
            app_path = self.get_app_path()
            
            if not startup_folder or not app_path:
                print("Không thể thêm vào Startup folder")
                return False
            
            # Tên file shortcut
            shortcut_name = "Pet Screen.lnk"
            shortcut_path = os.path.join(startup_folder, shortcut_name)
            
            # Kiểm tra xem shortcut đã tồn tại chưa
            if os.path.exists(shortcut_path):
                print("Shortcut đã tồn tại trong Startup folder")
                return True
            
            # Thử tạo shortcut bằng win32com (nếu có)
            try:
                import win32com.client
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(shortcut_path)
                shortcut.Targetpath = app_path
                shortcut.WorkingDirectory = os.path.dirname(app_path)
                shortcut.save()
                print(f"Đã tạo shortcut tại {shortcut_path}")
                return True
            except ImportError:
                # Nếu không có win32com, thử dùng batch file
                print("Không có win32com, thử tạo batch file...")
                batch_path = os.path.join(startup_folder, "Pet Screen.bat")
                with open(batch_path, 'w', encoding='utf-8') as f:
                    if getattr(sys, 'frozen', False):
                        # Chạy từ .exe
                        f.write(f'@echo off\n"{app_path}"\n')
                    else:
                        # Chạy từ Python script
                        python_exe = sys.executable
                        f.write(f'@echo off\n"{python_exe}" "{app_path}"\n')
                print(f"Đã tạo batch file tại {batch_path}")
                return True
            except Exception as e:
                print(f"Lỗi khi tạo shortcut bằng win32com: {e}")
                # Fallback: tạo batch file
                batch_path = os.path.join(startup_folder, "Pet Screen.bat")
                with open(batch_path, 'w', encoding='utf-8') as f:
                    if getattr(sys, 'frozen', False):
                        f.write(f'@echo off\n"{app_path}"\n')
                    else:
                        python_exe = sys.executable
                        f.write(f'@echo off\n"{python_exe}" "{app_path}"\n')
                print(f"Đã tạo batch file tại {batch_path}")
                return True
        except Exception as e:
            print(f"Lỗi khi thêm vào Startup folder: {e}")
            return False
    
    def remove_from_startup(self):
        """Xóa ứng dụng khỏi Startup folder"""
        try:
            startup_folder = self.get_startup_folder()
            
            if not startup_folder:
                print("Không thể truy cập Startup folder")
                return False
            
            # Xóa shortcut .lnk
            shortcut_path = os.path.join(startup_folder, "Pet Screen.lnk")
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
                print(f"Đã xóa shortcut tại {shortcut_path}")
            
            # Xóa batch file (nếu có)
            batch_path = os.path.join(startup_folder, "Pet Screen.bat")
            if os.path.exists(batch_path):
                os.remove(batch_path)
                print(f"Đã xóa batch file tại {batch_path}")
            
            return True
        except Exception as e:
            print(f"Lỗi khi xóa khỏi Startup folder: {e}")
            return False
    
    def sync_auto_start_status(self):
        """Đồng bộ trạng thái auto-start với Windows Startup folder"""
        try:
            startup_folder = self.get_startup_folder()
            if not startup_folder:
                return
            
            # Kiểm tra xem shortcut/batch file có tồn tại không
            shortcut_path = os.path.join(startup_folder, "Pet Screen.lnk")
            batch_path = os.path.join(startup_folder, "Pet Screen.bat")
            exists_in_startup = os.path.exists(shortcut_path) or os.path.exists(batch_path)
            
            # Lấy trạng thái từ config
            config_enabled = self.config_manager.get_auto_start()
            
            # Đồng bộ: nếu có trong Startup nhưng config không bật, hoặc ngược lại
            if exists_in_startup != config_enabled:
                if exists_in_startup:
                    # Có trong Startup nhưng config không bật -> cập nhật config
                    self.config_manager.set_auto_start(True)
                    if hasattr(self, 'auto_start_checkbox'):
                        self.auto_start_checkbox.setChecked(True)
                else:
                    # Không có trong Startup nhưng config bật -> cập nhật config
                    self.config_manager.set_auto_start(False)
                    if hasattr(self, 'auto_start_checkbox'):
                        self.auto_start_checkbox.setChecked(False)
            else:
                # Đồng bộ checkbox với config
                if hasattr(self, 'auto_start_checkbox'):
                    self.auto_start_checkbox.setChecked(config_enabled)
        except Exception as e:
            print(f"Lỗi khi đồng bộ trạng thái auto-start: {e}")
    
    def closeEvent(self, event):
        """Sự kiện khi đóng ứng dụng"""
        try:
            # Thay vì đóng hoàn toàn, minimize xuống system tray
            self.hide()
            event.ignore()  # Ngăn không cho đóng cửa sổ
            
            # Hiển thị thông báo trong system tray
            if self.tray_icon:
                self.tray_icon.showMessage(
                    "Pet Screen",
                    "Ứng dụng đang chạy ngầm vs ICON chữ P",
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
                background-color: #e6f2ff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #a3d0ff;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: #f0f8ff;
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
                border: 1px solid #b3d9ff;
                border-radius: 5px;
                background-color: #f9fcff;
            }
            QSlider::groove:horizontal {
                border: 1px solid #a3d0ff;
                height: 8px;
                background: #d4e8ff;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffccb3, stop:1 #ffb3d9);
                border: 1px solid #ffa680;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
        """)
        
        petCharacter = PetCharacter()
        petCharacter.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Lỗi khởi động ứng dụng: {e}")
