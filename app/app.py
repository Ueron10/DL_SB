import tkinter as tk
from PIL import Image, ImageTk
import cv2
import threading
import os
import sys
import time
import serial

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.detection import DetectionSystem

SERIAL_PORT = "COM4"
BAUD_RATE = 115200
SERIAL_COMMANDS = {
    "organik": "O",
    "nonorganik": "N",
    "sampah_berbahaya": "B"
}

class SerialComm:
    def __init__(self, enabled=True):
        self.ser = None
        self.connected = False
        self.enabled = enabled
        if self.enabled:
            self._initialize()
        else:
            print("Serial communication disabled (display only mode)")
    
    def _initialize(self):
        print("Initializing serial connection...")
        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            self.connected = True
            print(f"Serial connected to {SERIAL_PORT}")
        except Exception as e:
            print(f"Warning: Could not connect to serial port: {e}")
            print("Serial communication disabled.")
            self.connected = False
            self.ser = None
    
    def send_command(self, category):
        if not self.connected or self.ser is None:
            return False
        
        command = SERIAL_COMMANDS.get(category, None)
        if command is None:
            return False
        
        try:
            self.ser.write(command.encode())
            return True
        except Exception as e:
            print(f"Serial write error: {e}")
            return False
    
    def read_done_signal(self):
        if not self.connected or self.ser is None:
            return False
        
        try:
            if self.ser.in_waiting > 0:
                line = self.ser.readline().decode().strip()
                return line == "DONE"
        except Exception as e:
            print(f"Serial read error: {e}")
            return False
        return False
    
    def close(self):
        if self.connected and self.ser is not None:
            self.ser.close()
            print("Serial connection closed")

