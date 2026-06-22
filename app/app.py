import tkinter as tk
from PIL import Image, ImageTk
import cv2
import threading
import socket
import urllib.request
import os
import sys
import time
import serial
import webbrowser

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.detection import DetectionSystem

STABILITY_FRAMES_REQUIRED = 3

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
        self.last_internet_check = 0
        self.internet_connected = False
        self.frame_count = 0
        self.processing = False
        self.last_detection_result = None
        self.stability_start_time = 0
        self.api_connected = False
        self.last_processed_object = None
        self.last_processed_time = 0
        self.capturing = False
        self.no_detection_start_time = 0
        self.no_detection_timeout = 3.0
        
        self.setup_ui()
        self.setup_camera()
    
    def setup_ui(self):
        self.root.title("SMARTBIN - Automatic Waste Sorter")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0fff4")
        
        main_frame = tk.Frame(self.root, bg="#f0fff4")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
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
                          activeforeground="white", relief=tk.FLAT,
                          cursor="hand2", padx=30, pady=14, command=command,
                          bd=0, highlightthickness=0)
        return button
    
    def setup_camera(self):
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Could not open camera")
            print("Camera initialized successfully")
        except Exception as e:
            print(f"Error initializing camera: {e}")
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
    
    def stop_detection(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        self.stability_counter = 0
        self.last_detected_category = None
        self.last_decision_time = 0
        self.processing = False
        self.last_detection_result = None
        self.stability_start_time = 0
        self.api_connected = False
        self.last_processed_object = None
        self.last_processed_time = 0
        self.capturing = False
        self.no_detection_start_time = 0
        self.frame_count = 0
        self.internet_connected = False
        self.last_internet_check = 0
        
        self.object_label.config(text="--")
        self.category_label.config(text="--")
        self.source_label.config(text="--")
        self.stability_label.config(text=f"0/{STABILITY_FRAMES_REQUIRED} frames")
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
        
        ret, frame = self.cap.read()
        if ret:
            capture_folder = os.path.join(self.base_dir, "captures")
            os.makedirs(capture_folder, exist_ok=True)
            
            timestamp = int(time.time())
            capture_path = os.path.join(capture_folder, f"capture_{timestamp}.jpg")
            cv2.imwrite(capture_path, frame)
            print(f"Image captured: {capture_path}")
            
            detection_result = self.detection_system.detect(frame)
            print(f"Detection result: {detection_result}")
            
            self.last_detection_result = detection_result.copy()
            
            if detection_result["current_category"]:
                success = self.serial_comm.send_command(detection_result["current_category"])
                if success:
                    print(f"Serial command sent: {detection_result['current_category']}")
            
            self.last_processed_object = detection_result["best_class"]
            self.last_processed_time = time.time()
            
            current_time = cv2.getTickCount() / cv2.getTickFrequency()
            self.update_gui(frame, detection_result, False, current_time)
        else:
            self.show_error("Failed to capture image")
        
        self.capturing = False
    
    def detection_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            self.frame_count += 1
            current_time = cv2.getTickCount() / cv2.getTickFrequency()
            in_cooldown = False
            
            if self.processing:
                done_signal = self.serial_comm.read_done_signal()
                if done_signal:
                    self.processing = False
                    self.last_detection_result = None
                    print("Servo returned to initial position, system ready")
            
            if not self.processing:
                if self.frame_count % 3 == 0:
                    detection_result = self.detection_system.detect(frame, in_cooldown)
                    
                    if detection_result["best_class"] and not in_cooldown:
                        if (detection_result["best_class"] == self.last_processed_object and 
                            (current_time - self.last_processed_time) < 2.0):
                            self.stability_counter = 0
                        elif detection_result["best_class"] == self.last_detected_category:
                            self.stability_counter += 1
                        else:
                            self.stability_counter = 1
                            self.last_detected_category = detection_result["best_class"]
                        
                        if self.stability_counter >= STABILITY_FRAMES_REQUIRED:
                            detection_folder = os.path.join(self.base_dir, "detections")
                            os.makedirs(detection_folder, exist_ok=True)
                            
                            capture_path = os.path.join(detection_folder, f"detection_{int(current_time)}.jpg")
                            cv2.imwrite(capture_path, frame)
                            print(f"Image captured: {capture_path}")
                            print(f"YOLO Confidence: {detection_result['best_confidence']:.2f}")
                            
                            self.processing = True
                            
                            self.stability_counter = 0
                            self.last_detected_category = None
                            
                            detection_result["decision_source"] = f"Automatic - Custom YOLO Model"
                            
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
                                detection_result["decision_source"] = "No Detection - Waiting 3 seconds to restart"
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
            
            self.update_gui(frame, detection_result, in_cooldown, current_time)
    
    def check_internet_connection(self):
        try:
            urllib.request.urlopen('https://www.google.com', timeout=0.5)
            return True
        except:
            return False

    def update_gui(self, frame, detection_result, in_cooldown, current_time):
        if detection_result["best_box"] is not None:
            x1, y1, x2, y2 = map(int, detection_result["best_box"])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
        
        if self.internet_connected:
            cv2.circle(frame, (620, 20), 10, (0, 255, 0), -1)
        else:
            cv2.circle(frame, (620, 20), 10, (0, 0, 255), -1)
        
        if self.api_connected:
            cv2.circle(frame, (640, 20), 10, (255, 0, 0), -1)
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (640, 480))
        
        image = Image.fromarray(frame_resized)
        photo = ImageTk.PhotoImage(image=image)
        
        self.root.after(0, lambda: self.video_label.config(image=photo))
        self.root.after(0, lambda: setattr(self.video_label, 'image', photo))
        
        obj_text = "terdeteksi" if detection_result["best_class"] else "None"
        cat_text = detection_result["current_category"] if detection_result["current_category"] else "None"
        source_text = detection_result["decision_source"]
        
        if self.last_detected_category:
            stab_text = f"{min(self.stability_counter, STABILITY_FRAMES_REQUIRED)}/{STABILITY_FRAMES_REQUIRED} frames"
        else:
            stab_text = f"0/{STABILITY_FRAMES_REQUIRED} frames"
        
        serial_text = "Connected" if self.serial_comm.connected else "Disconnected"
        
        status_text = "Processing..." if self.processing else "Ready"
        
        if current_time - self.last_internet_check > 5.0:
            self.internet_connected = self.check_internet_connection()
            self.last_internet_check = current_time
        
        def update_all():
            self.object_label.config(text=obj_text)
            self.category_label.config(text=cat_text)
            self.source_label.config(text=source_text)
            self.stability_label.config(text=stab_text)
            self.serial_label.config(text=serial_text)
            self.status_label.config(text=status_text)
            self.status_label.config(fg="#ecc94b" if self.processing else "#48bb78")
        
        self.root.after(0, update_all)
    
    def show_error(self, message):
        error_window = tk.Toplevel(self.root)
        error_window.title("Error")
        error_window.geometry("450x180")
        error_window.configure(bg="#e53e3e")
        
        error_label = tk.Label(error_window, text=message, font=("Segoe UI", 12),
                               bg="#e53e3e", fg="white", wraplength=400)
        error_label.pack(expand=True, padx=25, pady=25)
    
    def cleanup(self):
        self.stop_detection()
        if self.cap is not None:
            self.cap.release()
        self.serial_comm.close()


