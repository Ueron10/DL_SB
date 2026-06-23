# SMARTBIN - Line by Line Code Explanation

## Table of Contents
1. [app/app.py](#appapppy---831-lines)
2. [src/convert_coco_to_yolo.py](#srconvert_coco_to_yolopy---119-lines)
3. [src/detection.py](#srcdetectionpy---83-lines)
4. [src/main.py](#srcmainpy---312-lines)
5. [data/data.yaml](#datadatayaml---8-lines)
6. [requirements.txt](#requirementstxt---8-lines)

---

## app/app.py - 831 Lines

### Lines 1-20: Imports and Configuration
```
Line 1:  import tkinter as tk
         - Import library tkinter untuk membuat GUI (Graphical User Interface)
         
Line 2:  from PIL import Image, ImageTk
         - Import PIL (Python Imaging Library) untuk manipulasi gambar dan konversi ke format Tkinter
         
Line 3:  import cv2
         - Import OpenCV (cv2) untuk capture video dan processing gambar
         
Line 4:  import threading
         - Import threading untuk menjalankan deteksi di background thread agar GUI tidak freeze
         
Line 5:  import os
         - Import os untuk operasi file system dan path handling
         
Line 6:  import sys
         - Import sys untuk manipulasi system path
         
Line 7:  import time
         - Import time untuk fungsi waktu (sleep, timestamp)
         
Line 8:  import serial
         - Import pyserial untuk komunikasi serial dengan Arduino
         
Line 9:  (blank line)
         
Line 10: sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
         - Menambahkan parent directory ke Python path agar bisa import modul dari src/
         
Line 11: (blank line)
         
Line 12: from src.detection import DetectionSystem
         - Import class DetectionSystem dari modul src.detection
         
Line 13: (blank line)
         
Line 14: SERIAL_PORT = "COM4"
         - Konstanta port serial untuk komunikasi Arduino (COM4)
         
Line 15: BAUD_RATE = 115200
         - Konstanta baud rate untuk komunikasi serial (115200 bps)
         
Line 16: SERIAL_COMMANDS = {
         - Mulai dictionary untuk mapping kategori sampah ke command serial
         
Line 17:     "organik": "O",
         - Command "O" untuk kategori organik
         
Line 18:     "nonorganik": "N",
         - Command "N" untuk kategori non-organik
         
Line 19:     "sampah_berbahaya": "B"
         - Command "B" untuk kategori sampah berbahaya
         
Line 20: }
         - Tutup dictionary SERIAL_COMMANDS
```

### Lines 22-76: SerialComm Class
```
Line 22: class SerialComm:
         - Mendefinisikan class SerialComm untuk handle komunikasi serial
         
Line 23:     def __init__(self, enabled=True):
         - Constructor class, parameter enabled untuk enable/disable serial
         
Line 24:         self.ser = None
         - Inisialisasi serial object sebagai None
         
Line 25:         self.connected = False
         - Inisialisasi status koneksi sebagai False
         
Line 26:         self.enabled = enabled
         - Simpan parameter enabled ke instance variable
         
Line 27:         if self.enabled:
         - Cek jika serial communication di-enable
         
Line 28:             self._initialize()
         - Panggil method _initialize untuk koneksi serial
         
Line 29:         else:
         - Jika serial disabled
         
Line 30:             print("Serial communication disabled (display only mode)")
         - Print pesan bahwa serial dalam mode display only
         
Line 31: (blank line)
         
Line 32:     def _initialize(self):
         - Method private untuk inisialisasi koneksi serial
         
Line 33:         print("Initializing serial connection...")
         - Print pesan inisialisasi serial
         
Line 34:         try:
         - Mulai try block untuk handle error koneksi
         
Line 35:             self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
         - Coba buka koneksi serial dengan port dan baud rate yang ditentukan
         
Line 36:             self.connected = True
         - Set status connected menjadi True jika berhasil
         
Line 37:             print(f"Serial connected to {SERIAL_PORT}")
         - Print pesan sukses koneksi
         
Line 38:         except Exception as e:
         - Catch exception jika koneksi gagal
         
Line 39:             print(f"Warning: Could not connect to serial port: {e}")
         - Print pesan warning dengan error detail
         
Line 40:             print("Serial communication disabled.")
         - Print pesan bahwa serial disabled
         
Line 41:             self.connected = False
         - Set status connected menjadi False
         
Line 42:             self.ser = None
         - Set serial object menjadi None
         
Line 43: (blank line)
         
Line 44:     def send_command(self, category):
         - Method untuk mengirim command ke Arduino berdasarkan kategori
         
Line 45:         if not self.connected or self.ser is None:
         - Cek jika tidak terkoneksi atau serial object None
         
Line 46:             return False
         - Return False jika tidak bisa kirim
         
Line 47: (blank line)
         
Line 48:         command = SERIAL_COMMANDS.get(category, None)
         - Ambil command dari dictionary berdasarkan kategori
         
Line 49:         if command is None:
         - Cek jika command tidak ditemukan
         
Line 50:             return False
         - Return False jika command invalid
         
Line 51: (blank line)
         
Line 52:         try:
         - Mulai try block untuk kirim data
         
Line 53:             self.ser.write(command.encode())
         - Encode command ke bytes dan kirim via serial
         
Line 54:             return True
         - Return True jika berhasil kirim
         
Line 55:         except Exception as e:
         - Catch exception jika error saat kirim
         
Line 56:             print(f"Serial write error: {e}")
         - Print error message
         
Line 57:             return False
         - Return False jika gagal
         
Line 58: (blank line)
         
Line 59:     def read_done_signal(self):
         - Method untuk membaca sinyal "DONE" dari Arduino
         
Line 60:         if not self.connected or self.ser is None:
         - Cek jika tidak terkoneksi
         
Line 61:             return False
         - Return False jika tidak bisa baca
         
Line 62: (blank line)
         
Line 63:         try:
         - Mulai try block untuk baca data
         
Line 64:             if self.ser.in_waiting > 0:
         - Cek jika ada data di buffer serial
         
Line 65:                 line = self.ser.readline().decode().strip()
         - Baca line, decode dari bytes ke string, dan strip whitespace
         
Line 66:                 return line == "DONE"
         - Return True jika line adalah "DONE"
         
Line 67:         except Exception as e:
         - Catch exception jika error baca
         
Line 68:             print(f"Serial read error: {e}")
         - Print error message
         
Line 69:             return False
         - Return False jika error
         
Line 70:         return False
         - Return False jika tidak ada data
         
Line 71: (blank line)
         
Line 72:     def close(self):
         - Method untuk menutup koneksi serial
         
Line 73:         if self.connected and self.ser is not None:
         - Cek jika terkoneksi dan serial object ada
         
Line 74:             self.ser.close()
         - Tutup koneksi serial
         
Line 75:             print("Serial connection closed")
         - Print pesan koneksi ditutup
         
Line 76: (blank line)
```

### Lines 77-108: SmartBinGUI Class - Initialization
```
Line 77: class SmartBinGUI:
         - Mendefinisikan class utama GUI aplikasi SmartBin
         
Line 78:     def __init__(self, root, detection_system, serial_comm, use_microcontroller):
         - Constructor dengan parameter: root window, detection system, serial comm, mode flag
         
Line 79:         self.root = root
         - Simpan reference ke root Tkinter window
         
Line 80:         self.detection_system = detection_system
         - Simpan reference ke detection system
         
Line 81:         self.serial_comm = serial_comm
         - Simpan reference ke serial communication object
         
Line 82:         self.use_microcontroller = use_microcontroller
         - Simpan flag apakah menggunakan microcontroller atau display only
         
Line 83:         self.running = False
         - Flag untuk status deteksi berjalan
         
Line 84:         self.cap = None
         - Object untuk capture kamera (VideoCapture)
         
Line 85:         self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
         - Dapatkan base directory project (2 level up dari app.py)
         
Line 86: (blank line)
         
Line 87:         self.stability_counter = 0
         - Counter untuk stability check (jumlah frame berturut-turut)
         
Line 88:         self.last_detected_category = None
         - Simpan kategori terakhir yang terdeteksi
         
Line 89:         self.last_decision_time = 0
         - Simpan waktu keputusan terakhir
         
Line 90:         self.frame_count = 0
         - Counter total frame yang diproses
         
Line 91:         self.processing = False
         - Flag untuk status sedang memproses (menunggu Arduino)
         
Line 92:         self.last_detection_result = None
         - Simpan hasil deteksi terakhir
         
Line 93:         self.last_processed_object = None
         - Simpan objek terakhir yang diproses
         
Line 94:         self.last_processed_time = 0
         - Simpan waktu proses terakhir
         
Line 95:         self.capturing = False
         - Flag untuk status sedang capture manual
         
Line 96:         self.no_detection_start_time = 0
         - Waktu mulai tidak ada deteksi
         
Line 97:         self.no_detection_timeout = 3.0
         - Timeout untuk tidak ada deteksi (3 detik)
         
Line 98:         self.auto_detection = True
         - Flag untuk mode auto detection
         
Line 99:         self.cooldown_duration = 3.0
         - Durasi cooldown setelah deteksi (3 detik)
         
Line 100:         self.cooldown_start_time = 0
         - Waktu mulai cooldown
         
Line 101:         self.stability_frames_required = 3
         - Jumlah frame berturut-turut yang diperlukan untuk deteksi valid
         
Line 102:         self.confidence_threshold = 0.5
         - Threshold confidence untuk deteksi
         
Line 103: (blank line)
         
Line 104:         self.setup_ui()
         - Panggil method untuk setup UI
         
Line 105:         self.setup_camera()
         - Panggil method untuk setup kamera
         
Line 106: (blank line)
         
Line 107:         self.root.bind('<space>', self.on_spacebar)
         - Bind tombol spacebar ke handler on_spacebar
         
Line 108: (blank line)
```

### Lines 109-178: UI Setup Methods
```
Line 109:     def setup_ui(self):
         - Method untuk membuat dan mengatur UI
         
Line 110:         self.root.title("SMARTBIN - Automatic Waste Sorter")
         - Set judul window
         
Line 111:         self.root.geometry("1200x700")
         - Set ukuran window 1200x700 pixels
         
Line 112:         self.root.configure(bg="#f0fff4")
         - Set background color ke hijau muda
         
Line 113: (blank line)
         
Line 114:         main_frame = tk.Frame(self.root, bg="#f0fff4")
         - Buat main frame dengan background hijau muda
         
Line 115:         main_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
         - Pack main frame dengan padding 25px
         
Line 116: (blank line)
         
Line 117:         top_bar = tk.Frame(main_frame, bg="#f0fff4")
         - Buat top bar frame
         
Line 118:         top_bar.pack(fill=tk.X, pady=(0, 10))
         - Pack top bar dengan padding bottom 10px
         
Line 119: (blank line)
         
Line 120:         back_button = tk.Button(top_bar, text="← Back", font=("Segoe UI", 9, "bold"),
         - Buat tombol back dengan font Segoe UI bold size 9
         
Line 121:                                bg="#718096", fg="white", activebackground="#4a5568",
         - Set warna background abu-abu, foreground white, active background lebih gelap
         
Line 122:                                activeforeground="white", relief=tk.RAISED,
         - Set active foreground white dan relief raised
         
Line 123:                                cursor="hand2", padx=10, pady=5, command=self.go_back_to_mode_selection,
         - Set cursor hand2, padding, dan command untuk kembali ke mode selection
         
Line 124:                                bd=2, highlightthickness=0)
         - Set border width 2 dan tanpa highlight
         
Line 125:         back_button.pack(side=tk.LEFT)
         - Pack tombol back di sisi kiri
         
Line 126: (blank line)
         
Line 127:         video_frame = tk.Frame(main_frame, bg="#e6ffed", bd=0, relief=tk.FLAT)
         - Buat frame untuk video dengan background hijau lebih muda
         
Line 128:         video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
         - Pack video frame di kiri dengan expand dan padding right 15px
         
Line 129: (blank line)
         
Line 130:         video_border = tk.Frame(video_frame, bg="#48bb78", bd=0)
         - Buat border frame dengan warna hijau
         
Line 131:         video_border.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
         - Pack border dengan padding 3px
         
Line 132: (blank line)
         
Line 133:         self.video_label = tk.Label(video_border, bg="#e6ffed")
         - Buat label untuk menampilkan video feed
         
Line 134:         self.video_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
         - Pack label dengan padding 10px
         
Line 135: (blank line)
         
Line 136:         button_frame = tk.Frame(video_frame, bg="#e6ffed")
         - Buat frame untuk tombol kontrol
         
Line 137:         button_frame.pack(fill=tk.X, padx=10, pady=10)
         - Pack button frame dengan padding
         
Line 138: (blank line)
         
Line 139:         self.start_button = self.create_modern_button(button_frame, "Start Detection", "#48bb78", self.start_detection)
         - Buat tombol start detection dengan warna hijau
         
Line 140:         self.start_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
         - Pack tombol start di kiri dengan expand
         
Line 141: (blank line)
         
Line 142:         self.stop_button = self.create_modern_button(button_frame, "Reset", "#e53e3e", self.stop_detection)
         - Buat tombol reset dengan warna merah
         
Line 143:         self.stop_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
         - Pack tombol reset di tengah dengan expand
         
Line 144:         self.stop_button.config(state=tk.DISABLED)
         - Disable tombol reset secara default
         
Line 145: (blank line)
         
Line 146:         self.capture_button = self.create_modern_button(button_frame, "Capture Image", "#ecc94b", self.capture_image)
         - Buat tombol capture dengan warna kuning
         
Line 147:         self.capture_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
         - Pack tombol capture di kanan dengan expand
         
Line 148: (blank line)
         
Line 149:         info_frame = tk.Frame(main_frame, bg="#e6ffed", bd=0, relief=tk.FLAT, width=450)
         - Buat frame untuk info panel dengan lebar 450px
         
Line 150:         info_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(15, 0))
         - Pack info frame di kanan dengan padding left 15px
         
Line 151: (blank line)
         
Line 152:         title_label = tk.Label(info_frame, text="Detection Info", 
         - Buat label title untuk info panel
         
Line 153:                               font=("Segoe UI", 20, "bold"), bg="#e6ffed", fg="#2f855a")
         - Set font Segoe UI bold size 20 dengan warna hijau gelap
         
Line 154:         title_label.pack(pady=(25, 20))
         - Pack title dengan padding
         
Line 155: (blank line)
         
Line 156:         separator = tk.Frame(info_frame, bg="#48bb78", height=2)
         - Buat separator line dengan tinggi 2px
         
Line 157:         separator.pack(fill=tk.X, padx=20, pady=(0, 20))
         - Pack separator dengan padding
         
Line 158: (blank line)
         
Line 159:         self.create_modern_info_card(info_frame, "Detected", "object_label", "#2f855a")
         - Buat info card untuk objek yang terdeteksi
         
Line 160:         self.create_modern_info_card(info_frame, "Category", "category_label", "#2f855a")
         - Buat info card untuk kategori
         
Line 161:         self.create_modern_info_card(info_frame, "Confidence", "confidence_label", "#2f855a")
         - Buat info card untuk confidence
         
Line 162:         self.create_modern_info_card(info_frame, "Decision Source", "source_label", "#2f855a")
         - Buat info card untuk sumber keputusan
         
Line 163:         self.create_modern_info_card(info_frame, "Stability", "stability_label", "#2f855a")
         - Buat info card untuk stability progress
         
Line 164:         self.create_modern_info_card(info_frame, "Serial Status", "serial_label", "#2f855a")
         - Buat info card untuk status serial
         
Line 165:         self.create_modern_info_card(info_frame, "Status", "status_label", "#2f855a")
         - Buat info card untuk status aplikasi
         
Line 166: (blank line)
         
Line 167:         model_frame = tk.Frame(info_frame, bg="#e6ffed")
         - Buat frame untuk info model
         
Line 168:         model_frame.pack(pady=15)
         - Pack dengan padding 15px
         
Line 169: (blank line)
         
Line 170:         self.model_status_label = tk.Label(model_frame, text="Model: Custom YOLO",
         - Buat label untuk status model
         
Line 171:                                           font=("Segoe UI", 10, "bold"), bg="#e6ffed", fg="#48bb78")
         - Set font bold size 10 dengan warna hijau
         
Line 172:         self.model_status_label.pack()
         - Pack label
         
Line 173: (blank line)
         
Line 174:         mode_text = "Microcontroller" if self.use_microcontroller else "Display Only"
         - Tentukan text mode berdasarkan flag
         
Line 175:         self.mode_status_label = tk.Label(model_frame, text=f"Mode: {mode_text}",
         - Buat label untuk status mode
         
Line 176:                                           font=("Segoe UI", 10, "bold"), bg="#e6ffed", fg="#48bb78")
         - Set font bold size 10 dengan warna hijau
         
Line 177:         self.mode_status_label.pack(pady=(5, 0))
         - Pack dengan padding top 5px
         
Line 178: (blank line)
```

### Lines 179-200: UI Helper Methods
```
Line 179:     def create_modern_info_card(self, parent, title, label_name, accent_color):
         - Method untuk membuat info card modern
         
Line 180:         card_frame = tk.Frame(parent, bg="#c6f6d5", bd=0, relief=tk.FLAT)
         - Buat frame card dengan background hijau muda
         
Line 181:         card_frame.pack(fill=tk.X, padx=20, pady=8)
         - Pack card dengan padding
         
Line 182: (blank line)
         
Line 183:         title_label = tk.Label(card_frame, text=title, font=("Segoe UI", 9, "bold"), 
         - Buat label untuk title card
         
Line 184:                               bg="#c6f6d5", fg="#2f855a", width=15, anchor=tk.W)
         - Set warna dan alignment left
         
Line 185:         title_label.pack(anchor=tk.W, padx=12, pady=(8, 2))
         - Pack title dengan padding
         
Line 186: (blank line)
         
Line 187:         value_label = tk.Label(card_frame, text="--", font=("Segoe UI", 14, "bold"), 
         - Buat label untuk nilai card
         
Line 188:                               bg="#c6f6d5", fg="#276749", anchor=tk.W, width=20)
         - Set font lebih besar dengan warna hijau gelap
         
Line 189:         value_label.pack(anchor=tk.W, padx=12, pady=(2, 8))
         - Pack value dengan padding
         
Line 190: (blank line)
         
Line 191:         setattr(self, label_name, value_label)
         - Simpan reference ke label sebagai attribute instance
         
Line 192: (blank line)
         
Line 193:     def create_modern_button(self, parent, text, color, command):
         - Method untuk membuat tombol modern
         
Line 194:         button = tk.Button(parent, text=text, font=("Segoe UI", 11, "bold"),
         - Buat tombol dengan font bold size 11
         
Line 195:                           bg=color, fg="white", activebackground=color,
         - Set warna background dan foreground
         
Line 196:                           activeforeground="white", relief=tk.RAISED,
         - Set active foreground dan relief
         
Line 197:                           cursor="hand2", padx=30, pady=14, command=command,
         - Set cursor hand2, padding, dan command
         
Line 198:                           bd=2, highlightthickness=0)
         - Set border width dan tanpa highlight
         
Line 199:         return button
         - Return object tombol
         
Line 200: (blank line)
```

### Lines 201-225: Camera Setup
```
Line 201:     def setup_camera(self):
         - Method untuk inisialisasi kamera
         
Line 202:         try:
         - Mulai try block untuk handle error kamera
         
Line 203:             self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
         - Coba buka kamera dengan DirectShow backend
         
Line 204:             if not self.cap.isOpened():
         - Cek jika kamera tidak terbuka
         
Line 205:                 self.cap = cv2.VideoCapture(0)
         - Coba buka dengan default backend
         
Line 206:                 if not self.cap.isOpened():
         - Cek lagi jika masih gagal
         
Line 207:                     raise Exception("Could not open camera with any backend")
         - Raise exception jika semua backend gagal
         
Line 208: (blank line)
         
Line 209:             self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
         - Set lebar frame ke 640 pixels
         
Line 210:             self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
         - Set tinggi frame ke 480 pixels
         
Line 211:             self.cap.set(cv2.CAP_PROP_FPS, 30)
         - Set FPS ke 30
         
Line 212:             self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
         - Set buffer size ke 1 untuk mengurangi latency
         
Line 213: (blank line)
         
Line 214:             ret, frame = self.cap.read()
         - Baca satu frame untuk test
         
Line 215:             if not ret or frame is None:
         - Cek jika gagal baca frame
         
Line 216:                 raise Exception("Camera opened but failed to read frame")
         - Raise exception jika frame tidak terbaca
         
Line 217: (blank line)
         
Line 218:             print("Camera initialized successfully")
         - Print pesan sukses
         
Line 219:         except Exception as e:
         - Catch exception jika error
         
Line 220:             print(f"Error initializing camera: {e}")
         - Print error message
         
Line 221:             if self.cap is not None:
         - Cek jika capture object ada
         
Line 222:                 self.cap.release()
         - Release kamera
         
Line 223:                 self.cap = None
         - Set capture object ke None
         
Line 224:             self.show_error(f"Camera Error: {e}")
         - Tampilkan error dialog
         
Line 225: (blank line)
```

### Lines 226-271: Detection Control Methods
```
Line 226:     def start_detection(self):
         - Method untuk memulai deteksi
         
Line 227:         if self.cap is None or not self.cap.isOpened():
         - Cek jika kamera tidak tersedia
         
Line 228:             self.show_error("Camera not available")
         - Tampilkan error dialog
         
Line 229:             return
         - Return early
         
Line 230: (blank line)
         
Line 231:         self.running = True
         - Set flag running ke True
         
Line 232:         self.start_button.config(state=tk.DISABLED)
         - Disable tombol start
         
Line 233:         self.stop_button.config(state=tk.NORMAL)
         - Enable tombol stop
         
Line 234: (blank line)
         
Line 235:         self.detection_thread = threading.Thread(target=self.detection_loop)
         - Buat thread baru untuk detection loop
         
Line 236:         self.detection_thread.daemon = True
         - Set sebagai daemon thread (auto kill saat main exit)
         
Line 237:         self.detection_thread.start()
         - Start thread deteksi
         
Line 238: (blank line)
         
Line 239:     def on_spacebar(self, event):
         - Handler untuk tombol spacebar
         
Line 240:         if self.running:
         - Cek jika deteksi sedang berjalan
         
Line 241:print("Spacebar pressed - restarting detection from beginning")
         - Print pesan restart
         
Line 242:             self.auto_detection = True
         - Set auto detection ke True
         
Line 243:             self.stop_detection()
         - Stop deteksi
         
Line 244:             self.start_detection()
         - Start deteksi lagi
         
Line 245: (blank line)
         
Line 246:     def stop_detection(self):
         - Method untuk stop deteksi
         
Line 247:         self.running = False
         - Set flag running ke False
         
Line 248:         self.start_button.config(state=tk.NORMAL)
         - Enable tombol start
         
Line 249:         self.stop_button.config(state=tk.DISABLED)
         - Disable tombol stop
         
Line 250: (blank line)
         
Line 251:         self.stability_counter = 0
         - Reset stability counter
         
Line 252:         self.last_detected_category = None
         - Reset last detected category
         
Line 253:         self.last_decision_time = 0
         - Reset last decision time
         
Line 254:         self.processing = False
         - Reset processing flag
         
Line 255:         self.last_detection_result = None
         - Reset last detection result
         
Line 256:         self.last_processed_object = None
         - Reset last processed object
         
Line 257:         self.last_processed_time = 0
         - Reset last processed time
         
Line 258:         self.capturing = False
         - Reset capturing flag
         
Line 259:         self.no_detection_start_time = 0
         - Reset no detection start time
         
Line 260:         self.frame_count = 0
         - Reset frame count
         
Line 261:         self.auto_detection = True
         - Reset auto detection flag
         
Line 262: (blank line)
         
Line 263:         self.object_label.config(text="--")
         - Reset object label
         
Line 264:         self.category_label.config(text="--")
         - Reset category label
         
Line 265:         self.source_label.config(text="--")
         - Reset source label
         
Line 266:         self.stability_label.config(text=f"0/{self.stability_frames_required} frames")
         - Reset stability label
         
Line 267:         self.status_label.config(text="Ready")
         - Reset status label
         
Line 268:         self.status_label.config(fg="#48bb78")
         - Reset status label color
         
Line 269: (blank line)
         
Line 270:         print("Detection stopped and reset to initial state")
         - Print pesan reset
         
Line 271: (blank line)
```

### Lines 272-366: Manual Capture Method
```
Line 272:     def capture_image(self):
         - Method untuk capture image manual
         
Line 273:         if self.cap is None or not self.cap.isOpened():
         - Cek jika kamera tidak tersedia
         
Line 274:             self.show_error("Camera not available")
         - Tampilkan error
         
Line 275:             return
         - Return early
         
Line 276: (blank line)
         
Line 277:         if self.capturing:
         - Cek jika sedang capturing
         
Line 278:             print("Already capturing, please wait...")
         - Print pesan tunggu
         
Line 279:             return
         - Return early
         
Line 280: (blank line)
         
Line 281:         self.capturing = True
         - Set capturing flag ke True
         
Line 282: (blank line)
         
Line 283:         self.no_detection_start_time = 0
         - Reset no detection start time
         
Line 284: (blank line)
         
Line 285:         self.root.after(0, lambda: self.status_label.config(text="Capturing..."))
         - Update status label ke "Capturing..."
         
Line 286:         self.root.after(0, lambda: self.status_label.config(fg="#ecc94b"))
         - Update status label color ke kuning
         
Line 287: (blank line)
         
Line 288:         try:
         - Mulai try block untuk capture
         
Line 289:             ret, frame = self.cap.read()
         - Baca frame dari kamera
         
Line 290:             if not ret or frame is None:
         - Cek jika gagal baca frame
         
Line 291:                 print("Warning: Failed to read frame, attempting to reconnect...")
         - Print warning
         
Line 292:                 self.cap.release()
         - Release kamera
         
Line 293:                 time.sleep(0.5)
         - Tunggu 0.5 detik
         
Line 294:                 self.setup_camera()
         - Re-setup kamera
         
Line 295:                 if self.cap is None or not self.cap.isOpened():
         - Cek jika re-setup gagal
         
Line 296:                     self.show_error("Camera reconnection failed")
         - Tampilkan error
         
Line 297:                     self.capturing = False
         - Reset capturing flag
         
Line 298:                     self.root.after(0, lambda: self.status_label.config(text="Ready"))
         - Reset status label
         
Line 299:                     self.root.after(0, lambda: self.status_label.config(fg="#48bb78"))
         - Reset status color
         
Line 300:                     return
         - Return early
         
Line 301:                 ret, frame = self.cap.read()
         - Coba baca frame lagi
         
Line 302:                 if not ret or frame is None:
         - Cek jika masih gagal
         
Line 303:                     self.show_error("Failed to capture image after reconnection")
         - Tampilkan error
         
Line 304:                     self.capturing = False
         - Reset capturing flag
         
Line 305:                     self.root.after(0, lambda: self.status_label.config(text="Ready"))
         - Reset status label
         
Line 306:                     self.root.after(0, lambda: self.status_label.config(fg="#48bb78"))
         - Reset status color
         
Line 307:                     return
         - Return early
         
Line 308: (blank line)
         
Line 309:             detection_result = self.detection_system.detect(frame, in_cooldown=False, manual_mode=True)
         - Jalankan deteksi pada frame dengan mode manual
         
Line 310:             print(f"Detection result: {detection_result}")
         - Print hasil deteksi
         
Line 311: (blank line)
         
Line 312:             frame_flipped = cv2.flip(frame, 0)
         - Flip frame secara vertikal
         
Line 313: (blank line)
         
Line 314:             if detection_result["current_category"]:
         - Cek jika ada kategori terdeteksi
         
Line 315:                 capture_folder = os.path.join(self.base_dir, "captures")
         - Buat path folder captures
         
Line 316:                 os.makedirs(capture_folder, exist_ok=True)
         - Buat folder jika belum ada
         
Line 317: (blank line)
         
Line 318:                 timestamp = int(time.time())
         - Dapatkan timestamp saat ini
         
Line 319:                 capture_path = os.path.join(capture_folder, f"capture_{timestamp}.jpg")
         - Buat path file capture
         
Line 320:                 cv2.imwrite(capture_path, frame_flipped)
         - Simpan gambar ke file
         
Line 321:                 print(f"Image captured: {capture_path}")
         - Print path gambar
         
Line 322:                 print(f"YOLO Confidence: {detection_result['best_confidence']:.2f}")
         - Print confidence score
         
Line 323: (blank line)
         
Line 324:                 detection_result["decision_source"] = "Manual"
         - Set sumber keputusan ke "Manual"
         
Line 325: (blank line)
         
Line 326:                 self.last_detection_result = detection_result.copy()
         - Simpan copy hasil deteksi
         
Line 327: (blank line)
         
Line 328:                 if detection_result["current_category"]:
         - Cek jika ada kategori
         
Line 329:                     success = self.serial_comm.send_command(detection_result["current_category"])
         - Kirim command ke Arduino
         
Line 330:                     if success:
         - Cek jika berhasil kirim
         
Line 331:                         print(f"Serial command sent: {detection_result['current_category']}")
         - Print command yang dikirim
         
Line 332: (blank line)
         
Line 333:                 self.last_processed_object = detection_result["best_class"]
         - Simpan objek terakhir
         
Line 334:                 self.last_processed_time = time.time()
         - Simpan waktu proses
         
Line 335: (blank line)
         
Line 336:                 current_time = cv2.getTickCount() / cv2.getTickFrequency()
         - Dapatkan current time
         
Line 337:                 self.update_gui(frame_flipped, detection_result, False, current_time)
         - Update GUI dengan hasil
         
Line 338: (blank line)
         
Line 339:                 self.auto_detection = False
         - Disable auto detection
         
Line 340:                 print("Manual capture completed. Detection result displayed. Press SPACE to restart detection.")
         - Print instruksi
         
Line 341:             else:
         - Jika tidak ada deteksi
         
Line 342:                 print("No detection in manual capture")
         - Print pesan no detection
         
Line 343:                 self.root.after(0, lambda: self.status_label.config(text="No Detection"))
         - Update status label
         
Line 344:                 self.root.after(0, lambda: self.status_label.config(fg="#e53e3e"))
         - Update status color ke merah
         
Line 345: (blank line)
         
Line 346:                 no_detection_result = {
         - Buat result kosong
         
Line 347:                     "best_class": None,
         - Set best class ke None
         
Line 348:                     "best_confidence": 0.0,
         - Set confidence ke 0
         
Line 349:                     "best_box": None,
         - Set box ke None
         
Line 350:                     "current_category": None,
         - Set category ke None
         
Line 351:                     "decision_source": "No Detection"
         - Set source ke "No Detection"
         
Line 352:                 }
         - Tutup dictionary
         
Line 353:                 current_time = cv2.getTickCount() / cv2.getTickFrequency()
         - Dapatkan current time
         
Line 354:                 self.update_gui(frame_flipped, no_detection_result, False, current_time)
         - Update GUI dengan result kosong
         
Line 355: (blank line)
         
Line 356:                 self.show_retry_dialog()
         - Tampilkan dialog retry
         
Line 357: (blank line)
         
Line 358:                 self.auto_detection = False
         - Disable auto detection
         
Line 359:         except Exception as e:
         - Catch exception jika error
         
Line 360:             print(f"Error during capture: {e}")
         - Print error
         
Line 361:             self.show_error(f"Capture Error: {e}")
         - Tampilkan error dialog
         
Line 362:             self.root.after(0, lambda: self.status_label.config(text="Error"))
         - Update status ke Error
         
Line 363:             self.root.after(0, lambda: self.status_label.config(fg="#e53e3e"))
         - Update color ke merah
         
Line 364: (blank line)
         
Line 365:         self.capturing = False
         - Reset capturing flag
         
Line 366: (blank line)
```

### Lines 367-493: Detection Loop
```
Line 367:     def detection_loop(self):
         - Method untuk loop deteksi otomatis (berjalan di thread)
         
Line 368:         while self.running:
         - Loop selama running True
         
Line 369:             try:
         - Mulai try block untuk baca frame
         
Line 370:                 ret, frame = self.cap.read()
         - Baca frame dari kamera
         
Line 371:                 if not ret or frame is None:
         - Cek jika gagal baca
         
Line 372:                     print("Warning: Failed to read frame, attempting to reconnect...")
         - Print warning
         
Line 373:                     self.cap.release()
         - Release kamera
         
Line 374:                     time.sleep(0.5)
         - Tunggu 0.5 detik
         
Line 375:                     self.setup_camera()
         - Re-setup kamera
         
Line 376:                     if self.cap is None or not self.cap.isOpened():
         - Cek jika re-setup gagal
         
Line 377:                         print("Camera reconnection failed, stopping detection")
         - Print pesan stop
         
Line 378:                         break
         - Break loop
         
Line 379:                     continue
         - Continue loop
         
Line 380:             except Exception as e:
         - Catch exception
         
Line 381:                 print(f"Error reading frame: {e}")
         - Print error
         
Line 382:                 self.cap.release()
         - Release kamera
         
Line 383:                 time.sleep(0.5)
         - Tunggu 0.5 detik
         
Line 384:                 self.setup_camera()
         - Re-setup kamera
         
Line 385:                 if self.cap is None or not self.cap.isOpened():
         - Cek jika gagal
         
Line 386:                         print("Camera reconnection failed, stopping detection")
         - Print pesan stop
         
Line 387:                         break
         - Break loop
         
Line 388:                     continue
         - Continue loop
         
Line 389: (blank line)
         
Line 390:             self.frame_count += 1
         - Increment frame counter
         
Line 391:             current_time = cv2.getTickCount() / cv2.getTickFrequency()
         - Dapatkan current time
         
Line 392: (blank line)
         
Line 393:             in_cooldown = (current_time - self.cooldown_start_time) < self.cooldown_duration
         - Cek jika dalam cooldown period
         
Line 394: (blank line)
         
Line 395:             if not self.auto_detection:
         - Cek jika auto detection disabled
         
Line 396:                 frame_flipped = cv2.flip(frame, 0)
         - Flip frame
         
Line 397:                 if self.last_detection_result:
         - Cek jika ada hasil terakhir
         
Line 398:                     detection_result = self.last_detection_result.copy()
         - Copy hasil terakhir
         
Line 399:                     detection_result["decision_source"] = "Last Detection (Paused)"
         - Set source ke paused
         
Line 400:                 else:
         - Jika tidak ada hasil
         
Line 401:                     detection_result = {
         - Buat result kosong
         
Line 402:                         "best_class": None,
         - Set None
         
Line 403:                         "best_confidence": 0.0,
         - Set 0
         
Line 404:                         "best_box": None,
         - Set None
         
Line 405:                        "current_category": None,
         - Set None
         
Line 406:                        "decision_source": "Camera Only Mode"
         - Set source
         
Line 407:                     }
         - Tutup dictionary
         
Line 408:                 self.update_gui(frame_flipped, detection_result, False, current_time)
         - Update GUI
         
Line 409:                 continue
         - Continue loop
         
Line 410: (blank line)
         
Line 411:             if self.processing:
         - Cek jika sedang processing
         
Line 412:                 done_signal = self.serial_comm.read_done_signal()
         - Baca sinyal done dari Arduino
         
Line 413:                 if done_signal:
         - Cek jika Arduino selesai
         
Line 414:                     self.processing = False
         - Reset processing flag
         
Line 415:                     self.cooldown_start_time = current_time
         - Start cooldown
         
Line 416:                     self.auto_detection = False
         - Disable auto detection
         
Line 417:                     print("Automatic detection completed. Result displayed. Press SPACE to restart detection.")
         - Print instruksi
         
Line 418: (blank line)
         
Line 419:             if not self.processing:
         - Cek jika tidak sedang processing
         
Line 420:                 if self.frame_count % 3 == 0:
         - Proses setiap 3 frame (untuk optimasi)
         
Line 421:                     detection_result = self.detection_system.detect(frame, in_cooldown, manual_mode=False)
         - Jalankan deteksi auto mode
         
Line 422: (blank line)
         
Line 423:                     if detection_result["best_class"] and not in_cooldown:
         - Cek jika ada deteksi dan tidak dalam cooldown
         
Line 424:                         if (detection_result["best_class"] == self.last_processed_object and 
         - Cek jika objek sama dengan yang terakhir diproses
         
Line 425:                             (current_time - self.last_processed_time) < 2.0):
         - Dan dalam 2 detik terakhir
         
Line 426:                             self.stability_counter = 0
         - Reset stability counter (prevent spam)
         
Line 427:                         elif detection_result["best_class"] == self.last_detected_category:
         - Cek jika sama dengan kategori terakhir
         
Line 428:                             self.stability_counter += 1
         - Increment stability counter
         
Line 429:                         else:
         - Jika berbeda
         
Line 430:                             self.stability_counter = 1
         - Reset ke 1
         
Line 431:                             self.last_detected_category = detection_result["best_class"]
         - Update kategori terakhir
         
Line 432: (blank line)
         
Line 433:                         detection_result["stability_progress"] = f"{self.stability_counter}/{self.stability_frames_required}"
         - Set progress stability
         
Line 434: (blank line)
         
Line 435:                         if self.stability_counter >= self.stability_frames_required:
         - Cek jika stability cukup (3 frame)
         
Line 436:                             detection_folder = os.path.join(self.base_dir, "detections")
         - Buat path folder detections
         
Line 437:                             os.makedirs(detection_folder, exist_ok=True)
         - Buat folder jika belum ada
         
Line 438: (blank line)
         
Line 439:                             frame_flipped = cv2.flip(frame, 0)
         - Flip frame
         
Line 440:                             capture_path = os.path.join(detection_folder, f"detection_{int(current_time)}.jpg")
         - Buat path file
         
Line 441:                             cv2.imwrite(capture_path, frame_flipped)
         - Simpan gambar
         
Line 442:                             print(f"Image captured: {capture_path}")
         - Print path
         
Line 443:                             print(f"YOLO Confidence: {detection_result['best_confidence']:.2f}")
         - Print confidence
         
Line 444: (blank line)
         
Line 445:                             self.processing = True
         - Set processing ke True
         
Line 446: (blank line)
         
Line 447:                             self.stability_counter = 0
         - Reset stability counter
         
Line 448:                             self.last_detected_category = None
         - Reset kategori terakhir
         
Line 449: (blank line)
         
Line 450:                             detection_result["decision_source"] = "Automatic"
         - Set source ke Automatic
         
Line 451: (blank line)
         
Line 452:                             self.last_processed_object = detection_result["best_class"]
         - Simpan objek terakhir
         
Line 453:                             self.last_processed_time = current_time
         - Simpan waktu
         
Line 454: (blank line)
         
Line 455:                             self.last_detection_result = detection_result.copy()
         - Simpan copy result
         
Line 456: (blank line)
         
Line 457:                             if detection_result["current_category"]:
         - Cek jika ada kategori
         
Line 458:                                 success = self.serial_comm.send_command(detection_result["current_category"])
         - Kirim command ke Arduino
         
Line 459:                                 if success:
         - Cek jika berhasil
         
Line 460:                                     self.last_decision_time = current_time
         - Simpan waktu keputusan
         
Line 461:                                     self.stability_counter = 0
         - Reset counter
         
Line 462:                                     self.last_detected_category = None
         - Reset kategori
         
Line 463:                             else:
         - Jika tidak ada kategori
         
Line 464:                                 detection_result["decision_source"] = "No Detection"
         - Set source
         
Line 465:                                 print("No detection in automatic mode")
         - Print pesan
         
Line 466:                                 print("Waiting 3 seconds to restart...")
         - Print pesan tunggu
         
Line 467:                                 time.sleep(3)
         - Tunggu 3 detik
         
Line 468:                                 self.stability_counter = 0
         - Reset counter
         
Line 469:                                 self.last_detected_category = None
         - Reset kategori
         
Line 470:                                 self.processing = False
         - Reset processing
         
Line 471:                 else:
         - Jika bukan frame ke-3
         
Line 472:                     detection_result = {
         - Buat result kosong
         
Line 473:                         "best_class": None,
         - Set None
         
Line 474:                         "best_confidence": 0.0,
         - Set 0
         
Line 475:                         "best_box": None,
         - Set None
         
Line 476:                        "current_category": None,
         - Set None
         
Line 477:                        "decision_source": "None"
         - Set source
         
Line 478:                     }
         - Tutup dictionary
         
Line 479:             else:
         - Jika sedang processing
         
Line 480:                 if self.last_detection_result:
         - Cek jika ada result terakhir
         
Line 481:                     detection_result = self.last_detection_result.copy()
         - Copy result
         
Line 482:                 else:
         - Jika tidak ada
         
Line 483:                     detection_result = {
                         - Buat result kosong
                         
Line 484:                         "best_class": None,
                         - Set None
                         
Line 485:                         "best_confidence": 0.0,
                         - Set 0
                         
Line 486:                         "best_box": None,
                         - Set None
                         
Line 487:                        "current_category": None,
                         - Set None
                         
Line 488:                        "decision_source": "Processing..."
                         - Set source
                         
Line 489:                     }
                         - Tutup dictionary
                         
Line 490: (blank line)
Line 491:             frame_flipped = cv2.flip(frame, 0)
         - Flip frame
         
Line 492:             self.update_gui(frame_flipped, detection_result, in_cooldown, current_time)
         - Update GUI
         
Line 493: (blank line)
```

### Lines 494-541: GUI Update Method
```
Line 494:     def update_gui(self, frame, detection_result, in_cooldown, current_time):
         - Method untuk update GUI dengan frame dan hasil deteksi
         
Line 495:         if detection_result["best_box"] is not None:
         - Cek jika ada bounding box
         
Line 496:             x1, y1, x2, y2 = map(int, detection_result["best_box"])
         - Extract dan convert koordinat box ke integer
         
Line 497:             cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
         - Gambar rectangle hijau pada frame
         
Line 498: (blank line)
         
Line 499:         frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
         - Convert frame dari BGR ke RGB
         
Line 500:         frame_resized = cv2.resize(frame_rgb, (640, 480))
         - Resize frame ke 640x480
         
Line 501: (blank line)
         
Line 502:         image = Image.fromarray(frame_resized)
         - Convert numpy array ke PIL Image
         
Line 503:         photo = ImageTk.PhotoImage(image=image)
         - Convert PIL Image ke Tkinter PhotoImage
         
Line 504: (blank line)
         
Line 505:         self.root.after(0, lambda: self.video_label.config(image=photo))
         - Update video label dengan gambar
         
Line 506:         self.root.after(0, lambda: setattr(self.video_label, 'image', photo))
         - Simpan reference ke photo untuk prevent garbage collection
         
Line 507: (blank line)
         
Line 508:         obj_text = "terdeteksi" if detection_result["best_class"] else "None"
         - Tentukan text objek
         
Line 509:         cat_text = detection_result["current_category"] if detection_result["current_category"] else "None"
         - Tentukan text kategori
         
Line 510:         conf_text = f"{detection_result['best_confidence']:.2%}" if detection_result["best_confidence"] > 0 else "0%"
         - Format confidence ke percentage
         
Line 511:         source_text = detection_result["decision_source"]
         - Ambil text source
         
Line 512: (blank line)
         
Line 513:         if self.last_detected_category:
         - Cek jika ada kategori terakhir
         
Line 514:             stab_text = f"{min(self.stability_counter, self.stability_frames_required)}/{self.stability_frames_required} frames"
         - Format text stability
         
Line 515:         elif "stability_progress" in detection_result:
         - Cek jika ada progress di result
         
Line 516:             stab_text = f"{detection_result['stability_progress']} frames"
         - Gunakan progress dari result
         
Line 517:         else:
         - Jika tidak ada
         
Line 518:             stab_text = f"0/{self.stability_frames_required} frames"
         - Set ke 0
         
Line 519: (blank line)
         
Line 520:         serial_text = "Connected" if self.serial_comm.connected else "Disconnected"
         - Tentukan text serial status
         
Line 521: (blank line)
         
Line 522:         if self.processing:
         - Cek jika sedang processing
         
Line 523:             status_text = "Processing..."
         - Set status text
         
Line 524:         elif in_cooldown:
         - Cek jika dalam cooldown
         
Line 525:             cooldown_remaining = self.cooldown_duration - (current_time - self.cooldown_start_time)
         - Hitung sisa cooldown
         
Line 526:             status_text = f"Cooldown: {cooldown_remaining:.1f}s"
         - Format status text
         
Line 527:         else:
         - Jika tidak processing dan tidak cooldown
         
Line 528:             status_text = "Ready"
         - Set status ke Ready
         
Line 529: (blank line)
         
Line 530:         def update_all():
         - Inner function untuk update semua label
         
Line 531:             self.object_label.config(text=obj_text)
         - Update object label
         
Line 532:             self.category_label.config(text=cat_text)
         - Update category label
         
Line 533:             self.confidence_label.config(text=conf_text)
         - Update confidence label
         
Line 534:             self.source_label.config(text=source_text)
         - Update source label
         
Line 535:             self.stability_label.config(text=stab_text)
         - Update stability label
         
Line 536:             self.serial_label.config(text=serial_text)
         - Update serial label
         
Line 537:             self.status_label.config(text=status_text)
         - Update status label
         
Line 538:             self.status_label.config(fg="#ecc94b" if self.processing else "#48bb78")
         - Update status color (kuning jika processing, hijau jika ready)
         
Line 539: (blank line)
         
Line 540:         self.root.after(0, update_all)
         - Schedule update_all di main thread
         
Line 541: (blank line)
```

### Lines 542-607: Dialog Methods
```
Line 542:     def show_error(self, message):
         - Method untuk menampilkan error dialog
         
Line 543:         error_window = tk.Toplevel(self.root)
         - Buat new top-level window
         
Line 544:         error_window.title("Error")
         - Set judul window
         
Line 545:         error_window.geometry("450x200")
         - Set ukuran window
         
Line 546:         error_window.configure(bg="#e53e3e")
         - Set background merah
         
Line 547: (blank line)
         
Line 548:         error_window.update_idletasks()
         - Force update window geometry
         
Line 549:         width = error_window.winfo_width()
         - Dapatkan lebar window
         
Line 550:         height = error_window.winfo_height()
         - Dapatkan tinggi window
         
Line 551:         x = (error_window.winfo_screenwidth() // 2) - (width // 2)
         - Hitung posisi x untuk center
         
Line 552:         y = (error_window.winfo_screenheight() // 2) - (height // 2)
         - Hitung posisi y untuk center
         
Line 553:         error_window.geometry(f'{width}x{height}+{x}+{y}')
         - Set posisi window di center screen
         
Line 554: (blank line)
         
Line 555:         error_label = tk.Label(error_window, text=message, font=("Segoe UI", 12),
         - Buat label untuk error message
         
Line 556:                                bg="#e53e3e", fg="white", wraplength=400)
         - Set warna dan wrap text
         
Line 557:         error_label.pack(expand=True, padx=25, pady=25)
         - Pack label dengan padding
         
Line 558: (blank line)
         
Line 559:         close_button = tk.Button(error_window, text="OK", font=("Segoe UI", 11, "bold"),
         - Buat tombol OK
         
Line 560:                                 bg="white", fg="#e53e3e", activebackground="#fed7d7",
         - Set warna tombol
         
Line 561:                                 activeforeground="#e53e3e", relief=tk.RAISED,
         - Set active colors dan relief
         
Line 562:                                 cursor="hand2", padx=30, pady=8,
         - Set cursor dan padding
         
Line 563:                                 command=error_window.destroy,
         - Set command untuk destroy window
         
Line 564:                                 bd=2, highlightthickness=0)
         - Set border dan highlight
         
Line 565:         close_button.pack(pady=(0, 15))
         - Pack tombol dengan padding
         
Line 566: (blank line)
         
Line 567:     def show_retry_dialog(self):
         - Method untuk menampilkan dialog retry
         
Line 568:         retry_window = tk.Toplevel(self.root)
         - Buat new top-level window
         
Line 569:         retry_window.title("Retry Capture")
         - Set judul
         
Line 570:         retry_window.geometry("400x200")
         - Set ukuran
         
Line 571:         retry_window.configure(bg="#f0fff4")
         - Set background hijau muda
         
Line 572: (blank line)
         
Line 573:         retry_window.update_idletasks()
         - Force update geometry
         
Line 574:         width = retry_window.winfo_width()
         - Dapatkan lebar
         
Line 575:         height = retry_window.winfo_height()
         - Dapatkan tinggi
         
Line 576:         x = (retry_window.winfo_screenwidth() // 2) - (width // 2)
         - Hitung posisi x
         
Line 577:         y = (retry_window.winfo_screenheight() // 2) - (height // 2)
         - Hitung posisi y
         
Line 578:         retry_window.geometry(f'{width}x{height}+{x}+{y}')
         - Set posisi center
         
Line 579: (blank line)
         
Line 580:         message_label = tk.Label(retry_window, text="No object detected.\nWould you like to try again?",
         - Buat label message
         
Line 581:                                  font=("Segoe UI", 12), bg="#f0fff4", fg="#276749")
         - Set font dan warna
         
Line 582:         message_label.pack(expand=True, padx=25, pady=25)
         - Pack dengan padding
         
Line 583: (blank line)
         
Line 584:         button_frame = tk.Frame(retry_window, bg="#f0fff4")
         - Buat frame untuk tombol
         
Line 585:         button_frame.pack(pady=10)
         - Pack frame
         
Line 586: (blank line)
         
Line 587:         def on_retry():
         - Inner function untuk retry
         
Line 588:             retry_window.destroy()
         - Tutup dialog
         
Line 589:             self.capture_image()
         - Panggil capture_image lagi
         
Line 590: (blank line)
         
Line 591:         def on_cancel():
         - Inner function untuk cancel
         
Line 592:             retry_window.destroy()
         - Tutup dialog
         
Line 593: (blank line)
         
Line 594:         retry_button = tk.Button(button_frame, text="Retry", font=("Segoe UI", 11, "bold"),
         - Buat tombol Retry
         
Line 595:                                  bg="#48bb78", fg="white", activebackground="#38a169",
         - Set warna hijau
         
Line 596:                                  activeforeground="white", relief=tk.RAISED,
         - Set active colors
         
Line 597:                                  cursor="hand2", padx=25, pady=10, command=on_retry,
         - Set cursor dan command
         
Line 598:                                  bd=2, highlightthickness=0)
         - Set border
         
Line 599:         retry_button.pack(side=tk.LEFT, padx=5)
         - Pack di kiri
         
Line 600: (blank line)
         
Line 601:         cancel_button = tk.Button(button_frame, text="Cancel", font=("Segoe UI", 11, "bold"),
         - Buat tombol Cancel
         
Line 602:                                   bg="#e53e3e", fg="white", activebackground="#c53030",
         - Set warna merah
         
Line 603:                                   activeforeground="white", relief=tk.RAISED,
         - Set active colors
         
Line 604:                                   cursor="hand2", padx=25, pady=10, command=on_cancel,
         - Set cursor dan command
         
Line 605:                                   bd=2, highlightthickness=0)
         - Set border
         
Line 606:         cancel_button.pack(side=tk.LEFT, padx=5)
         - Pack di kanan
         
Line 607: (blank line)
```

### Lines 608-644: Cleanup and Navigation
```
Line 608:     def cleanup(self):
         - Method untuk cleanup resources
         
Line 609:         self.stop_detection()
         - Stop deteksi
         
Line 610:         if self.cap is not None:
         - Cek jika kamera ada
         
Line 611:             self.cap.release()
         - Release kamera
         
Line 612:         self.serial_comm.close()
         - Tutup serial connection
         
Line 613: (blank line)
         
Line 614:     def go_back_to_mode_selection(self):
         - Method untuk kembali ke mode selection
         
Line 615:         self.cleanup()
         - Cleanup resources
         
Line 616:         self.root.destroy()
         - Destroy current window
         
Line 617: (blank line)
         
Line 618:         use_microcontroller = select_mode()
         - Panggil select_mode untuk pilih mode lagi
         
Line 619: (blank line)
         
Line 620:         if use_microcontroller is None:
         - Cek jika user cancel
         
Line 621:             print("No mode selected, exiting...")
         - Print pesan exit
         
Line 622:             return
         - Return
         
Line 623: (blank line)
         
Line 624:         print("Initializing detection system...")
         - Print pesan inisialisasi
         
Line 625:         from src.detection import DetectionSystem
         - Import DetectionSystem
         
Line 626:         detection_system = DetectionSystem()
         - Buat instance DetectionSystem
         
Line 627: (blank line)
         
Line 628:         print("Initializing serial communication...")
         - Print pesan serial
         
Line 629:         serial_comm = SerialComm(enabled=use_microcontroller)
         - Buat SerialComm dengan mode yang dipilih
         
Line 630: (blank line)
         
Line 631:         root = tk.Tk()
         - Buat new Tk root
         
Line 632:         gui = SmartBinGUI(root, detection_system, serial_comm, use_microcontroller)
         - Buat instance GUI baru
         
Line 633: (blank line)
         
Line 634:         def on_closing():
         - Inner function untuk handle window close
         
Line 635:             gui.cleanup()
         - Cleanup
         
Line 636:             root.destroy()
         - Destroy window
         
Line 637: (blank line)
         
Line 638:         root.protocol("WM_DELETE_WINDOW", on_closing)
         - Bind close event ke handler
         
Line 639: (blank line)
         
Line 640:         print("Starting GUI...")
         - Print pesan start
         
Line 641:         root.mainloop()
         - Start mainloop
         
Line 642: (blank line)
         
Line 643:         print("Application terminated.")
         - Print pesan terminated
         
Line 644: (blank line)
```

### Lines 646-732: Info Dialog
```
Line 646: def show_info_dialog():
         - Function untuk menampilkan dialog info project
         
Line 647:     info_window = tk.Toplevel()
         - Buat top-level window
         
Line 648:     info_window.title("Project Info")
         - Set judul
         
Line 649:     info_window.geometry("800x650")
         - Set ukuran
         
Line 650:     info_window.configure(bg="#f0fff4")
         - Set background
         
Line 651: (blank line)
         
Line 652:     info_window.update_idletasks()
         - Force update geometry
         
Line 653:     width = info_window.winfo_width()
         - Dapatkan lebar
         
Line 654:     height = info_window.winfo_height()
         - Dapatkan tinggi
         
Line 655:     x = (info_window.winfo_screenwidth() // 2) - (width // 2)
         - Hitung posisi x
         
Line 656:     y = (info_window.winfo_screenheight() // 2) - (height // 2)
         - Hitung posisi y
         
Line 657:     info_window.geometry(f'{width}x{height}+{x}+{y}')
         - Set posisi center
         
Line 658: (blank line)
         
Line 659:     main_frame = tk.Frame(info_window, bg="#f0fff4")
         - Buat main frame
         
Line 660:     main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
         - Pack dengan padding
         
Line 661: (blank line)
         
Line 662:     title_label = tk.Label(main_frame, text="SMARTBIN", 
         - Buat label title
         
Line 663:                          font=("Segoe UI", 28, "bold"), bg="#f0fff4", fg="#2f855a")
         - Set font besar bold
         
Line 664:     title_label.pack(pady=(0, 5))
         - Pack dengan padding
         
Line 665: (blank line)
         
Line 666:     subtitle_label = tk.Label(main_frame, text="Automatic Waste Sorter System", 
         - Buat label subtitle
         
Line 667:                               font=("Segoe UI", 14), bg="#f0fff4", fg="#48bb78")
         - Set font medium
         
Line 668:     subtitle_label.pack(pady=(0, 25))
         - Pack dengan padding
         
Line 669: (blank line)
         
Line 670:     separator = tk.Frame(main_frame, bg="#48bb78", height=2)
         - Buat separator
         
Line 671:     separator.pack(fill=tk.X, pady=(0, 20))
         - Pack separator
         
Line 672: (blank line)
         
Line 673:     sections_frame = tk.Frame(main_frame, bg="#f0fff4")
         - Buat frame untuk sections
         
Line 674:     sections_frame.pack(fill=tk.BOTH, expand=True)
         - Pack dengan expand
         
Line 675: (blank line)
         
Line 676:     def create_section(parent, title, content, color):
         - Inner function untuk membuat section
         
Line 677:         frame = tk.Frame(parent, bg="#e6ffed", bd=1, relief=tk.SOLID)
         - Buat frame section
         
Line 678:         frame.pack(fill=tk.X, pady=8)
         - Pack section
         
Line 679: (blank line)
         
Line 680:         header = tk.Frame(frame, bg=color)
         - Buat header frame
         
Line 681:         header.pack(fill=tk.X)
         - Pack header
         
Line 682: (blank line)
         
Line 683:         title_label = tk.Label(header, text=title, font=("Segoe UI", 11, "bold"),
         - Buat label title
         
Line 684:                               bg=color, fg="white", padx=15, pady=8)
         - Set warna
         
Line 685:         title_label.pack(side=tk.LEFT)
         - Pack di kiri
         
Line 686: (blank line)
         
Line 687:         content_frame = tk.Frame(frame, bg="#e6ffed")
         - Buat frame content
         
Line 688:         content_frame.pack(fill=tk.X, padx=15, pady=10)
         - Pack content
         
Line 689: (blank line)
         
Line 690:         for line in content:
         - Loop untuk setiap line content
         
Line 691:             label = tk.Label(content_frame, text=line, font=("Segoe UI", 10),
         - Buat label untuk line
         
Line 692:                            bg="#e6ffed", fg="#276749", anchor=tk.W)
         - Set warna dan alignment
         
Line 693:             label.pack(fill=tk.X, pady=2)
         - Pack label
         
Line 694: (blank line)
         
Line 695:     create_section(sections_frame, "Dataset", [
         - Buat section Dataset
         
Line 696:         "Source: Roboflow Custom Dataset",
         - Line 1
         
Line 697:         "Total Images: 314 images across 3 classes",
         - Line 2
         
Line 698:         "Classes: Organik (103), Non-Organik (111), Sampah Berbahaya (100)"
         - Line 3
         
Line 699:     ], "#48bb78")
         - Warna header hijau
         
Line 700: (blank line)
         
Line 701:     create_section(sections_frame, "Model", [
         - Buat section Model
         
Line 702:         "Architecture: YOLOv8n (Nano)",
         - Line 1
         
Line 703:         "Framework: Ultralytics",
         - Line 2
         
Line 704:         "Training: Custom trained on waste classification dataset",
         - Line 3
         
Line 705:         "Input Size: 416x416 pixels"
         - Line 4
         
Line 706:     ], "#38a169")
         - Warna header hijau gelap
         
Line 707: (blank line)
         
Line 708:     create_section(sections_frame, "Features", [
         - Buat section Features
         
Line 709:         "Real-time object detection with YOLO",
         - Line 1
         
Line 710:         "Stability check system (3 consecutive frames)",
         - Line 2
         
Line 711:         "Automatic & Manual capture modes",
         - Line 3
         
Line 712:         "Cooldown mechanism to prevent spam detection",
         - Line 4
         
Line 713:         "Serial communication with Arduino (COM4, 115200 baud)",
         - Line 5
         
Line 714:         "Confidence display with percentage format"
         - Line 6
         
Line 715:     ], "#2f855a")
         - Warna header lebih gelap
         
Line 716: (blank line)
         
Line 717:     create_section(sections_frame, "Usage", [
         - Buat section Usage
         
Line 718:         "Start Detection: Automatic detection loop",
         - Line 1
         
Line 719:         "Capture Image: Single-frame manual capture",
         - Line 2
         
Line 720:         "Reset: Stop and reset detection",
         - Line 3
         
Line 721:         "SPACE: Restart detection anytime",
         - Line 4
         
Line 722:         "Back: Return to mode selection"
         - Line 5
         
Line 723:     ], "#276749")
         - Warna header paling gelap
         
Line 724: (blank line)
         
Line 725:     close_button = tk.Button(main_frame, text="Close", font=("Segoe UI", 12, "bold"),
         - Buat tombol Close
         
Line 726:                              bg="#48bb78", fg="white", activebackground="#38a169",
         - Set warna
         
Line 727:                              activeforeground="white", relief=tk.RAISED,
         - Set active colors
         
Line 728:                              cursor="hand2", padx=40, pady=12,
         - Set cursor dan padding
         
Line 729:                              command=info_window.destroy,
         - Set command
         
Line 730:                              bd=2, highlightthickness=0)
         - Set border
         
Line 731:     close_button.pack(pady=(20, 0))
         - Pack tombol
         
Line 732: (blank line)
```

### Lines 734-831: Mode Selection and Main
```
Line 734: def select_mode():
         - Function untuk dialog selection mode
         
Line 735:     dialog = tk.Tk()
         - Buat new Tk window
         
Line 736:     dialog.title("Select Mode")
         - Set judul
         
Line 737:     dialog.geometry("500x350")
         - Set ukuran
         
Line 738:     dialog.configure(bg="#f0fff4")
         - Set background
         
Line 739: (blank line)
         
Line 740:     dialog.update_idletasks()
         - Force update geometry
         
Line 741:     width = dialog.winfo_width()
         - Dapatkan lebar
         
Line 742:     height = dialog.winfo_height()
         - Dapatkan tinggi
         
Line 743:     x = (dialog.winfo_screenwidth() // 2) - (width // 2)
         - Hitung posisi x
         
Line 744:     y = (dialog.winfo_screenheight() // 2) - (height // 2)
         - Hitung posisi y
         
Line 745:     dialog.geometry(f'{width}x{height}+{x}+{y}')
         - Set posisi center
         
Line 746: (blank line)
         
Line 747:     selected_mode = [None]
         - List untuk menyimpan pilihan mode (mutable)
         
Line 748: (blank line)
         
Line 749:     def on_microcontroller():
         - Inner function untuk pilih microcontroller
         
Line 750:         selected_mode[0] = True
         - Set mode ke True
         
Line 751:         dialog.destroy()
         - Tutup dialog
         
Line 752: (blank line)
         
Line 753:     def on_display_only():
         - Inner function untuk pilih display only
         
Line 754:         selected_mode[0] = False
         - Set mode ke False
         
Line 755:         dialog.destroy()
         - Tutup dialog
         
Line 756: (blank line)
         
Line 757:     def on_info():
         - Inner function untuk show info
         
Line 758:         show_info_dialog()
         - Panggil show_info_dialog
         
Line 759: (blank line)
         
Line 760:     title_label = tk.Label(dialog, text="SMARTBIN - Mode Selection",
         - Buat label title
         
Line 761:                           font=("Segoe UI", 18, "bold"), bg="#f0fff4", fg="#2f855a")
         - Set font dan warna
         
Line 762:     title_label.pack(pady=(30, 20))
         - Pack dengan padding
         
Line 763: (blank line)
         
Line 764:     desc_label = tk.Label(dialog, text="Select output mode for the application:",
         - Buat label deskripsi
         
Line 765:                           font=("Segoe UI", 11), bg="#f0fff4", fg="#276749")
         - Set font dan warna
         
Line 766:     desc_label.pack(pady=(0, 20))
         - Pack dengan padding
         
Line 767: (blank line)
         
Line 768:     button_frame = tk.Frame(dialog, bg="#f0fff4")
         - Buat frame untuk tombol
         
Line 769:     button_frame.pack(pady=10)
         - Pack frame
         
Line 770: (blank line)
         
Line 771:     mcu_button = tk.Button(button_frame, text="Microcontroller\n(With Arduino)",
         - Buat tombol Microcontroller
         
Line 772:                           font=("Segoe UI", 11, "bold"),
         - Set font
         
Line 773:                           bg="#48bb78", fg="white", activebackground="#38a169",
         - Set warna hijau
         
Line 774:                           activeforeground="white", relief=tk.RAISED,
         - Set active colors
         
Line 775:                           cursor="hand2", padx=25, pady=12, command=on_microcontroller,
         - Set cursor dan command
         
Line 776:                           bd=2, highlightthickness=0, width=18)
         - Set border dan width
         
Line 777:     mcu_button.pack(side=tk.LEFT, padx=8)
         - Pack di kiri
         
Line 778: (blank line)
         
Line 779:     display_button = tk.Button(button_frame, text="Display Only\n(Without Arduino)",
         - Buat tombol Display Only
         
Line 780:                               font=("Segoe UI", 11, "bold"),
         - Set font
         
Line 781:                               bg="#ecc94b", fg="white", activebackground="#d69e2e",
         - Set warna kuning
         
Line 782:                               activeforeground="white", relief=tk.RAISED,
         - Set active colors
         
Line 783:                               cursor="hand2", padx=25, pady=12, command=on_display_only,
         - Set cursor dan command
         
Line 784:                               bd=2, highlightthickness=0, width=18)
         - Set border dan width
         
Line 785:     display_button.pack(side=tk.LEFT, padx=8)
         - Pack di kanan
         
Line 786: (blank line)
         
Line 787:     info_button = tk.Button(dialog, text="Project Info",
         - Buat tombol Info
         
Line 788:                            font=("Segoe UI", 10, "bold"),
         - Set font
         
Line 789:                            bg="#4299e1", fg="white", activebackground="#3182ce",
         - Set warna biru
         
Line 790:                            activeforeground="white", relief=tk.RAISED,
         - Set active colors
         
Line 791:                            cursor="hand2", padx=20, pady=8, command=on_info,
         - Set cursor dan command
         
Line 792:                            bd=2, highlightthickness=0)
         - Set border
         
Line 793:     info_button.pack(pady=15)
         - Pack tombol
         
Line 794: (blank line)
         
Line 795:     dialog.mainloop()
         - Start mainloop dialog
         
Line 796: (blank line)
         
Line 797:     return selected_mode[0]
         - Return mode yang dipilih
         
Line 798: (blank line)
         
Line 799: (blank line)
Line 800: def main():
         - Function main entry point
         
Line 801:     use_microcontroller = select_mode()
         - Panggil select_mode
         
Line 802: (blank line)
         
Line 803:     if use_microcontroller is None:
         - Cek jika user cancel
         
Line 804:         print("No mode selected, exiting...")
         - Print pesan exit
         
Line 805:         return
         - Return
         
Line 806: (blank line)
         
Line 807:     print("Initializing detection system...")
         - Print pesan inisialisasi
         
Line 808:     from src.detection import DetectionSystem
         - Import DetectionSystem
         
Line 809:     detection_system = DetectionSystem()
         - Buat instance
         
Line 810: (blank line)
         
Line 811:     print("Initializing serial communication...")
         - Print pesan serial
         
Line 812:     serial_comm = SerialComm(enabled=use_microcontroller)
         - Buat SerialComm
         
Line 813: (blank line)
         
Line 814:     root = tk.Tk()
         - Buat Tk root
         
Line 815:     gui = SmartBinGUI(root, detection_system, serial_comm, use_microcontroller)
         - Buat GUI instance
         
Line 816: (blank line)
         
Line 817:     def on_closing():
         - Inner function untuk handle close
         
Line 818:         gui.cleanup()
         - Cleanup
         
Line 819:         root.destroy()
         - Destroy window
         
Line 820: (blank line)
         
Line 821:     root.protocol("WM_DELETE_WINDOW", on_closing)
         - Bind close event
         
Line 822: (blank line)
         
Line 823:     print("Starting GUI...")
         - Print pesan start
         
Line 824:     root.mainloop()
         - Start mainloop
         
Line 825: (blank line)
         
Line 826:     print("Application terminated.")
         - Print pesan terminated
         
Line 827: (blank line)
         
Line 828: (blank line)
Line 829: if __name__ == "__main__":
         - Cek jika dijalankan sebagai script
         
Line 830:     main()
         - Panggil main
         
Line 831: (blank line)
```

---

## src/convert_coco_to_yolo.py - 119 Lines

### Lines 1-28: Imports and Setup
```
Line 1: (blank line)

Line 2: import os
         - Import os untuk operasi file system
         
Line 3: import json
         - Import json untuk membaca file JSON COCO
         
Line 4: import shutil
         - Import shutil untuk copy file
         
Line 5: from pathlib import Path
         - Import Path untuk path handling
         
Line 6: (blank line)

Line 7: (blank line)

Line 8: def convert_coco_to_yolo():
         - Function utama untuk konversi COCO ke YOLO
         
Line 9:     base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
         - Dapatkan base directory project (2 level up dari file ini)
         
Line 10:     raw_dir = os.path.join(base_dir, 'data', 'raw')
         - Buat path ke folder raw dataset COCO
         
Line 11:     yolo_dir = os.path.join(base_dir, 'data', 'yolo_dataset')
         - Buat path ke folder output YOLO dataset
         
Line 12: (blank line)
         
Line 13:     class_mapping = {
         - Mapping class name ke class ID YOLO
         
Line 14:         'organik': 0,
         - Class organik → ID 0
         
Line 15:         'nonorganik': 1,
         - Class nonorganik → ID 1
         
Line 16:         'sampah_berbahaya': 2
         - Class sampah_berbahaya → ID 2
         
Line 17:     }
         - Tutup dictionary
         
Line 18: (blank line)
         
Line 19:     category_folder_mapping = {
         - Mapping nama folder kategori ke class name
         
Line 20:         'Organik': 'organik',
         - Folder Organik → class organik
         
Line 21:         'Anorganik': 'nonorganik',
         - Folder Anorganik → class nonorganik
         
Line 22:         'B3': 'sampah_berbahaya'
         - Folder B3 → class sampah_berbahaya
         
Line 23:     }
         - Tutup dictionary
         
Line 24:     splits = ['train', 'valid', 'test']
         - List split dataset
         
Line 25:     for split in splits:
         - Loop untuk setiap split
         
Line 26:         os.makedirs(os.path.join(yolo_dir, split, 'images'), exist_ok=True)
         - Buat folder images untuk split
         
Line 27:         os.makedirs(os.path.join(yolo_dir, split, 'labels'), exist_ok=True)
         - Buat folder labels untuk split
         
Line 28: (blank line)
```

### Lines 29-53: Main Conversion Loop
```
Line 29:     print("Converting COCO dataset to YOLO format...")
         - Print pesan start konversi
         
Line 30:     print(f"Source: {raw_dir}")
         - Print source directory
         
Line 31:     print(f"Target: {yolo_dir}")
         - Print target directory
         
Line 32: (blank line)
         
Line 33:     # Process each category folder
         - Komentar
         
Line 34:     for category_folder, class_name in category_folder_mapping.items():
         - Loop untuk setiap kategori folder
         
Line 35:         category_path = os.path.join(raw_dir, category_folder)
         - Buat path ke folder kategori
         
Line 36:         if not os.path.exists(category_path):
         - Cek jika folder tidak ada
         
Line 37:             print(f"Warning: {category_path} does not exist, skipping...")
         - Print warning
         
Line 38:             continue
         - Skip ke kategori berikutnya
         
Line 39: (blank line)
         
Line 40:         class_id = class_mapping[class_name]
         - Dapatkan class ID dari mapping
         
Line 41:         print(f"\nProcessing {category_folder} -> {class_name} (class_id: {class_id})")
         - Print info proses
         
Line 42: (blank line)
         
Line 43:         for split in splits:
         - Loop untuk setiap split
         
Line 44:             split_path = os.path.join(category_path, split)
         - Buat path ke folder split
         
Line 45:             if not os.path.exists(split_path):
         - Cek jika folder split tidak ada
         
Line 46:                 print(f"  Warning: {split_path} does not exist, skipping...")
         - Print warning
         
Line 47:             continue
         - Skip split ini
         
Line 48: (blank line)
         
Line 49:             coco_json = os.path.join(split_path, '_annotations.coco.json')
         - Buat path ke file JSON COCO
         
Line 50:             if not os.path.exists(coco_json):
         - Cek jika file JSON tidak ada
         
Line 51:                 print(f"  Warning: {coco_json} does not exist, skipping...")
         - Print warning
         
Line 52:             continue
         - Skip split ini
         
Line 53: (blank line)
```

### Lines 54-89: JSON Processing
```
Line 54:             with open(coco_json, 'r') as f:
         - Buka file JSON untuk dibaca
         
Line 55:                 coco_data = json.load(f)
         - Load JSON ke dictionary
         
Line 56: (blank line)
         
Line 57:             image_id_to_filename = {img['id']: img['file_name'] for img in coco_data['images']}
         - Buat mapping image ID ke filename
         
Line 58: (blank line)
         
Line 59:             image_id_to_annotations = {}
         - Buat dictionary untuk mapping image ID ke annotations
         
Line 60:             for ann in coco_data['annotations']:
         - Loop untuk setiap annotation
         
Line 61:                 image_id = ann['image_id']
         - Ambil image ID dari annotation
         
Line 62:                 if image_id not in image_id_to_annotations:
         - Cek jika image ID belum ada di dictionary
         
Line 63:                     image_id_to_annotations[image_id] = []
         - Buat list baru untuk image ID ini
         
Line 64:                 image_id_to_annotations[image_id].append(ann)
         - Tambahkan annotation ke list
         
Line 65: (blank line)
         
Line 66:             for image_id, annotations in image_id_to_annotations.items():
         - Loop untuk setiap image ID dan annotations
         
Line 67:                 image_filename = image_id_to_filename.get(image_id)
         - Dapatkan filename dari image ID
         
Line 68:                 if not image_filename:
         - Cek jika filename tidak ditemukan
         
Line 69:                     continue
         - Skip image ini
         
Line 70: (blank line)
         
Line 71:                 src_image_path = os.path.join(split_path, image_filename)
         - Buat path ke gambar source
         
Line 72:                 dst_image_path = os.path.join(yolo_dir, split, 'images', image_filename)
         - Buat path ke gambar destination
         
Line 73: (blank line)
         
Line 74:                 if os.path.exists(src_image_path):
         - Cek jika gambar source ada
         
Line 75:                     shutil.copy2(src_image_path, dst_image_path)
         - Copy gambar ke destination
         
Line 76:                 else:
         - Jika gambar tidak ada
         
Line 77:                     print(f"  Warning: Image {src_image_path} not found, skipping...")
         - Print warning
         
Line 78:                     continue
         - Skip image ini
         
Line 79: (blank line)
         
Line 80:                 image_info = None
         - Inisialisasi image_info
         
Line 81:                 for img in coco_data['images']:
         - Loop untuk mencari image info
         
Line 82:                     if img['id'] == image_id:
         - Cek jika ID match
         
Line 83:                         image_info = img
         - Simpan image info
         
Line 84:                         break
         - Break loop
         
Line 85: (blank line)
         
Line 86:                 if not image_info:
         - Cek jika image info tidak ditemukan
         
Line 87:                     print(f"  Warning: Image info for ID {image_id} not found, skipping...")
         - Print warning
         
Line 88:                     continue
         - Skip image ini
         
Line 89: (blank line)
```

### Lines 90-112: Bounding Box Conversion
```
Line 90:                 img_width = image_info['width']
         - Ambil lebar gambar
         
Line 91:                 img_height = image_info['height']
         - Ambil tinggi gambar
         
Line 92: (blank line)
         
Line 93:                 label_filename = os.path.splitext(image_filename)[0] + '.txt'
         - Buat nama file label (ganti extension ke .txt)
         
Line 94:                 label_path = os.path.join(yolo_dir, split, 'labels', label_filename)
         - Buat path ke file label
         
Line 95: (blank line)
         
Line 96:                 with open(label_path, 'w') as f:
         - Buka file label untuk ditulis
         
Line 97:                     for ann in annotations:
         - Loop untuk setiap annotation
         
Line 98:                         bbox = ann['bbox']
         - Ambil bounding box dari annotation
         
Line 99:                         x_min, y_min, bbox_width, bbox_height = bbox
         - Unpack bbox COCO format
         
Line 100: (blank line)
                        
Line 101:                         x_center = x_min + bbox_width / 2
         - Hitung x center
         
Line 102:                         y_center = y_min + bbox_height / 2
         - Hitung y center
         
Line 103: (blank line)
                        
Line 104:                         x_center /= img_width
         - Normalize x center (0-1)
         
Line 105:                         y_center /= img_height
         - Normalize y center (0-1)
         
Line 106:                         bbox_width /= img_width
         - Normalize width (0-1)
         
Line 107:                         bbox_height /= img_height
         - Normalize height (0-1)
         
Line 108: (blank line)
                        
Line 109:                         f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {bbox_width:.6f} {bbox_height:.6f}\n")
         - Tulis label dalam format YOLO: class_id x_center y_center width height
         
Line 110: (blank line)
            
Line 111:             print(f"  Processed {len(image_id_to_annotations)} images in {split}")
         - Print jumlah gambar yang diproses
         
Line 112: (blank line)
```

### Lines 113-119: Completion
```
Line 113:     print("\nConversion completed successfully!")
         - Print pesan sukses
         
Line 114:     print(f"YOLO dataset created at: {yolo_dir}")
         - Print path output
         
Line 115: (blank line)
         
Line 116: (blank line)

Line 117: if __name__ == "__main__":
         - Cek jika dijalankan sebagai script
         
Line 118:     convert_coco_to_yolo()
         - Panggil function konversi
         
Line 119: (blank line)
```

---

## src/detection.py - 83 Lines

### Lines 1-16: Imports and Configuration
```
Line 1: import cv2
         - Import OpenCV untuk image processing
         
Line 2: import os
         - Import os untuk path handling
         
Line 3: from ultralytics import YOLO
         - Import YOLO dari ultralytics
         
Line 4: (blank line)

Line 5: YOLO_CONFIDENCE_THRESHOLD_MANUAL = 0.25
         - Threshold confidence untuk mode manual (25%)
         
Line 6: YOLO_CONFIDENCE_THRESHOLD_AUTO = 0.5
         - Threshold confidence untuk mode auto (50%)
         
Line 7: CUSTOM_MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runs", "waste_classification", "weights", "best.pt")
         - Path ke model custom yang sudah di-train
         
Line 8: YOLO_MODEL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "yolov8n.pt")
         - Path ke pre-trained YOLOv8n
         
Line 9: YOLO_MODEL = CUSTOM_MODEL_PATH if os.path.exists(CUSTOM_MODEL_PATH) else YOLO_MODEL
         - Gunakan custom model jika ada, else pre-trained
         
Line 10: (blank line)

Line 11: CUSTOM_CLASS_MAPPING = {
         - Mapping class ID ke nama kategori
         
Line 12:     0: "organik",
         - ID 0 → organik
         
Line 13:     1: "nonorganik",
         - ID 1 → nonorganik
         
Line 14:     2: "sampah_berbahaya"
         - ID 2 → sampah_berbahaya
         
Line 15: }
         - Tutup dictionary
         
Line 16: (blank line)
```

### Lines 17-44: DetectionSystem Class
```
Line 17: class DetectionSystem:
         - Class untuk sistem deteksi YOLO
         
Line 18:     def __init__(self):
         - Constructor
         
Line 19:         self.yolo_model = None
         - Inisialisasi model sebagai None
         
Line 20:         self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
         - Dapatkan base directory
         
Line 21:         self.auto_threshold = YOLO_CONFIDENCE_THRESHOLD_AUTO
         - Set threshold auto
         
Line 22:         self._initialize()
         - Panggil inisialisasi
         
Line 23: (blank line)

Line 24:     def _initialize(self):
         - Method private untuk inisialisasi model
         
Line 25:         print("Initializing YOLO model...")
         - Print pesan inisialisasi
         
Line 26:         try:
         - Mulai try block
         
Line 27:             if os.path.exists(CUSTOM_MODEL_PATH):
         - Cek jika custom model ada
         
Line 28:                 print(f"Loading custom model from: {CUSTOM_MODEL_PATH}")
         - Print path custom model
         
Line 29:                 self.yolo_model = YOLO(CUSTOM_MODEL_PATH)
         - Load custom model
         
Line 30:                 print("Custom YOLO model loaded successfully")
         - Print sukses
         
Line 31:                 print(f"Model classes: {self.yolo_model.names}")
         - Print nama class model
         
Line 32:             else:
         - Jika custom model tidak ada
         
Line 33:                 print(f"Custom model not found at {CUSTOM_MODEL_PATH}")
         - Print pesan tidak ditemukan
         
Line 34:                 print(f"Loading pre-trained model: {YOLO_MODEL}")
         - Print path pre-trained
         
Line 35:                 self.yolo_model = YOLO(YOLO_MODEL)
         - Load pre-trained model
         
Line 36:                 print("Pre-trained YOLO model loaded successfully")
         - Print sukses
         
Line 37:                 print(f"Model classes: {self.yolo_model.names}")
         - Print nama class model
         
Line 38:         except Exception as e:
         - Catch exception
         
Line 39:             print(f"Error loading YOLO model: {e}")
         - Print error
         
Line 40:             raise
         - Raise exception
         
Line 41: (blank line)

Line 42:     def get_category_from_class_id(self, class_id):
         - Method untuk dapatkan kategori dari class ID
         
Line 43:         return CUSTOM_CLASS_MAPPING.get(class_id, None)
         - Return kategori dari mapping atau None
         
Line 44: (blank line)
```

### Lines 45-83: Detect Method
```
Line 45:     def detect(self, frame, in_cooldown=False, manual_mode=True):
         - Method untuk deteksi objek pada frame
         - frame: gambar input (numpy array)
         - in_cooldown: flag cooldown
         - manual_mode: flag mode manual/auto
         
Line 46:         result = {
         - Inisialisasi result dictionary
         
Line 47:             "best_class": None,
         - Class terbaik (None)
         
Line 48:             "best_confidence": 0.0,
         - Confidence terbaik (0.0)
         
Line 49:             "best_box": None,
         - Bounding box terbaik (None)
         
Line 50:             "current_category": None,
         - Kategori saat ini (None)
         
Line 51:             "decision_source": "None"
         - Sumber keputusan ("None")
         
Line 52:         }
         - Tutup dictionary
         
Line 53: (blank line)

Line 54:         threshold = YOLO_CONFIDENCE_THRESHOLD_MANUAL if manual_mode else self.auto_threshold
         - Tentukan threshold berdasarkan mode
         
Line 55: (blank line)

Line 56:         print(f"Frame shape: {frame.shape}")
         - Print shape frame
         
Line 57:         print(f"Confidence threshold: {threshold} (manual={manual_mode})")
         - Print threshold dan mode
         
Line 58: (blank line)

Line 59:         yolo_results = self.yolo_model(frame, verbose=False, conf=threshold)
         - Jalankan inference YOLO pada frame
         
Line 60:         print(f"YOLO results: {len(yolo_results)}")
         - Print jumlah hasil
         
Line 61: (blank line)

Line 62:         for yolo_result in yolo_results:
         - Loop untuk setiap result YOLO
         
Line 63:             print(f"Boxes in result: {len(yolo_result.boxes) if hasattr(yolo_result, 'boxes') else 0}")
         - Print jumlah bounding boxes
         
Line 64:             for box in yolo_result.boxes:
         - Loop untuk setiap bounding box
         
Line 65:                 class_id = int(box.cls[0])
         - Ambil class ID dari box
         
Line 66:                 confidence = float(box.conf[0])
         - Ambil confidence dari box
         
Line 67: (blank line)
                        
Line 68:                 category = self.get_category_from_class_id(class_id)
         - Dapatkan kategori dari class ID
         
Line 69:                 if category is None:
         - Cek jika kategori tidak valid
         
Line 70:                     continue
         - Skip box ini
         
Line 71: (blank line)
                        
Line 72:                 print(f"Detected: {category} (confidence: {confidence:.4f})")
         - Print hasil deteksi
         
Line 73: (blank line)
                        
Line 74:                 if confidence > result["best_confidence"]:
         - Cek jika confidence lebih tinggi dari best
         
Line 75:                     result["best_confidence"] = confidence
         - Update best confidence
         
Line 76:                     result["best_class"] = class_id
         - Update best class
         
Line 77:                     result["current_category"] = category
         - Update current category
         
Line 78:                     result["best_box"] = box.xyxy[0].cpu().numpy()
         - Update best bounding box (convert ke numpy)
         
Line 79:                     result["decision_source"] = "YOLO"
         - Set decision source
         
Line 80: (blank line)
Line 81:         return result
         - Return result dictionary
         
Line 82: (blank line)
Line 83: (blank line)
```

---

## src/main.py - 312 Lines

### Lines 1-12: Imports and Setup
```
Line 1: (blank line)

Line 2: import os
         - Import os untuk operasi system
         
Line 3: os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '0'
         - Disable MPS fallback untuk PyTorch (Mac GPU)
         
Line 4: os.environ['TORCH_DISABLE_NVIDIA_TF32'] = '1'
         - Disable NVIDIA TF32 untuk compatibility
         
Line 5: (blank line)

Line 6: import argparse
         - Import argparse untuk command line arguments
         
Line 7: from ultralytics import YOLO
         - Import YOLO dari ultralytics
         
Line 8: import numpy as np
         - Import numpy untuk numerical computing
         
Line 9: from collections import defaultdict
         - Import defaultdict untuk dictionary dengan default value
         
Line 10: from convert_coco_to_yolo import convert_coco_to_yolo
         - Import function konversi
         
Line 11: import matplotlib.pyplot as plt
         - Import matplotlib untuk visualisasi
         
Line 12: (blank line)
```

### Lines 14-44: Training Function
```
Line 14: def train_custom_model():
         - Function untuk training custom YOLO model
         
Line 15:     base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
         - Dapatkan base directory
         
Line 16:     data_yaml = os.path.join(base_dir, 'data', 'data.yaml')
         - Buat path ke data.yaml
         
Line 17: (blank line)

Line 18:     print("Loading YOLOv8n model...")
         - Print pesan load model
         
Line 19:     model = YOLO(os.path.join(base_dir, 'models', 'yolov8n.pt'))
         - Load pre-trained YOLOv8n
         
Line 20: (blank line)

Line 21:     print("Starting training...")
         - Print pesan start training
         
Line 22:     results = model.train(
         - Mulai training
         
Line 23:         data=data_yaml,
         - Path ke data config
         
Line 24:         epochs=30,
         - Jumlah epoch 30
         
Line 25:         imgsz=416,
         - Ukuran gambar 416x416
         
Line 26:         batch=8,
         - Batch size 8
         
Line 27:         device='cpu',
         - Gunakan CPU
         
Line 28:         project=base_dir,
         - Project directory
         
Line 29:         name='runs/waste_classification',
         - Nama run
         
Line 30:         patience=5,
         - Early stopping patience 5
         
Line 31:         save=True,
         - Save model
         
Line 32:         plots=False,
         - Disable plots otomatis
         
Line 33:         verbose=True
         - Print verbose output
         
Line 34:     )
         - Tutup call train
         
Line 35: (blank line)

Line 36:     print("Training completed!")
         - Print pesan selesai
         
Line 37:     print(f"Best model saved at: {results.save_dir}/weights/best.pt")
         - Print path model terbaik
         
Line 38: (blank line)

Line 39:     print("\nValidating model...")
         - Print pesan validasi
         
Line 40:     metrics = model.val()
         - Jalankan validasi
         
Line 41:     print(f"mAP50: {metrics.box.map50}")
         - Print mAP50
         
Line 42:     print(f"mAP50-95: {metrics.box.map}")
         - Print mAP50-95
         
Line 43: (blank line)

Line 44:     return model
         - Return model yang sudah di-train
         
Line 45: (blank line)
```

### Lines 47-155: Visualization Function
```
Line 47: def create_visualizations(metrics, base_dir):
         - Function untuk membuat visualisasi metrics
         
Line 48:     """Create visualization charts for evaluation results"""
         - Docstring
         
Line 49:     print("\n=== Creating Visualizations ===")
         - Print header
         
Line 50: (blank line)

Line 51:     # Create visual folder
         - Komentar
         
Line 52:     visual_dir = os.path.join(base_dir, 'visual')
         - Buat path folder visual
         
Line 53:     os.makedirs(visual_dir, exist_ok=True)
         - Buat folder jika belum ada
         
Line 54: (blank line)

Line 55:     # Data dari hasil evaluasi
         - Komentar
         
Line 56:     classes = ['Organik', 'Non-Organik', 'Sampah Berbahaya']
         - List nama kelas
         
Line 57:     precision = [float(metrics.box.p[i]) for i in range(3)]
         - List precision per kelas
         
Line 58:     recall = [float(metrics.box.r[i]) for i in range(3)]
         - List recall per kelas
         
Line 59: (blank line)

Line 60:     # Dataset distribution
         - Komentar
         
Line 61:     dataset_info = {
         - Info dataset
         
Line 62:         'Organik': {'images': 103, 'instances': 316},
         - Info kelas Organik
         
Line 63:         'Non-Organik': {'images': 111, 'instances': 123},
         - Info kelas Non-Organik
         
Line 64:         'Sampah Berbahaya': {'images': 100, 'instances': 323}
         - Info kelas Sampah Berbahaya
         
Line 65:     }
         - Tutup dictionary
         
Line 66: (blank line)

Line 67:     # VISUALISASI 1: Precision dan Recall per Kelas (Side by Side)
         - Komentar
         
Line 68:     fig, ax = plt.subplots(figsize=(10, 6))
         - Buat figure dan axis
         
Line 69:     x = np.arange(len(classes))
         - Buat array posisi x
         
Line 70:     width = 0.35
         - Lebar bar
         
Line 71: (blank line)

Line 72:     bars1 = ax.bar(x - width/2, precision, width, label='Precision', color='#3498db', alpha=0.8)
         - Buat bar precision
         
Line 73:     bars2 = ax.bar(x + width/2, recall, width, label='Recall', color='#e74c3c', alpha=0.8)
         - Buat bar recall
         
Line 74: (blank line)

Line 75:     ax.set_ylabel('Score', fontsize=12, fontweight='bold')
         - Set label y-axis
         
Line 76:     ax.set_title('Precision dan Recall per Kelas Sampah', fontsize=14, fontweight='bold')
         - Set judul title
         
Line 77:     ax.set_xticks(x)
         - Set posisi ticks x
         
Line 78:     ax.set_xticklabels(classes)
         - Set label ticks x
         
Line 79:     ax.legend(fontsize=11)
         - Tambahkan legend
         
Line 80:     ax.set_ylim(0, 1.0)
         - Set range y-axis
         
Line 81:     ax.grid(axis='y', alpha=0.3)
         - Tambahkan grid
         
Line 82: (blank line)

Line 83:     for bars in [bars1, bars2]:
         - Loop untuk setiap bar group
         
Line 84:         for bar in bars:
         - Loop untuk setiap bar
         
Line 85:             height = bar.get_height()
         - Ambil tinggi bar
         
Line 86:             ax.text(bar.get_x() + bar.get_width()/2., height,
         - Tambahkan text di atas bar
         
Line 87:                     f'{height:.4f}',
         - Format nilai
         
Line 88:                     ha='center', va='bottom', fontsize=10, fontweight='bold')
         - Set alignment dan font
         
Line 89: (blank line)

Line 90:     plt.tight_layout()
         - Adjust layout
         
Line 91:     viz_path = os.path.join(visual_dir, 'precision_recall_comparison.png')
         - Buat path output
         
Line 92:     plt.savefig(viz_path, dpi=300, bbox_inches='tight')
         - Simpan figure
         
Line 93:     print(f"✓ Saved: precision_recall_comparison.png")
         - Print pesan sukses
         
Line 94:     plt.close()
         - Tutup figure
         
Line 95: (blank line)

Line 96:     # VISUALISASI 2: Distribusi Dataset
         - Komentar
         
Line 97:     fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
         - Buat figure dengan 2 subplot
         
Line 98: (blank line)

Line 99:     # Distribusi Citra
         - Komentar
         
Line 100:     images = [dataset_info[cls]['images'] for cls in classes]
         - List jumlah gambar per kelas
         
Line 101:     colors = ['#2ecc71', '#3498db', '#e74c3c']
         - List warna untuk bar
         
Line 102:     bars1 = ax1.bar(classes, images, color=colors, alpha=0.8)
         - Buat bar distribusi gambar
         
Line 103:     ax1.set_ylabel('Jumlah Citra', fontsize=12, fontweight='bold')
         - Set label y-axis
         
Line 104:     ax1.set_title('Distribusi Citra per Kelas', fontsize=14, fontweight='bold')
         - Set judul
         
Line 105:     ax1.grid(axis='y', alpha=0.3)
         - Tambahkan grid
         
Line 106:     for bar in bars1:
         - Loop untuk setiap bar
         
Line 107:         height = bar.get_height()
         - Ambil tinggi
         
Line 108:         ax1.text(bar.get_x() + bar.get_width()/2., height,
         - Tambahkan text
         
Line 109:                  f'{int(height)}',
         - Format nilai
         
Line 110:                  ha='center', va='bottom', fontsize=11, fontweight='bold')
         - Set alignment
         
Line 111: (blank line)

Line 112:     # Distribusi Instances
         - Komentar
         
Line 113:     instances = [dataset_info[cls]['instances'] for cls in classes]
         - List jumlah instances per kelas
         
Line 114:     bars2 = ax2.bar(classes, instances, color=colors, alpha=0.8)
         - Buat bar distribusi instances
         
Line 115:     ax2.set_ylabel('Jumlah Instances', fontsize=12, fontweight='bold')
         - Set label y-axis
         
Line 116:     ax2.set_title('Distribusi Instances per Kelas', fontsize=14, fontweight='bold')
         - Set judul
         
Line 117:     ax2.grid(axis='y', alpha=0.3)
         - Tambahkan grid
         
Line 118:     for bar in bars2:
         - Loop untuk setiap bar
         
Line 119:         height = bar.get_height()
         - Ambil tinggi
         
Line 120:         ax2.text(bar.get_x() + bar.get_width()/2., height,
         - Tambahkan text
         
Line 121:                  f'{int(height)}',
         - Format nilai
         
Line 122:                  ha='center', va='bottom', fontsize=11, fontweight='bold')
         - Set alignment
         
Line 123: (blank line)

Line 124:     plt.tight_layout()
         - Adjust layout
         
Line 125:     viz_path = os.path.join(visual_dir, 'dataset_distribution.png')
         - Buat path output
         
Line 126:     plt.savefig(viz_path, dpi=300, bbox_inches='tight')
         - Simpan figure
         
Line 127:     print(f"✓ Saved: dataset_distribution.png")
         - Print pesan sukses
         
Line 128:     plt.close()
         - Tutup figure
         
Line 129: (blank line)

Line 130:     # VISUALISASI 3: Overall Metrics
         - Komentar
         
Line 131:     metrics_names = ['mAP50', 'mAP50-95', 'Precision', 'Recall']
         - List nama metrics
         
Line 132:     metrics_values = [float(metrics.box.map50), float(metrics.box.map), 
         - List nilai metrics
         
Line 133:                       float(metrics.box.mp), float(metrics.box.mr)]
         - Lanjutan list nilai
         
Line 134: (blank line)

Line 135:     fig, ax = plt.subplots(figsize=(10, 6))
         - Buat figure dan axis
         
Line 136:     bars = ax.bar(metrics_names, metrics_values, color=['#9b59b6', '#3498db', '#2ecc71', '#e74c3c'], alpha=0.8)
         - Buat bar metrics
         
Line 137:     ax.set_ylabel('Score', fontsize=12, fontweight='bold')
         - Set label y-axis
         
Line 138:     ax.set_title('Overall Validation Metrics', fontsize=14, fontweight='bold')
         - Set judul
         
Line 139:     ax.set_ylim(0, 1.0)
         - Set range y-axis
         
Line 140:     ax.grid(axis='y', alpha=0.3)
         - Tambahkan grid
         
Line 141: (blank line)

Line 142:     for bar in bars:
         - Loop untuk setiap bar
         
Line 143:         height = bar.get_height()
         - Ambil tinggi
         
Line 144:         ax.text(bar.get_x() + bar.get_width()/2., height,
         - Tambahkan text
         
Line 145:                 f'{height:.4f}',
         - Format nilai
         
Line 146:                 ha='center', va='bottom', fontsize=11, fontweight='bold')
         - Set alignment
         
Line 147: (blank line)

Line 148:     plt.tight_layout()
         - Adjust layout
         
Line 149:     viz_path = os.path.join(visual_dir, 'overall_metrics.png')
         - Buat path output
         
Line 150:     plt.savefig(viz_path, dpi=300, bbox_inches='tight')
         - Simpan figure
         
Line 151:     print(f"✓ Saved: overall_metrics.png")
         - Print pesan sukses
         
Line 152:     plt.close()
         - Tutup figure
         
Line 153: (blank line)

Line 154:     print(f"All visualizations saved to: {visual_dir}")
         - Print path folder visual
         
Line 155: (blank line)
```

### Lines 157-194: Evaluation Function
```
Line 157: def evaluate_model(model_path=None, data_yaml=None):
         - Function untuk evaluasi model
         
Line 158:     base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
         - Dapatkan base directory
         
Line 159: (blank line)

Line 160:     if model_path is None:
         - Cek jika model path tidak diberikan
         
Line 161:         model_path = os.path.join(base_dir, "runs", "waste_classification", "weights", "best.pt")
         - Gunakan path default
         
Line 162: (blank line)

Line 163:     if data_yaml is None:
         - Cek jika data yaml tidak diberikan
         
Line 164:         data_yaml = os.path.join(base_dir, 'data', 'data.yaml')
         - Gunakan path default
         
Line 165: (blank line)

Line 166:     if not os.path.exists(model_path):
         - Cek jika model tidak ada
         
Line 167:         print(f"Model not found at {model_path}")
         - Print pesan error
         
Line 168:         print("Please train the model first using train_custom_model")
         - Print instruksi
         
Line 169:         return None
         - Return None
         
Line 170: (blank line)

Line 171:     print(f"Loading model from: {model_path}")
         - Print path model
         
Line 172:     model = YOLO(model_path)
         - Load model
         
Line 173: (blank line)

Line 174:     print("\n=== Model Validation ===")
         - Print header
         
Line 175:     metrics = model.val(data=data_yaml, plots=False)
         - Jalankan validasi
         
Line 176: (blank line)

Line 177:     print(f"\n=== Validation Metrics ===")
         - Print header
         
Line 178:     print(f"mAP50: {metrics.box.map50:.4f}")
         - Print mAP50
         
Line 179:     print(f"mAP50-95: {metrics.box.map:.4f}")
         - Print mAP50-95
         
Line 180:     print(f"Precision: {metrics.box.mp:.4f}")
         - Print precision
         
Line 181:     print(f"Recall: {metrics.box.mr:.4f}")
         - Print recall
         
Line 182: (blank line)

Line 183:     print(f"\n=== Per-Class Metrics ===")
         - Print header
         
Line 184:     class_names = ['organik', 'nonorganik', 'sampah_berbahaya']
         - List nama kelas
         
Line 185:     for i, class_name in enumerate(class_names):
         - Loop untuk setiap kelas
         
Line 186:         if i < len(metrics.box.p):
         - Cek jika index valid
         
Line 187:             print(f"{class_name}:")
         - Print nama kelas
         
Line 188:             print(f"  Precision: {metrics.box.p[i]:.4f}")
         - Print precision
         
Line 189:             print(f"  Recall: {metrics.box.r[i]:.4f}")
         - Print recall
         
Line 190: (blank line)

Line 191:     # Create visualizations
         - Komentar
         
Line 192:     create_visualizations(metrics, base_dir)
         - Panggil function visualisasi
         
Line 193: (blank line)

Line 194:     return metrics
         - Return metrics
         
Line 195: (blank line)
```

### Lines 197-248: Testing Function
```
Line 197: def test_on_images(model_path=None, test_images_dir=None):
         - Function untuk testing pada gambar
         
Line 198:     base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
         - Dapatkan base directory
         
Line 199: (blank line)

Line 200:     if model_path is None:
         - Cek jika model path tidak diberikan
         
Line 201:         model_path = os.path.join(base_dir, "runs", "waste_classification", "weights", "best.pt")
         - Gunakan path default
         
Line 202: (blank line)

Line 203:     if test_images_dir is None:
         - Cek jika test dir tidak diberikan
         
Line 204:         test_images_dir = os.path.join(base_dir, "data", "yolo_dataset", "test", "images")
         - Gunakan path default
         
Line 205: (blank line)

Line 206:     if not os.path.exists(model_path):
         - Cek jika model tidak ada
         
Line 207:         print(f"Model not found at {model_path}")
         - Print error
         
Line 208:         return
         - Return
         
Line 209: (blank line)

Line 210:     if not os.path.exists(test_images_dir):
         - Cek jika test dir tidak ada
         
Line 211:         print(f"Test images directory not found at {test_images_dir}")
         - Print error
         
Line 212:         return
         - Return
         
Line 213: (blank line)

Line 214:     print(f"Loading model from: {model_path}")
         - Print path model
         
Line 215:     model = YOLO(model_path)
         - Load model
         
Line 216: (blank line)

Line 217:     image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
         - List extension gambar yang didukung
         
Line 218:     test_images = []
         - List untuk menyimpan nama gambar
         
Line 219:     for ext in image_extensions:
         - Loop untuk setiap extension
         
Line 220:         test_images.extend([f for f in os.listdir(test_images_dir) if f.lower().endswith(ext)])
         - Tambahkan gambar dengan extension tersebut
         
Line 221: (blank line)

Line 222:     print(f"\nFound {len(test_images)} test images")
         - Print jumlah gambar
         
Line 223: (blank line)

Line 224:     class_mapping = {0: 'organik', 1: 'nonorganik', 2: 'sampah_berbahaya'}
         - Mapping class ID ke nama
         
Line 225:     results_summary = defaultdict(int)
         - Dictionary untuk summary hasil
         
Line 226: (blank line)

Line 227:     for i, image_name in enumerate(test_images[:10]):
         - Loop untuk 10 gambar pertama
         
Line 228:         image_path = os.path.join(test_images_dir, image_name)
         - Buat path ke gambar
         
Line 229:         print(f"\n[{i+1}/10] Testing: {image_name}")
         - Print progress
         
Line 230: (blank line)

Line 231:         results = model(image_path, verbose=False, conf=0.25)
         - Jalankan inference
         
Line 232: (blank line)

Line 233:         for result in results:
         - Loop untuk setiap result
         
Line 234:             if result.boxes:
         - Cek jika ada bounding boxes
         
Line 235:                 for box in result.boxes:
         - Loop untuk setiap box
         
Line 236:                     class_id = int(box.cls[0])
         - Ambil class ID
         
Line 237:                     confidence = float(box.conf[0])
         - Ambil confidence
         
Line 238:                     class_name = class_mapping.get(class_id, 'unknown')
         - Dapatkan nama kelas
         
Line 239: (blank line)
                        
Line 240:                     print(f"  Detected: {class_name} (confidence: {confidence:.2f})")
         - Print hasil deteksi
         
Line 241:                     results_summary[class_name] += 1
         - Increment counter untuk kelas ini
         
Line 242:             else:
         - Jika tidak ada boxes
         
Line 243:                 print("  No detection")
         - Print no detection
         
Line 244:                 results_summary['no_detection'] += 1
         - Increment counter no detection
         
Line 245: (blank line)

Line 246:     print(f"\n=== Test Summary ===")
         - Print header summary
         
Line 247:     for class_name, count in results_summary.items():
         - Loop untuk setiap kelas
         
Line 248:         print(f"{class_name}: {count}")
         - Print hasil
         
Line 249: (blank line)
```

### Lines 251-312: Main Function
```
Line 251: def main():
         - Function main entry point
         
Line 252:     parser = argparse.ArgumentParser(description='SmartBin Pipeline: Train and Evaluate Model')
         - Buat argument parser
         
Line 253:     parser.add_argument('--mode', type=str, choices=['train', 'evaluate', 'test', 'all', 'convert'], 
         - Tambahkan argument mode
         
Line 254:                         default='all', help='Pipeline mode: train, evaluate, test, all, or convert')
         - Set default dan help
         
Line 255:     parser.add_argument('--model-path', type=str, default=None, 
         - Tambahkan argument model path
         
Line 256:                         help='Path to trained model (for evaluation/testing)')
         - Set help
         
Line 257:     parser.add_argument('--data-yaml', type=str, default=None, 
         - Tambahkan argument data yaml
         
Line 258:                         help='Path to data.yaml file')
         - Set help
         
Line 259:     parser.add_argument('--test-images-dir', type=str, default=None, 
         - Tambahkan argument test images dir
         
Line 260:                         help='Path to test images directory')
         - Set help
         
Line 261:     parser.add_argument('--force-train', action='store_true',
         - Tambahkan argument force train
         
Line 262:                         help='Force training even if model already exists')
         - Set help
         
Line 263: (blank line)

Line 264:     args = parser.parse_args()
         - Parse arguments
         
Line 265: (blank line)

Line 266:     print("="*60)
         - Print separator
         
Line 267:     print("SMARTBIN PIPELINE")
         - Print title
         
Line 268:     print("="*60)
         - Print separator
         
Line 269: (blank line)

Line 270:     if args.mode in ['convert', 'all']:
         - Cek jika mode convert atau all
         
Line 271:         print("\n[0/4] Converting COCO to YOLO format...")
         - Print step
         
Line 272:         print("-"*60)
         - Print separator
         
Line 273:         convert_coco_to_yolo()
         - Panggil konversi
         
Line 274:         print("\nConversion completed!")
         - Print selesai
         
Line 275: (blank line)

Line 276:     if args.mode in ['train', 'all']:
         - Cek jika mode train atau all
         
Line 277:         base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
         - Dapatkan base dir
         
Line 278:         default_model_path = os.path.join(base_dir, "runs", "waste_classification", "weights", "best.pt")
         - Path default model
         
Line 279: (blank line)

Line 280:         if os.path.exists(default_model_path) and not args.force_train:
         - Cek jika model ada dan tidak force train
         
Line 281:             print("\n[1/4] Training Model...")
         - Print step
         
Line 282:             print("-"*60)
         - Print separator
         
Line 283:             print(f"Model already exists at: {default_model_path}")
         - Print path model
         
Line 284:             print("Skipping training. Use --force-train to retrain.")
         - Print skip message
         
Line 285:             print("\nTraining skipped!")
         - Print selesai
         
Line 286:         else:
         - Jika perlu training
         
Line 287:             print("\n[1/4] Training Model...")
         - Print step
         
Line 288:             print("-"*60)
         - Print separator
         
Line 289:             train_custom_model()
         - Panggil training
         
Line 290:             print("\nTraining completed!")
         - Print selesai
         
Line 291: (blank line)

Line 292:     if args.mode in ['evaluate', 'all']:
         - Cek jika mode evaluate atau all
         
Line 293:         print("\n[2/4] Evaluating Model...")
         - Print step
         
Line 294:         print("-"*60)
         - Print separator
         
Line 295:         evaluate_model(model_path=args.model_path, data_yaml=args.data_yaml)
         - Panggil evaluasi
         
Line 296:         print("\nEvaluation completed!")
         - Print selesai
         
Line 297: (blank line)

Line 298:     if args.mode in ['test', 'all']:
         - Cek jika mode test atau all
         
Line 299:         print("\n[3/4] Testing on Images...")
         - Print step
         
Line 300:         print("-"*60)
         - Print separator
         
Line 301:         test_on_images(model_path=args.model_path, test_images_dir=args.test_images_dir)
         - Panggil testing
         
Line 302:         print("\nTesting completed!")
         - Print selesai
         
Line 303: (blank line)

Line 304:     print("\n" + "="*60)
         - Print separator
         
Line 305:     print("PIPELINE COMPLETED")
         - Print selesai
         
Line 306:     print("="*60)
         - Print separator
         
Line 307:     print("\nTo run the GUI application, use: python app/app.py")
         - Print instruksi run GUI
         
Line 308: (blank line)

Line 309: (blank line)

Line 310: if __name__ == "__main__":
         - Cek jika dijalankan sebagai script
         
Line 311:     main()
         - Panggil main
         
Line 312: (blank line)
```

---

## data/data.yaml - 8 Lines

```
Line 1: path: D:\Matkul Kuliah\Semester 6\1Deep Learning\UAS\Smart\data\yolo_dataset
         - Path root directory dataset YOLO (absolute path)
         
Line 2: train: train/images
         - Path relatif ke folder training images (relatif terhadap path di line 1)
         
Line 3: val: valid/images
         - Path relatif ke folder validation images
         
Line 4: test: test/images
         - Path relatif ke folder test images
         
Line 5: (blank line)

Line 6: nc: 3
         - Number of classes (jumlah kelas) = 3
         
Line 7: names: ['organik', 'nonorganik', 'sampah_berbahaya']
         - List nama kelas sesuai urutan class ID (0, 1, 2)
         
Line 8: (blank line)
```

---

## requirements.txt - 8 Lines

```
Line 1: ultralytics==8.0.196
         - Library Ultralytics untuk YOLO (versi 8.0.196)
         - Digunakan untuk training dan inference YOLOv8
         
Line 2: torch==2.1.0
         - PyTorch versi 2.1.0
         - Deep learning framework sebagai backend untuk YOLO
         
Line 3: torchvision==0.16.0
         - Torchvision versi 0.16.0
         - Library computer vision untuk PyTorch
         
Line 4: torchaudio==2.1.0
         - Torchaudio versi 2.1.0
         - Library audio processing untuk PyTorch (dependency)
         
Line 5: opencv-python>=4.8.0
         - OpenCV versi 4.8.0 atau lebih tinggi
         - Digunakan untuk capture video, image processing, dan computer vision
         
Line 6: numpy<2
         - NumPy versi di bawah 2.0
         - Library numerical computing untuk array operations
         
Line 7: Pillow>=10.0.0
         - Pillow (PIL) versi 10.0.0 atau lebih tinggi
         - Library image processing untuk konversi gambar ke Tkinter format
         
Line 8: pyserial>=3.5
         - PySerial versi 3.5 atau lebih tinggi
         - Library untuk komunikasi serial dengan Arduino
```

---

## Summary

Project ini adalah sistem **SMARTBIN - Automatic Waste Sorter** yang menggunakan:

1. **YOLOv8** untuk object detection sampah (3 kelas: organik, nonorganik, sampah berbahaya)
2. **Tkinter** untuk GUI aplikasi dengan real-time video feed
3. **OpenCV** untuk capture kamera dan image processing
4. **PySerial** untuk komunikasi dengan Arduino (COM4, 115200 baud)
5. **Ultralytics** framework untuk training dan inference YOLO

**Alur Kerja:**
- Dataset COCO → Konversi ke YOLO format → Training YOLO → Evaluasi → Testing → Deployment GUI
- GUI memiliki 2 mode: Microcontroller (dengan Arduino) dan Display Only (tanpa Arduino)
- Deteksi otomatis dengan stability check (3 frame berturut-turut) untuk mencegah false positive
- Mode manual capture untuk single-frame detection
- Cooldown mechanism setelah deteksi untuk mencegah spam detection