class SmartBinGUI:
    def __init__(self, root, detection_system, serial_comm, use_microcontroller):
        self.root = root
        self.detection_system = detection_system
        self.serial_comm = serial_comm
        self.use_microcontroller = use_microcontroller
        self.running = False
        self.cap = None
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.stability_counter = 0
        self.last_detected_category = None
        self.last_decision_time = 0
        self.frame_count = 0
        self.processing = False
        self.last_detection_result = None
        self.last_processed_object = None
        self.last_processed_time = 0
        self.capturing = False
        self.no_detection_start_time = 0
        self.no_detection_timeout = 3.0
        self.auto_detection = True
        self.cooldown_duration = 3.0
        self.cooldown_start_time = 0
        self.stability_frames_required = 3
        self.confidence_threshold = 0.5
        
        self.setup_ui()
        self.setup_camera()
        
        self.root.bind('<space>', self.on_spacebar)
    
    def setup_ui(self):
        self.root.title("SMARTBIN - Automatic Waste Sorter")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0fff4")
        
        main_frame = tk.Frame(self.root, bg="#f0fff4")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        top_bar = tk.Frame(main_frame, bg="#f0fff4")
        top_bar.pack(fill=tk.X, pady=(0, 10))
        
        back_button = tk.Button(top_bar, text="← Back", font=("Segoe UI", 9, "bold"),
                               bg="#718096", fg="white", activebackground="#4a5568",
                               activeforeground="white", relief=tk.RAISED,
                               cursor="hand2", padx=10, pady=5, command=self.go_back_to_mode_selection,
                               bd=2, highlightthickness=0)
        back_button.pack(side=tk.LEFT)
        
        video_frame = tk.Frame(main_frame, bg="#e6ffed", bd=0, relief=tk.FLAT)
        video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        video_border = tk.Frame(video_frame, bg="#48bb78", bd=0)
        video_border.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        self.video_label = tk.Label(video_border, bg="#e6ffed")
        self.video_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        button_frame = tk.Frame(video_frame, bg="#e6ffed")
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.start_button = self.create_modern_button(button_frame, "Start Detection", "#48bb78", self.start_detection)
        self.start_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.stop_button = self.create_modern_button(button_frame, "Reset", "#e53e3e", self.stop_detection)
        self.stop_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.stop_button.config(state=tk.DISABLED)
        
        self.capture_button = self.create_modern_button(button_frame, "Capture Image", "#ecc94b", self.capture_image)
        self.capture_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        info_frame = tk.Frame(main_frame, bg="#e6ffed", bd=0, relief=tk.FLAT, width=450)
        info_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(15, 0))
        
        title_label = tk.Label(info_frame, text="Detection Info", 
                              font=("Segoe UI", 20, "bold"), bg="#e6ffed", fg="#2f855a")
        title_label.pack(pady=(25, 20))
        
        separator = tk.Frame(info_frame, bg="#48bb78", height=2)
        separator.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.create_modern_info_card(info_frame, "Detected", "object_label", "#2f855a")
        self.create_modern_info_card(info_frame, "Category", "category_label", "#2f855a")
        self.create_modern_info_card(info_frame, "Confidence", "confidence_label", "#2f855a")
        self.create_modern_info_card(info_frame, "Decision Source", "source_label", "#2f855a")
        self.create_modern_info_card(info_frame, "Stability", "stability_label", "#2f855a")
        self.create_modern_info_card(info_frame, "Serial Status", "serial_label", "#2f855a")
        self.create_modern_info_card(info_frame, "Status", "status_label", "#2f855a")
        
        model_frame = tk.Frame(info_frame, bg="#e6ffed")
        model_frame.pack(pady=15)
        
        self.model_status_label = tk.Label(model_frame, text="Model: Custom YOLO",
                                          font=("Segoe UI", 10, "bold"), bg="#e6ffed", fg="#48bb78")
        self.model_status_label.pack()
        
        mode_text = "Microcontroller" if self.use_microcontroller else "Display Only"
        self.mode_status_label = tk.Label(model_frame, text=f"Mode: {mode_text}",
                                          font=("Segoe UI", 10, "bold"), bg="#e6ffed", fg="#48bb78")
        self.mode_status_label.pack(pady=(5, 0))
    
    def create_modern_info_card(self, parent, title, label_name, accent_color):
        card_frame = tk.Frame(parent, bg="#c6f6d5", bd=0, relief=tk.FLAT)
        card_frame.pack(fill=tk.X, padx=20, pady=8)
        
        title_label = tk.Label(card_frame, text=title, font=("Segoe UI", 9, "bold"), 
                              bg="#c6f6d5", fg="#2f855a", width=15, anchor=tk.W)
        title_label.pack(anchor=tk.W, padx=12, pady=(8, 2))
        
        value_label = tk.Label(card_frame, text="--", font=("Segoe UI", 14, "bold"), 
                              bg="#c6f6d5", fg="#276749", anchor=tk.W, width=20)
        value_label.pack(anchor=tk.W, padx=12, pady=(2, 8))
        
        setattr(self, label_name, value_label)
    
    def create_modern_button(self, parent, text, color, command):
        button = tk.Button(parent, text=text, font=("Segoe UI", 11, "bold"),
                          bg=color, fg="white", activebackground=color,
                          activeforeground="white", relief=tk.RAISED,
                          cursor="hand2", padx=30, pady=14, command=command,
                          bd=2, highlightthickness=0)
        return button
    
    def setup_camera(self):
        try:
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                self.cap = cv2.VideoCapture(0)
                if not self.cap.isOpened():
                    raise Exception("Could not open camera with any backend")
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            ret, frame = self.cap.read()
            if not ret or frame is None:
                raise Exception("Camera opened but failed to read frame")
            
            print("Camera initialized successfully")
        except Exception as e:
            print(f"Error initializing camera: {e}")
            if self.cap is not None:
                self.cap.release()
                self.cap = None
            self.show_error(f"Camera Error: {e}")
    
    def start_detection(self):
        if self.cap is None or not self.cap.isOpened():
            self.show_error("Camera not available")
            return
        
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        self.detection_thread = threading.Thread(target=self.detection_loop)
        self.detection_thread.daemon = True
        self.detection_thread.start()
    
    def on_spacebar(self, event):
        if self.running:
            print("Spacebar pressed - restarting detection from beginning")
            self.auto_detection = True
            self.stop_detection()
            self.start_detection()
    
    def stop_detection(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        self.stability_counter = 0
        self.last_detected_category = None
        self.last_decision_time = 0
        self.processing = False
        self.last_detection_result = None
        self.last_processed_object = None
        self.last_processed_time = 0
        self.capturing = False
        self.no_detection_start_time = 0
        self.frame_count = 0
        self.auto_detection = True
        
        self.object_label.config(text="--")
        self.category_label.config(text="--")
        self.source_label.config(text="--")
        self.stability_label.config(text=f"0/{self.stability_frames_required} frames")
        self.status_label.config(text="Ready")
        self.status_label.config(fg="#48bb78")
        
        print("Detection stopped and reset to initial state")
    
    def capture_image(self):
        if self.cap is None or not self.cap.isOpened():
            self.show_error("Camera not available")
            return
        
        if self.capturing:
            print("Already capturing, please wait...")
            return
        
        self.capturing = True
        
        self.no_detection_start_time = 0
        
        self.root.after(0, lambda: self.status_label.config(text="Capturing..."))
        self.root.after(0, lambda: self.status_label.config(fg="#ecc94b"))
        
        try:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                print("Warning: Failed to read frame, attempting to reconnect...")
                self.cap.release()
                time.sleep(0.5)
                self.setup_camera()
                if self.cap is None or not self.cap.isOpened():
                    self.show_error("Camera reconnection failed")
                    self.capturing = False
                    self.root.after(0, lambda: self.status_label.config(text="Ready"))
                    self.root.after(0, lambda: self.status_label.config(fg="#48bb78"))
                    return
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    self.show_error("Failed to capture image after reconnection")
                    self.capturing = False
                    self.root.after(0, lambda: self.status_label.config(text="Ready"))
                    self.root.after(0, lambda: self.status_label.config(fg="#48bb78"))
                    return
            
            detection_result = self.detection_system.detect(frame, in_cooldown=False, manual_mode=True)
            print(f"Detection result: {detection_result}")
            
            frame_flipped = cv2.flip(frame, 0)
            
            if detection_result["current_category"]:
                capture_folder = os.path.join(self.base_dir, "captures")
                os.makedirs(capture_folder, exist_ok=True)
                
                timestamp = int(time.time())
                capture_path = os.path.join(capture_folder, f"capture_{timestamp}.jpg")
                cv2.imwrite(capture_path, frame_flipped)
                print(f"Image captured: {capture_path}")
                print(f"YOLO Confidence: {detection_result['best_confidence']:.2f}")
                
                detection_result["decision_source"] = "Manual"
                
                self.last_detection_result = detection_result.copy()
                
                if detection_result["current_category"]:
                    success = self.serial_comm.send_command(detection_result["current_category"])
                    if success:
                        print(f"Serial command sent: {detection_result['current_category']}")
                
                self.last_processed_object = detection_result["best_class"]
                self.last_processed_time = time.time()
                
                current_time = cv2.getTickCount() / cv2.getTickFrequency()
                self.update_gui(frame_flipped, detection_result, False, current_time)
                
                self.auto_detection = False
                print("Manual capture completed. Detection result displayed. Press SPACE to restart detection.")
            else:
                print("No detection in manual capture")
                self.root.after(0, lambda: self.status_label.config(text="No Detection"))
                self.root.after(0, lambda: self.status_label.config(fg="#e53e3e"))
                
                no_detection_result = {
                    "best_class": None,
                    "best_confidence": 0.0,
                    "best_box": None,
                    "current_category": None,
                    "decision_source": "No Detection"
                }
                current_time = cv2.getTickCount() / cv2.getTickFrequency()
                self.update_gui(frame_flipped, no_detection_result, False, current_time)
                
                self.show_retry_dialog()
                
                self.auto_detection = False
        except Exception as e:
            print(f"Error during capture: {e}")
            self.show_error(f"Capture Error: {e}")
            self.root.after(0, lambda: self.status_label.config(text="Error"))
            self.root.after(0, lambda: self.status_label.config(fg="#e53e3e"))
        
        self.capturing = False
    
    def detection_loop(self):
        while self.running:
            try:
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    print("Warning: Failed to read frame, attempting to reconnect...")
                    self.cap.release()
                    time.sleep(0.5)
                    self.setup_camera()
                    if self.cap is None or not self.cap.isOpened():
                        print("Camera reconnection failed, stopping detection")
                        break
                    continue
            except Exception as e:
                print(f"Error reading frame: {e}")
                self.cap.release()
                time.sleep(0.5)
                self.setup_camera()
                if self.cap is None or not self.cap.isOpened():
                    print("Camera reconnection failed, stopping detection")
                    break
                continue
            
            self.frame_count += 1
            current_time = cv2.getTickCount() / cv2.getTickFrequency()
            
            in_cooldown = (current_time - self.cooldown_start_time) < self.cooldown_duration
            
            if not self.auto_detection:
                frame_flipped = cv2.flip(frame, 0)
                if self.last_detection_result:
                    detection_result = self.last_detection_result.copy()
                    detection_result["decision_source"] = "Last Detection (Paused)"
                else:
                    detection_result = {
                        "best_class": None,
                        "best_confidence": 0.0,
                        "best_box": None,
                        "current_category": None,
                        "decision_source": "Camera Only Mode"
                    }
                self.update_gui(frame_flipped, detection_result, False, current_time)
                continue
            
            if self.processing:
                done_signal = self.serial_comm.read_done_signal()
                if done_signal:
                    self.processing = False
                    self.cooldown_start_time = current_time
                    self.auto_detection = False
                    print("Automatic detection completed. Result displayed. Press SPACE to restart detection.")
            
            if not self.processing:
                if self.frame_count % 3 == 0:
                    detection_result = self.detection_system.detect(frame, in_cooldown, manual_mode=False)
                    
                    if detection_result["best_class"] and not in_cooldown:
                        if (detection_result["best_class"] == self.last_processed_object and 
                            (current_time - self.last_processed_time) < 2.0):
                            self.stability_counter = 0
                        elif detection_result["best_class"] == self.last_detected_category:
                            self.stability_counter += 1
                        else:
                            self.stability_counter = 1
                            self.last_detected_category = detection_result["best_class"]
                        
                        detection_result["stability_progress"] = f"{self.stability_counter}/{self.stability_frames_required}"
                        
                        if self.stability_counter >= self.stability_frames_required:
                            detection_folder = os.path.join(self.base_dir, "detections")
                            os.makedirs(detection_folder, exist_ok=True)
                            
                            frame_flipped = cv2.flip(frame, 0)
                            capture_path = os.path.join(detection_folder, f"detection_{int(current_time)}.jpg")
                            cv2.imwrite(capture_path, frame_flipped)
                            print(f"Image captured: {capture_path}")
                            print(f"YOLO Confidence: {detection_result['best_confidence']:.2f}")
                            
                            self.processing = True
                            
                            self.stability_counter = 0
                            self.last_detected_category = None
                            
                            detection_result["decision_source"] = "Automatic"
                            
                            self.last_processed_object = detection_result["best_class"]
                            self.last_processed_time = current_time
                            
                            self.last_detection_result = detection_result.copy()
                            
                            if detection_result["current_category"]:
                                success = self.serial_comm.send_command(detection_result["current_category"])
                                if success:
                                    self.last_decision_time = current_time
                                    self.stability_counter = 0
                                    self.last_detected_category = None
                            else:
                                detection_result["decision_source"] = "No Detection"
                                print("No detection in automatic mode")
                                print("Waiting 3 seconds to restart...")
                                time.sleep(3)
                                self.stability_counter = 0
                                self.last_detected_category = None
                                self.processing = False
                else:
                    detection_result = {
                        "best_class": None,
                        "best_confidence": 0.0,
                        "best_box": None,
                        "current_category": None,
                        "decision_source": "None"
                    }
            else:
                if self.last_detection_result:
                    detection_result = self.last_detection_result.copy()
                else:
                    detection_result = {
                        "best_class": None,
                        "best_confidence": 0.0,
                        "best_box": None,
                        "current_category": None,
                        "decision_source": "Processing..."
                    }
            
            frame_flipped = cv2.flip(frame, 0)
            self.update_gui(frame_flipped, detection_result, in_cooldown, current_time)
    
    def update_gui(self, frame, detection_result, in_cooldown, current_time):
        if detection_result["best_box"] is not None:
            x1, y1, x2, y2 = map(int, detection_result["best_box"])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (640, 480))
        
        image = Image.fromarray(frame_resized)
        photo = ImageTk.PhotoImage(image=image)
        
        self.root.after(0, lambda: self.video_label.config(image=photo))
        self.root.after(0, lambda: setattr(self.video_label, 'image', photo))
        
        obj_text = "terdeteksi" if detection_result["best_class"] else "None"
        cat_text = detection_result["current_category"] if detection_result["current_category"] else "None"
        conf_text = f"{detection_result['best_confidence']:.2%}" if detection_result["best_confidence"] > 0 else "0%"
        source_text = detection_result["decision_source"]
        
        if self.last_detected_category:
            stab_text = f"{min(self.stability_counter, self.stability_frames_required)}/{self.stability_frames_required} frames"
        elif "stability_progress" in detection_result:
            stab_text = f"{detection_result['stability_progress']} frames"
        else:
            stab_text = f"0/{self.stability_frames_required} frames"
        
        serial_text = "Connected" if self.serial_comm.connected else "Disconnected"
        
        if self.processing:
            status_text = "Processing..."
        elif in_cooldown:
            cooldown_remaining = self.cooldown_duration - (current_time - self.cooldown_start_time)
            status_text = f"Cooldown: {cooldown_remaining:.1f}s"
        else:
            status_text = "Ready"
        
        def update_all():
            self.object_label.config(text=obj_text)
            self.category_label.config(text=cat_text)
            self.confidence_label.config(text=conf_text)
            self.source_label.config(text=source_text)
            self.stability_label.config(text=stab_text)
            self.serial_label.config(text=serial_text)
            self.status_label.config(text=status_text)
            self.status_label.config(fg="#ecc94b" if self.processing else "#48bb78")
        
        self.root.after(0, update_all)
    
    def show_error(self, message):
        error_window = tk.Toplevel(self.root)
        error_window.title("Error")
        error_window.geometry("450x200")
        error_window.configure(bg="#e53e3e")
        
        error_window.update_idletasks()
        width = error_window.winfo_width()
        height = error_window.winfo_height()
        x = (error_window.winfo_screenwidth() // 2) - (width // 2)
        y = (error_window.winfo_screenheight() // 2) - (height // 2)
        error_window.geometry(f'{width}x{height}+{x}+{y}')
        
        error_label = tk.Label(error_window, text=message, font=("Segoe UI", 12),
                               bg="#e53e3e", fg="white", wraplength=400)
        error_label.pack(expand=True, padx=25, pady=25)
        
        close_button = tk.Button(error_window, text="OK", font=("Segoe UI", 11, "bold"),
                                bg="white", fg="#e53e3e", activebackground="#fed7d7",
                                activeforeground="#e53e3e", relief=tk.RAISED,
                                cursor="hand2", padx=30, pady=8,
                                command=error_window.destroy,
                                bd=2, highlightthickness=0)
        close_button.pack(pady=(0, 15))
    
    def show_retry_dialog(self):
        retry_window = tk.Toplevel(self.root)
        retry_window.title("Retry Capture")
        retry_window.geometry("400x200")
        retry_window.configure(bg="#f0fff4")
        
        retry_window.update_idletasks()
        width = retry_window.winfo_width()
        height = retry_window.winfo_height()
        x = (retry_window.winfo_screenwidth() // 2) - (width // 2)
        y = (retry_window.winfo_screenheight() // 2) - (height // 2)
        retry_window.geometry(f'{width}x{height}+{x}+{y}')
        
        message_label = tk.Label(retry_window, text="No object detected.\nWould you like to try again?",
                                 font=("Segoe UI", 12), bg="#f0fff4", fg="#276749")
        message_label.pack(expand=True, padx=25, pady=25)
        
        button_frame = tk.Frame(retry_window, bg="#f0fff4")
        button_frame.pack(pady=10)
        
        def on_retry():
            retry_window.destroy()
            self.capture_image()
        
        def on_cancel():
            retry_window.destroy()
        
        retry_button = tk.Button(button_frame, text="Retry", font=("Segoe UI", 11, "bold"),
                                 bg="#48bb78", fg="white", activebackground="#38a169",
                                 activeforeground="white", relief=tk.RAISED,
                                 cursor="hand2", padx=25, pady=10, command=on_retry,
                                 bd=2, highlightthickness=0)
        retry_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = tk.Button(button_frame, text="Cancel", font=("Segoe UI", 11, "bold"),
                                  bg="#e53e3e", fg="white", activebackground="#c53030",
                                  activeforeground="white", relief=tk.RAISED,
                                  cursor="hand2", padx=25, pady=10, command=on_cancel,
                                  bd=2, highlightthickness=0)
        cancel_button.pack(side=tk.LEFT, padx=5)
    
    def cleanup(self):
        self.stop_detection()
        if self.cap is not None:
            self.cap.release()
        self.serial_comm.close()
    
    def go_back_to_mode_selection(self):
        self.cleanup()
        self.root.destroy()
        
        use_microcontroller = select_mode()
        
        if use_microcontroller is None:
            print("No mode selected, exiting...")
            return
        
        print("Initializing detection system...")
        from src.detection import DetectionSystem
        detection_system = DetectionSystem()
        
        print("Initializing serial communication...")
        serial_comm = SerialComm(enabled=use_microcontroller)
        
        root = tk.Tk()
        gui = SmartBinGUI(root, detection_system, serial_comm, use_microcontroller)
        
        def on_closing():
            gui.cleanup()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        print("Starting GUI...")
        root.mainloop()
        
        print("Application terminated.")


def show_info_dialog():
    info_window = tk.Toplevel()
    info_window.title("Project Info")
    info_window.geometry("800x650")
    info_window.configure(bg="#f0fff4")
    
    info_window.update_idletasks()
    width = info_window.winfo_width()
    height = info_window.winfo_height()
    x = (info_window.winfo_screenwidth() // 2) - (width // 2)
    y = (info_window.winfo_screenheight() // 2) - (height // 2)
    info_window.geometry(f'{width}x{height}+{x}+{y}')
    
    main_frame = tk.Frame(info_window, bg="#f0fff4")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    
    title_label = tk.Label(main_frame, text="SMARTBIN", 
                          font=("Segoe UI", 28, "bold"), bg="#f0fff4", fg="#2f855a")
    title_label.pack(pady=(0, 5))
    
    subtitle_label = tk.Label(main_frame, text="Automatic Waste Sorter System", 
                              font=("Segoe UI", 14), bg="#f0fff4", fg="#48bb78")
    subtitle_label.pack(pady=(0, 25))
    
    separator = tk.Frame(main_frame, bg="#48bb78", height=2)
    separator.pack(fill=tk.X, pady=(0, 20))
    
    sections_frame = tk.Frame(main_frame, bg="#f0fff4")
    sections_frame.pack(fill=tk.BOTH, expand=True)
    
    def create_section(parent, title, content, color):
        frame = tk.Frame(parent, bg="#e6ffed", bd=1, relief=tk.SOLID)
        frame.pack(fill=tk.X, pady=8)
        
        header = tk.Frame(frame, bg=color)
        header.pack(fill=tk.X)
        
        title_label = tk.Label(header, text=title, font=("Segoe UI", 11, "bold"),
                              bg=color, fg="white", padx=15, pady=8)
        title_label.pack(side=tk.LEFT)
        
        content_frame = tk.Frame(frame, bg="#e6ffed")
        content_frame.pack(fill=tk.X, padx=15, pady=10)
        
        for line in content:
            label = tk.Label(content_frame, text=line, font=("Segoe UI", 10),
                           bg="#e6ffed", fg="#276749", anchor=tk.W)
            label.pack(fill=tk.X, pady=2)
    
    create_section(sections_frame, "Dataset", [
        "Source: Roboflow Custom Dataset",
        "Total Images: 314 images across 3 classes",
        "Classes: Organik (103), Non-Organik (111), Sampah Berbahaya (100)"
    ], "#48bb78")
    
    create_section(sections_frame, "Model", [
        "Architecture: YOLOv8n (Nano)",
        "Framework: Ultralytics",
        "Training: Custom trained on waste classification dataset",
        "Input Size: 416x416 pixels"
    ], "#38a169")
    
    create_section(sections_frame, "Features", [
        "Real-time object detection with YOLO",
        "Stability check system (3 consecutive frames)",
        "Automatic & Manual capture modes",
        "Cooldown mechanism to prevent spam detection",
        "Serial communication with Arduino (COM4, 115200 baud)",
        "Confidence display with percentage format"
    ], "#2f855a")
    
    create_section(sections_frame, "Usage", [
        "Start Detection: Automatic detection loop",
        "Capture Image: Single-frame manual capture",
        "Reset: Stop and reset detection",
        "SPACE: Restart detection anytime",
        "Back: Return to mode selection"
    ], "#276749")
    
    close_button = tk.Button(main_frame, text="Close", font=("Segoe UI", 12, "bold"),
                             bg="#48bb78", fg="white", activebackground="#38a169",
                             activeforeground="white", relief=tk.RAISED,
                             cursor="hand2", padx=40, pady=12,
                             command=info_window.destroy,
                             bd=2, highlightthickness=0)
    close_button.pack(pady=(20, 0))


def select_mode():
    dialog = tk.Tk()
    dialog.title("Select Mode")
    dialog.geometry("500x350")
    dialog.configure(bg="#f0fff4")
    
    dialog.update_idletasks()
    width = dialog.winfo_width()
    height = dialog.winfo_height()
    x = (dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog.winfo_screenheight() // 2) - (height // 2)
    dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    selected_mode = [None]
    
    def on_microcontroller():
        selected_mode[0] = True
        dialog.destroy()
    
    def on_display_only():
        selected_mode[0] = False
        dialog.destroy()
    
    def on_info():
        show_info_dialog()
    
    title_label = tk.Label(dialog, text="SMARTBIN - Mode Selection",
                          font=("Segoe UI", 18, "bold"), bg="#f0fff4", fg="#2f855a")
    title_label.pack(pady=(30, 20))
    
    desc_label = tk.Label(dialog, text="Select output mode for the application:",
                          font=("Segoe UI", 11), bg="#f0fff4", fg="#276749")
    desc_label.pack(pady=(0, 20))
    
    button_frame = tk.Frame(dialog, bg="#f0fff4")
    button_frame.pack(pady=10)
    
    mcu_button = tk.Button(button_frame, text="Microcontroller\n(With Arduino)",
                          font=("Segoe UI", 11, "bold"),
                          bg="#48bb78", fg="white", activebackground="#38a169",
                          activeforeground="white", relief=tk.RAISED,
                          cursor="hand2", padx=25, pady=12, command=on_microcontroller,
                          bd=2, highlightthickness=0, width=18)
    mcu_button.pack(side=tk.LEFT, padx=8)
    
    display_button = tk.Button(button_frame, text="Display Only\n(Without Arduino)",
                              font=("Segoe UI", 11, "bold"),
                              bg="#ecc94b", fg="white", activebackground="#d69e2e",
                              activeforeground="white", relief=tk.RAISED,
                              cursor="hand2", padx=25, pady=12, command=on_display_only,
                              bd=2, highlightthickness=0, width=18)
    display_button.pack(side=tk.LEFT, padx=8)
    
    info_button = tk.Button(dialog, text="Project Info",
                           font=("Segoe UI", 10, "bold"),
                           bg="#4299e1", fg="white", activebackground="#3182ce",
                           activeforeground="white", relief=tk.RAISED,
                           cursor="hand2", padx=20, pady=8, command=on_info,
                           bd=2, highlightthickness=0)
    info_button.pack(pady=15)
    
    dialog.mainloop()
    
    return selected_mode[0]


def main():
    use_microcontroller = select_mode()
    
    if use_microcontroller is None:
        print("No mode selected, exiting...")
        return
    
    print("Initializing detection system...")
    from src.detection import DetectionSystem
    detection_system = DetectionSystem()
    
    print("Initializing serial communication...")
    serial_comm = SerialComm(enabled=use_microcontroller)
    
    root = tk.Tk()
    gui = SmartBinGUI(root, detection_system, serial_comm, use_microcontroller)
    
    def on_closing():
        gui.cleanup()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    print("Starting GUI...")
    root.mainloop()
    
    print("Application terminated.")


if __name__ == "__main__":
    main()
