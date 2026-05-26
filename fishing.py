import sys
import ctypes
import cv2
import numpy as np
import dxcam
import time
import random
import configparser
import os

# ==============================================================================
# 1. DPI AWARENESS FIX
# ==============================================================================
if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2) # PROCESS_PER_MONITOR_DPI_AWARE
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

# ==============================================================================
# 2. INPUT CONTROLLER CLASS (Win32 SendInput API - Sinkron Murni)
# ==============================================================================
PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort), ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong), ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong), ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong), ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput), ("mi", MouseInput), ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("ii", Input_I)]

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008 

class InputController:
    def __init__(self):
        self.mouse_is_pressed = False

    def safe_mouse_down(self):
        if not self.mouse_is_pressed:
            extra = ctypes.c_ulong(0)
            ii_ = Input_I()
            ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, ctypes.pointer(extra))
            x = Input(ctypes.c_ulong(INPUT_MOUSE), ii_)
            ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
            self.mouse_is_pressed = True

    def safe_mouse_up(self):
        if self.mouse_is_pressed:
            extra = ctypes.c_ulong(0)
            ii_ = Input_I()
            ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_LEFTUP, 0, ctypes.pointer(extra))
            x = Input(ctypes.c_ulong(INPUT_MOUSE), ii_)
            ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
            self.mouse_is_pressed = False

    def single_click_instant(self):
        """Klik kilat sinkron murni tanpa antrean event loop untuk Fase 2"""
        duration = random.uniform(0.02, 0.04) 
        self.safe_mouse_down()
        time.sleep(duration)
        self.safe_mouse_up()

    def hold_key_scancode(self, hexKeyCode, duration):
        extra = ctypes.c_ulong(0)
        ii_down = Input_I()
        ii_down.ki = KeyBdInput(0, hexKeyCode, KEYEVENTF_SCANCODE, 0, ctypes.pointer(extra))
        x_down = Input(ctypes.c_ulong(INPUT_KEYBOARD), ii_down)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x_down), ctypes.sizeof(x_down))
        
        time.sleep(duration)
        
        ii_up = Input_I()
        ii_up.ki = KeyBdInput(0, hexKeyCode, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP, 0, ctypes.pointer(extra))
        x_up = Input(ctypes.c_ulong(INPUT_KEYBOARD), ii_up)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x_up), ctypes.sizeof(x_up))

    def tap_key_scancode(self, hexKeyCode):
        self.hold_key_scancode(hexKeyCode, random.uniform(0.12, 0.18))

    def type_string(self, text: str):
        """Mengetik teks secara berurutan langsung ke konsol game."""
        scancodes = {
            'f': 0x21, 'i': 0x17, 'x': 0x2D, 'u': 0x16,
            'r': 0x13, 'e': 0x12, 'l': 0x26, 'o': 0x18, 'a': 0x1E, 'd': 0x20,
            's': 0x1F, 'k': 0x25, 'n': 0x31
        }
        for char in text.lower():
            if char in scancodes:
                self.tap_key_scancode(scancodes[char])
                time.sleep(random.uniform(0.03, 0.06))

    def is_key_pressed(self, vk_code):
        return (ctypes.windll.user32.GetAsyncKeyState(vk_code) & 0x8000) != 0

    def get_cursor_pos(self):
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        pt = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.pointer(pt))
        return pt.x, pt.y

    def smooth_move_mouse(self, target_x, target_y, steps=20, duration=0.20):
        start_x, start_y = self.get_cursor_pos()
        dx = target_x - start_x
        dy = target_y - start_y
        sleep_time = duration / steps
        for i in range(1, steps + 1):
            curr_x = int(start_x + (dx * i / steps))
            curr_y = int(start_y + (dy * i / steps))
            ctypes.windll.user32.SetCursorPos(curr_x, curr_y)
            time.sleep(sleep_time)