def show_info_dialog():
    info_window = tk.Toplevel()
    info_window.title("Project Info")
    info_window.geometry("700x600")
    info_window.configure(bg="#f0fff4")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    text_frame = tk.Frame(info_window, bg="#f0fff4")
    text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    info_text = tk.Text(text_frame, font=("Segoe UI", 10), bg="#f0fff4", fg="#276749",
                        wrap=tk.WORD, bd=0, highlightthickness=0)
    info_text.pack(fill=tk.BOTH, expand=True)
    
    info_content = """
SMARTBIN - Automatic Waste Sorter
=================================

Dataset:
--------
Source: Roboflow
Link: https://app.roboflow.com/michael-juferson-balla-tangkilisan/klasifikasi-sampah-sdtpy-09cl3/browse?queryText=&pageSize=50&startingIndex=0&browseQuery=true

Classes:
- Organik (Organic waste)
- Nonorganik (Non-organic waste)
- Sampah Berbahaya (Hazardous waste)

Model:
------
Architecture: YOLOv8n (Nano)
Framework: Ultralytics
Training: Custom trained on waste classification dataset

Evaluation:
"""
    
    try:
        results_csv = os.path.join(base_dir, "runs", "waste_classification", "results.csv")
        if os.path.exists(results_csv):
            info_content += "\nEvaluation results available in: runs/waste_classification/results.csv\n"
        else:
            info_content += "\nRun 'python src/main.py --mode evaluate' to generate evaluation results\n"
    except:
        info_content += "\nRun 'python src/main.py --mode evaluate' to generate evaluation results\n"
    
    info_content += """
Usage:
------
GUI Application: python app/app.py
Training Pipeline: python src/main.py

Modes:
- Microcontroller (With Arduino): Sends serial commands to control servo motors
- Display Only (Without Arduino): Display detection results only

Configuration:
--------------
Confidence Threshold: 0.7 (70%)
Stability Frames Required: 3
Serial Port: COM4
Baud Rate: 115200
"""
    
    info_text.insert(tk.END, info_content)
    info_text.config(state=tk.DISABLED)
    
    close_button = tk.Button(info_window, text="Close", font=("Segoe UI", 11, "bold"),
                             bg="#48bb78", fg="white", activebackground="#38a169",
                             activeforeground="white", relief=tk.FLAT,
                             cursor="hand2", padx=30, pady=10,
                             command=info_window.destroy,
                             bd=0, highlightthickness=0)
    close_button.pack(pady=10)


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
                          activeforeground="white", relief=tk.FLAT,
                          cursor="hand2", padx=25, pady=12, command=on_microcontroller,
                          bd=0, highlightthickness=0, width=18)
    mcu_button.pack(side=tk.LEFT, padx=8)
    
    display_button = tk.Button(button_frame, text="Display Only\n(Without Arduino)",
                              font=("Segoe UI", 11, "bold"),
                              bg="#ecc94b", fg="white", activebackground="#d69e2e",
                              activeforeground="white", relief=tk.FLAT,
                              cursor="hand2", padx=25, pady=12, command=on_display_only,
                              bd=0, highlightthickness=0, width=18)
    display_button.pack(side=tk.LEFT, padx=8)
    
    info_button = tk.Button(dialog, text="Project Info",
                           font=("Segoe UI", 10, "bold"),
                           bg="#4299e1", fg="white", activebackground="#3182ce",
                           activeforeground="white", relief=tk.FLAT,
                           cursor="hand2", padx=20, pady=8, command=on_info,
                           bd=0, highlightthickness=0)
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