# ==============================================================================
# 3. FISHING BOT CLASS (Main Engine - Sinkron Murni)
# ==============================================================================
class FishingBot:
    def __init__(self):
        self.io = InputController()
        self.load_config()
        
        self.region = (
            int(400 * self.scale_x), 
            int(200 * self.scale_y), 
            int(1600 * self.scale_x), 
            int(1080 * self.scale_y)
        )
        self.camera = dxcam.create(output_color="BGR")
        self.camera.start(target_fps=60, region=self.region)

        self.lower_grad = np.array([0, 120, 165]) 
        self.upper_grad = np.array([50, 255, 255])
        self.lower_white = np.array([0, 0, 160])
        self.upper_white = np.array([179, 50, 255])
        
        self.state = "FASE_0_STANDBY"
        self.is_debug_mode = False
        self.debug_key_pressed = False
        self.afk_mode_enabled = False
        self.afk_key_pressed = False
        self.last_afk_time = time.time()
        self.fase1_start_time = 0
        
        self.timeout_strike_counter = 0
        self.MAX_TIMEOUT_STRIKES = 2 

        self.reset_minigame_state()

    def load_config(self):
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        
        config_file_path = os.path.join(application_path, 'config.ini')
        config = configparser.ConfigParser()

        if not os.path.exists(config_file_path):
            config['ENGINE'] = {
                'SCREEN_WIDTH': '1920',
                'SCREEN_HEIGHT': '1080',
                'ABSOLUTE_MAX_GREEN': '365',  
                'SUCCESS_THRESHOLD': '380',   
                'SAFETY_BUFFER': '15',
                'MAX_BAND_HIGH': '100',
                'MIN_SWING': '120',
                'TIGHT_GRIP_THRESHOLD': '80',
                'TIGHT_GRIP_SWING': '50',
                'TIMEOUT_SECONDS': '30', 
                'AFK_INTERVAL_MINUTES': '40',
                'CAST_DELAY_SECONDS': '4.8'
            }
            with open(config_file_path, 'w') as configfile:
                config.write(configfile)

        config.read(config_file_path)
        
        self.screen_w = int(config['ENGINE'].get('SCREEN_WIDTH', '1920'))
        self.screen_h = int(config['ENGINE'].get('SCREEN_HEIGHT', '1080'))
        self.timeout_sec = int(config['ENGINE'].get('TIMEOUT_SECONDS', '30')) 
        self.afk_interval = float(config['ENGINE'].get('AFK_INTERVAL_MINUTES', '40'))
        self.cast_delay = float(config['ENGINE'].get('CAST_DELAY_SECONDS', '4.8'))
        
        self.scale_x = self.screen_w / 1920.0
        self.scale_y = self.screen_h / 1080.0

        self.MAX_GREEN = int(int(config['ENGINE'].get('ABSOLUTE_MAX_GREEN', '365')) * self.scale_y)
        self.SUCCESS_THRESHOLD = int(int(config['ENGINE'].get('SUCCESS_THRESHOLD', '380')) * self.scale_y)
        self.SAFETY_BUFFER = int(int(config['ENGINE'].get('SAFETY_BUFFER', '15')) * self.scale_y)
        self.MIN_SWING = int(int(config['ENGINE'].get('MIN_SWING', '120')) * self.scale_y)
        self.MAX_BAND_HIGH = int(int(config['ENGINE'].get('MAX_BAND_HIGH', '100')) * self.scale_y)
        self.TIGHT_GRIP_THRESHOLD = int(int(config['ENGINE'].get('TIGHT_GRIP_THRESHOLD', '80')) * self.scale_y)
        self.TIGHT_GRIP_SWING = int(int(config['ENGINE'].get('TIGHT_GRIP_SWING', '50')) * self.scale_y)

    def reset_minigame_state(self):
        self.phase3_start_time = 0
        self.last_seen_time = 0
        self.max_white_h = 0
        self.max_grad_h = 0
        self.prev_grad_h = 0
        self.prev_white_h = 0
        self.prev_selisih = 0
        self.delta_selisih = 0
        self.is_cooling_down = True
        self.bar_ever_found = False
        self.in_rescue_mode = False
        self.hold_stall_counter = 0

    def interruptible_sleep(self, total_duration):
        """
        [BARU & SANGAT PENTING]
        Menggantikan time.sleep() makro agar Panic Button [X] tetap terdeteksi instan.
        Memecah durasi panjang menjadi irisan 0.05 detik yang mengecek tombol keyboard.
        Menghasilkan True jika diinterupsi oleh Panic Button X, False jika selesai normal.
        """
        start_sleep = time.time()
        while time.time() - start_sleep < total_duration:
            if self.io.is_key_pressed(0x58): # Tombol 'X' ditekan saat jeda tunggu
                return True
            time.sleep(0.05)
        return False

    def execute_fixui_recovery(self):
        print(f"\n[⚠️] DETEKSI ERROR: Timeout berturut-turut sebanyak {self.timeout_strike_counter}x!")
        print("[🔧] Memulai Proses Pembersihan UI via Konsol F8...")
        
        self.io.tap_key_scancode(0x42) # Scancode F8
        time.sleep(0.4)
        
        self.io.type_string("fixui")
        self.io.tap_key_scancode(0x1C) # Enter
        time.sleep(0.4)
        
        self.io.tap_key_scancode(0x42) # Scancode F8
        print("[✅] UI Sukses Di-refresh! Mengembalikan siklus mancing harian...\n")
        time.sleep(1.0)
        self.timeout_strike_counter = 0

    def perform_auto_collect(self):
        print("\n>>> TARGET TERCAPAI! Mengeksekusi Auto-Collect...")
        time.sleep(0.3) 
        base_x = random.randint(800, 850)
        base_y = random.randint(920, 940)
        collect_x = int(base_x * self.scale_x)
        collect_y = int(base_y * self.scale_y)
        self.io.smooth_move_mouse(collect_x, collect_y)
        time.sleep(random.uniform(0.1, 0.2)) 
        self.io.single_click_instant()
        print(f">>> Auto-Collect Selesai di (X:{collect_x}, Y:{collect_y}).\n")

    def perform_afk_routine(self):
        print("\n>>> [AFK ROUTINE] Memulai Anti-AFK & Makan/Minum...")
        print(">>> Menahan [D] selama 1.5 detik...")
        self.io.hold_key_scancode(0x20, 1.5)
        print(">>> Menahan [A] selama 1.5 detik...")
        self.io.hold_key_scancode(0x1E, 1.5)
        print(">>> Menahan [W] selama 1.0 detik...")
        self.io.hold_key_scancode(0x11, 1.0)
        print(">>> Makan (Tekan 4), jeda 6 detik...")
        self.io.tap_key_scancode(0x05)
        time.sleep(6.0)
        print(">>> Minum (Tekan 5), jeda 6 detik...")
        self.io.tap_key_scancode(0x06)
        time.sleep(6.0)
        print(">>> [AFK ROUTINE] Selesai.\n")

    def print_banner(self):
        print("========================================")
        print("      FISHING PIXEL BOT                 ")
        print("========================================")
        print(f"[CONFIG] Monitor : {self.screen_w}x{self.screen_h} (DPI Fixed)")
        print(f"[CONFIG] Max Grn : {self.MAX_GREEN} | Sukses: >{self.SUCCESS_THRESHOLD}")
        print(f"[CONFIG] Timeout : {self.timeout_sec} Detik (Strike: {self.MAX_TIMEOUT_STRIKES}x)")
        print(f"[CONFIG] Cast Dly: {self.cast_delay} Detik")
        print("========================================")
        print("[8] - Toggle Live Debug View")
        print("[9] - Exit Program")
        print("[7] - TOGGLE AUTO-EAT/AFK MODE")
        print("[3] - MANUALLY START FISHING")
        print("[X] - PANIC BUTTON (Instant Interrupt)")
        print("========================================")

    def run(self):
        self.print_banner()
        try:
            while True:
                # --------------------------------------------------------------
                # KEYBOARD INTERRUPT MONITORING (100% KILAT SINKRON)
                # --------------------------------------------------------------
                if self.io.is_key_pressed(0x39): break # Tombol '9' Exit
                
                if self.io.is_key_pressed(0x38): # Tombol '8' Debug
                    if not self.debug_key_pressed:
                        self.is_debug_mode = not self.is_debug_mode
                        if not self.is_debug_mode: cv2.destroyWindow("Live Debug")
                        self.debug_key_pressed = True
                else:
                    self.debug_key_pressed = False

                if self.io.is_key_pressed(0x37): # Tombol '7' AFK Mode
                    if not self.afk_key_pressed:
                        self.afk_mode_enabled = not self.afk_mode_enabled
                        status = "ON" if self.afk_mode_enabled else "OFF"
                        print(f"\n[!] AUTO-EAT / AFK MODE: {status}")
                        self.afk_key_pressed = True
                else:
                    self.afk_key_pressed = False

                # [PANIC BUTTON X] - Respon instan di loop utama
                if self.io.is_key_pressed(0x58): 
                    if self.state != "FASE_0_STANDBY":
                        print("\n[🚨] PANIC INTERRUPT! Kembali ke Standby...")
                        self.io.safe_mouse_up() 
                        self.state = "FASE_0_STANDBY"
                        self.reset_minigame_state()
                        time.sleep(0.5) 
                        continue 

                frame = self.camera.get_latest_frame()
                if frame is None: continue
                debug_frame = frame.copy() if self.is_debug_mode else None
                action_text = "IDLE"
                action_color = (255, 255, 255)

                try:
                    # --------------------------------------------------------------
                    # STATE MACHINE OPERASIONAL BOT
                    # --------------------------------------------------------------
                    if self.state == "FASE_0_STANDBY":
                        action_text = "STANDBY: Tekan '3' untuk mulai..."
                        action_color = (0, 255, 255) 
                        if self.io.is_key_pressed(0x33):
                            print("\n>>> Memulai siklus pemantauan...")
                            self.state = "FASE_1_WAITING"
                            self.fase1_start_time = time.time() 
                            time.sleep(1.0) 

                    elif self.state == "FASE_1_WAITING":
                        if time.time() - self.fase1_start_time > self.timeout_sec: 
                            print(f"\n[!] TIMEOUT: Tidak ada respons ikan dalam {self.timeout_sec} detik.")
                            self.timeout_strike_counter += 1 
                            
                            if self.timeout_strike_counter >= self.MAX_TIMEOUT_STRIKES:
                                self.execute_fixui_recovery()
                            
                            self.io.tap_key_scancode(0x04) # Ketuk tombol '3'
                            self.fase1_start_time = time.time() 
                            time.sleep(1.0) 
                            continue 

                        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                        mask_grad = cv2.inRange(hsv_frame, self.lower_grad, self.upper_grad)
                        contours, _ = cv2.findContours(mask_grad, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                        if contours:
                            c = max(contours, key=cv2.contourArea)
                            if cv2.contourArea(c) > 20: 
                                x, y, w, h = cv2.boundingRect(c)
                                min_h, max_h = max(1, int(3 * self.scale_y)), int(15 * self.scale_y)
                                min_w = int(50 * self.scale_x) 
                                
                                if (min_h <= h <= max_h) and w > min_w and w > (h * 4):
                                    action_text = "FASE 2 DETECTED! HOOKING..."
                                    
                                    # KEMBALI KILAT SINKRON: Deteksi umpan langsung memukul instan tanpa antrean
                                    self.io.single_click_instant()
                                    time.sleep(0.2) 
                                    self.io.safe_mouse_up() 
                                    
                                    self.timeout_strike_counter = 0
                                    self.reset_minigame_state()
                                    self.state = "FASE_3_MINIGAME"
                                    self.phase3_start_time = time.time() 
                                    self.last_seen_time = time.time() 
                                else:
                                    action_text = f"NOISE REJ (W:{w} H:{h})"

                    elif self.state == "FASE_3_MINIGAME":
                        if time.time() - self.phase3_start_time > 480:
                            self.io.safe_mouse_up()
                            print("\n[!] MINIGAME TIMEOUT (Terlalu Lama). Memutus paksa...")
                            self.state = "FASE_1_WAITING"
                            self.fase1_start_time = time.time()
                            continue

                        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                        mask_grad = cv2.inRange(hsv_frame, self.lower_grad, self.upper_grad)
                        mask_white = cv2.inRange(hsv_frame, self.lower_white, self.upper_white)
                        
                        contours_g, _ = cv2.findContours(mask_grad, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        contours_w, _ = cv2.findContours(mask_white, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        
                        valid_bar_found = False
                        grad_h, white_h = 0, 0
                        rescue_mode = False
                        white_rescue_mode = False
                        xw, yw, ww, hw = 0, 0, 0, 0

                        # --- DETEKSI GEOMETRI KETAT BAR PUTIH ---
                        if contours_w:
                            contours_w = sorted(contours_w, key=cv2.contourArea, reverse=True)
                            for cw in contours_w:
                                if cv2.contourArea(cw) >= 2: 
                                    x_tmp, y_tmp, w_tmp, h_tmp = cv2.boundingRect(cw)
                                    w_min = max(1, int(2 * self.scale_x))
                                    w_max = int(25 * self.scale_x)
                                    
                                    if h_tmp >= int(5 * self.scale_y) and w_min <= w_tmp <= w_max and h_tmp >= (w_tmp * 1.2):
                                        if self.bar_ever_found and h_tmp < (self.prev_white_h - int(80 * self.scale_y)):
                                            continue
                                        
                                        xw, yw, ww, hw = x_tmp, y_tmp, w_tmp, h_tmp
                                        white_h = hw
                                        valid_bar_found = True  
                                        self.bar_ever_found = True 
                                        self.last_seen_time = time.time()
                                        
                                        if white_h > self.max_white_h: 
                                            self.max_white_h = white_h
                                            
                                        if self.is_debug_mode:
                                            cv2.rectangle(debug_frame, (xw, yw), (xw+ww, yw+hw), (200, 200, 200), 2)
                                        break 

                        # --- DETEKSI BAR HIJAU ---
                        if valid_bar_found and contours_g:
                            contours_g = sorted(contours_g, key=cv2.contourArea, reverse=True)
                            for cg in contours_g:
                                if cv2.contourArea(cg) >= 2: 
                                    xg, yg, wg, hg = cv2.boundingRect(cg)
                                    gap = xg - (xw + ww)
                                    
                                    if abs(yg - yw) < int(30 * self.scale_y) and (int(3 * self.scale_x) <= gap <= int(50 * self.scale_x)):
                                        grad_h = hg
                                        if grad_h > self.max_grad_h:
                                            self.max_grad_h = grad_h
                                            
                                        if self.is_debug_mode:
                                            cv2.rectangle(debug_frame, (xg, yg), (xg+wg, yg+hg), (100, 255, 100), 2)
                                        break

                        # --------------------------------------------------------------
                        # CORE ENGINE MATEMATIKA (KONFIGURASI TUNING EMAS 170PX ANDA)
                        # --------------------------------------------------------------
                        if valid_bar_found:
                            selisih = grad_h - white_h
                            self.delta_selisih = selisih - self.prev_selisih
                            delta_white = white_h - self.prev_white_h 

                            self.prev_grad_h = grad_h
                            self.prev_white_h = white_h
                            self.prev_selisih = selisih

                            max_safe_selisih = self.MAX_GREEN - white_h - self.SAFETY_BUFFER
                            BAND_HIGH = max(int(10 * self.scale_y), min(self.MAX_BAND_HIGH, max_safe_selisih))
                            
                            if white_h < int(30 * self.scale_y):
                                current_swing = int(50 * self.scale_y) 
                                BAND_HIGH = max(BAND_HIGH, int(80 * self.scale_y)) 
                            elif white_h < int(100 * self.scale_y):
                                current_swing = int(80 * self.scale_y) 
                                BAND_HIGH = max(BAND_HIGH, int(100 * self.scale_y))
                            elif white_h > (self.SUCCESS_THRESHOLD - int(40 * self.scale_y)):
                                current_swing = int(170 * self.scale_y) # Tuning 170px Anda
                            else:
                                current_swing = self.MIN_SWING

                            if white_h < self.TIGHT_GRIP_THRESHOLD:
                                current_swing = min(current_swing, self.TIGHT_GRIP_SWING) 

                            BAND_LOW = BAND_HIGH - current_swing
                            
                            if white_h > (self.SUCCESS_THRESHOLD - int(40 * self.scale_y)):
                                BAND_LOW = max(BAND_LOW, -int(170 * self.scale_y)) # Lantai 170px dibuka lebar
                            else:
                                BAND_LOW = max(BAND_LOW, -int(60 * self.scale_y))

                            min_green_floor = int(45 * self.scale_y)
                            if (white_h + BAND_LOW) < min_green_floor:
                                BAND_LOW = min_green_floor - white_h

                            BAND_HIGH = int(BAND_HIGH * random.uniform(0.98, 1.02))
                            BAND_LOW  = int(BAND_LOW  * random.uniform(0.98, 1.02))

                            delta_clamp = max(int(-15 * self.scale_y), min(int(15 * self.scale_y), self.delta_selisih))
                            effective_band_high = max(BAND_LOW + int(10 * self.scale_y), BAND_HIGH - max(0, delta_clamp))
                            effective_band_low  = BAND_LOW + min(0, delta_clamp)
                                 
                            if self.is_cooling_down:
                                if selisih <= effective_band_low:
                                    self.is_cooling_down = False
                            else:
                                if selisih >= effective_band_high:
                                    self.is_cooling_down = True

                            # Rescue Bawah
                            if 0 < white_h < int(35 * self.scale_y):
                                if grad_h < (self.MAX_GREEN - int(25 * self.scale_y)):
                                    self.is_cooling_down = False
                                    white_rescue_mode = True
                                    self.hold_stall_counter = 0

                            # Rescue Atas
                            GREEN_RESCUE_ENTER = self.MAX_GREEN - int(5  * self.scale_y)
                            GREEN_RESCUE_EXIT  = self.MAX_GREEN - int(135 * self.scale_y) # Jeda keluar 135px Anda
                            
                            if grad_h >= GREEN_RESCUE_ENTER:
                                self.in_rescue_mode = True
                            elif grad_h <= GREEN_RESCUE_EXIT:
                                self.in_rescue_mode = False

                            if self.in_rescue_mode:
                                self.is_cooling_down = True
                                rescue_mode = True
                                white_rescue_mode = False
                                self.hold_stall_counter = 0

                            # Smart Stall Detection
                            STALL_FRAMES = 12
                            if not self.is_cooling_down and not white_rescue_mode:
                                if self.delta_selisih <= 1 and delta_white <= 1:
                                    self.hold_stall_counter += 1
                                else:
                                    self.hold_stall_counter = 0
                                    
                                if self.hold_stall_counter >= STALL_FRAMES:
                                    self.is_cooling_down = True
                                    self.hold_stall_counter = 0
                            else:
                                self.hold_stall_counter = 0

                            # Sinyal Klik Per-Frame
                            if self.is_cooling_down:
                                self.io.safe_mouse_up()
                                if rescue_mode:
                                    action_text, action_color = f"GREEN RESCUE! G:{grad_h} -> RELEASE PAKSA", (255, 100, 255)
                                else:
                                    action_text, action_color = f"SEL:{selisih:+d} BND:[{BAND_LOW}~{BAND_HIGH}] -> RELEASE", (0, 0, 255)
                            else:
                                self.io.safe_mouse_down()
                                if white_rescue_mode:
                                    action_text, action_color = f"WHITE RESCUE! W:{white_h} -> HOLD PAKSA", (0, 255, 255)
                                else:
                                    stall_tag = f" [STALL:{self.hold_stall_counter}/{STALL_FRAMES}]" if self.hold_stall_counter > 0 else ""
                                    action_text, action_color = f"SEL:{selisih:+d} BND:[{BAND_LOW}~{BAND_HIGH}]{stall_tag} -> HOLD", (0, 255, 0)

                            if self.is_debug_mode:
                                try:
                                    rescue_tag = " [RESCUE]" if self.in_rescue_mode else ""
                                    cv2.putText(debug_frame, f"W:{white_h} G:{grad_h} SEL:{selisih:+d}{rescue_tag}", (xw, yw-10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
                                    cv2.putText(debug_frame, f"dSEL:{self.delta_selisih:+d} BAND:[{effective_band_low}~{effective_band_high}] STALL:{self.hold_stall_counter}/{STALL_FRAMES}", (xw, yw-25), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (200, 200, 100), 1)
                                    y_band_low, y_band_high = yw + white_h + effective_band_low, yw + white_h + effective_band_high
                                    cv2.line(debug_frame, (xw-15, y_band_low),  (xw+30, y_band_low),  (0, 255, 0), 2)
                                    cv2.line(debug_frame, (xw-15, y_band_high), (xw+30, y_band_high), (0, 0, 255), 2)
                                except: pass

                        # --- LOGIKA DEKLARASI SIKLUS BERAKHIR ---
                        if not valid_bar_found:
                            time_lost = time.time() - self.last_seen_time
                            time_in_phase3 = time.time() - self.phase3_start_time
                            
                            if time_in_phase3 < 2.0 and self.max_white_h < int(10 * self.scale_y):
                                self.io.safe_mouse_down()
                                action_text, action_color = "INITIAL PULL (FORCED TENSION)...", (255, 100, 100)
                            elif self.bar_ever_found and time_lost < 0.6:
                                self.io.safe_mouse_up() 
                                self.is_cooling_down = True 
                                action_text, action_color = "BAR HILANG / FLICKER...", (0, 165, 255)
                            else:
                                self.io.safe_mouse_up()
                                print(f">>> UI Hilang.")
                                print(f"    HASIL: Max White: {self.max_white_h}px | Max Green: {self.max_grad_h}px | Target: >{self.SUCCESS_THRESHOLD}px")
                                
                                if self.max_white_h >= self.SUCCESS_THRESHOLD: 
                                    print(f"    STATUS: SUKSES\n")
                                    self.perform_auto_collect()
                                    if self.afk_mode_enabled and (time.time() - self.last_afk_time) >= (self.afk_interval * 60):
                                        self.perform_afk_routine()
                                        self.last_afk_time = time.time()
                                else:
                                    print(f"    STATUS: GAGAL / PUTUS\n")
                                    
                                print(f">>> Siklus Selesai. Melempar pancingan baru dalam {self.cast_delay} detik...")
                                
                                # Menggunakan Micro-Sleep Loop untuk cast_delay: Panic Button X tetap aktif
                                if self.interruptible_sleep(self.cast_delay):
                                    continue # Jika mendeteksi 'X', langsung potong siklus ke standby
                                    
                                self.io.tap_key_scancode(0x04) # Ketuk tombol '3'
                                
                                action_text = "AUTO-CASTING..."
                                self.state = "FASE_1_WAITING" 
                                self.reset_minigame_state()
                                self.fase1_start_time = time.time() 
                                
                                if self.interruptible_sleep(1.0):
                                    continue
                                    
                except Exception as inner_e:
                    print(f"Frame Processing Exception: {inner_e}")
                    pass

                # Rendering Antarmuka Live Debug
                if self.is_debug_mode and debug_frame is not None:
                    cv2.putText(debug_frame, f"State: {self.state}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                    cv2.putText(debug_frame, f"Action: {action_text}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, action_color, 2)
                    afk_status = "ON" if self.afk_mode_enabled else "OFF"
                    cv2.putText(debug_frame, f"AFK Mode: {afk_status}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                    if self.afk_mode_enabled:
                        time_left = max(0, (self.afk_interval * 60) - (time.time() - self.last_afk_time))
                        cv2.putText(debug_frame, f"AFK Timer: {int(time_left)}s", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                    cv2.imshow("Live Debug", debug_frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except KeyboardInterrupt:
            print("\n[!] Dihentikan secara paksa oleh user (Ctrl + C). Membersihkan resource...")
        except Exception as e:
            print(f"\n[!] Fatal Error: {e}")
        finally:
            self.io.safe_mouse_up()
            self.camera.stop()
            cv2.destroyAllWindows()
            os._exit(0)

if __name__ == "__main__":
    bot = FishingBot()
    bot.run()
