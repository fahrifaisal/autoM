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
        scancodes = {
            'f': 0x21, 'i': 0x17, 'x': 0x2D, 'u': 0x16,
            'r': 0x13, 'e': 0x12, 'l': 0x26, 'o': 0x18, 'a': 0x1E, 'd': 0x20,
            's': 0x1F, 'k': 0x25, 'n': 0x31, 'q': 0x10, 't': 0x14
        }
        for char in text.lower():
            if char in scancodes:
                self.tap_key_scancode(scancodes[char])
                time.sleep(random.uniform(0.04, 0.07))

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
# 3. FISHING BOT CLASS (Main Engine - Sinkron Murni Lightweight)
# ==============================================================================
class FishingBot:
    def __init__(self):
        self.io = InputController()
        self.load_config()
        
        self.region = (
            int(600 * self.scale_x), 
            int(250 * self.scale_y), 
            int(1200 * self.scale_x), 
            int(900 * self.scale_y)
        )
        
        # --- [CONFIG ATTACHED] TARGET FPS KINI DIBACA DARI CONFIG.INI ---
        self.camera = dxcam.create(output_color="BGR")
        self.camera.start(target_fps=self.target_fps, region=self.region)

        self.lower_grad = np.array([0, 120, 165]) 
        self.upper_grad = np.array([50, 255, 255])
        self.lower_white = np.array([0, 0, 160])
        self.upper_white = np.array([179, 50, 255])
        
        self.state = "FASE_0_STANDBY"
        self.is_debug_mode = False
        self.debug_key_pressed = False
        self.afk_mode_enabled = False
        self.afk_key_pressed = False
        
        self.auto_quit_enabled = False
        self.auto_quit_key_pressed = False
        
        self.last_afk_time = time.time()
        self.fase1_start_time = 0
        self.timeout_strike_counter = 0
        self.last_cmd_log_time = 0 

        self.reset_minigame_state()

    def load_config(self):
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        
        config_file_path = os.path.join(application_path, 'config.ini')
        config = configparser.ConfigParser()

        # Pembaruan otomatis templat config baru jika file belum ada
        if not os.path.exists(config_file_path):
            config['ENGINE'] = {
                'SCREEN_WIDTH': '1920',
                'SCREEN_HEIGHT': '1080',
                'TARGET_FPS': '120',            
                'STALL_FRAMES': '9999',          
                'ABSOLUTE_MAX_GREEN': '360',  
                'SUCCESS_THRESHOLD': '390',   
                'SAFETY_BUFFER': '15',
                'MAX_BAND_HIGH': '100',
                'MIN_SWING': '120',
                'TIGHT_GRIP_THRESHOLD': '80',
                'TIGHT_GRIP_SWING': '50',
                'TIMEOUT_SECONDS': '30',      
                'AFK_INTERVAL_MINUTES': '40',
                'CAST_DELAY_SECONDS': '5.0'   
            }
            with open(config_file_path, 'w') as configfile:
                config.write(configfile)

        config.read(config_file_path)
        
        self.screen_w = int(config['ENGINE'].get('SCREEN_WIDTH', '1920'))
        self.screen_h = int(config['ENGINE'].get('SCREEN_HEIGHT', '1080'))
        
        # Ambil nilai FPS dan Stall murni dari konfigurasi eksternal
        self.target_fps = int(config['ENGINE'].get('TARGET_FPS', '120'))
        self.config_stall_frames = int(config['ENGINE'].get('STALL_FRAMES', '9999'))
        
        self.timeout_sec = int(config['ENGINE'].get('TIMEOUT_SECONDS', '30')) 
        self.afk_interval = float(config['ENGINE'].get('AFK_INTERVAL_MINUTES', '40'))
        self.cast_delay = float(config['ENGINE'].get('CAST_DELAY_SECONDS', '5.0'))
        
        self.scale_x = self.screen_w / 1920.0
        self.scale_y = self.screen_h / 1080.0

        self.MAX_GREEN = int(int(config['ENGINE'].get('ABSOLUTE_MAX_GREEN', '360')) * self.scale_y)
        self.SUCCESS_THRESHOLD = int(int(config['ENGINE'].get('SUCCESS_THRESHOLD', '390')) * self.scale_y)
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
        start_sleep = time.time()
        while time.time() - start_sleep < total_duration:
            if self.io.is_key_pressed(0x58): 
                return True
            time.sleep(0.05)
        return False

    def execute_fixui_recovery(self):
        self.io.tap_key_scancode(0x42) # Buka Konsol F8
        time.sleep(0.5)                
        self.io.type_string("fixui")   
        time.sleep(0.2)
        self.io.tap_key_scancode(0x1C) # Tekan Enter
        time.sleep(0.6)                
        self.io.tap_key_scancode(0x42) # Tutup Konsol F8
        time.sleep(0.8)                

    def execute_force_quit_game(self):
        print("\n[🚨] MENGEKSEKUSI PROSEDUR AUTO-QUIT GAME DARURAT...")
        self.io.safe_mouse_up()
        
        self.io.tap_key_scancode(0x42) 
        time.sleep(0.4)
        self.io.type_string("quit")    
        self.io.tap_key_scancode(0x1C) 
        
        print("[✅] Sinyal penutupan game sukses dikirim. Menghentikan bot secara total.")
        time.sleep(1.0)
        self.camera.stop()
        os._exit(0) 

    def perform_auto_collect(self):
        print("\n>>> TARGET TERCAPAI! Mengeksekusi Auto-Collect...")
        time.sleep(0.8) 
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
        print(">>> Mengetuk [D]...")
        self.io.hold_key_scancode(0x20, 1.0)
        if self.interruptible_sleep(0.05): return
        print(">>> Mengetuk [A]...")
        self.io.hold_key_scancode(0x1E, 1.0)
        if self.interruptible_sleep(0.05): return
        
        print(">>> Makan (Tekan 4), jeda animasi 7 detik...")
        self.io.tap_key_scancode(0x05)
        if self.interruptible_sleep(7.0): return
        print(">>> Minum (Tekan 5), jeda animasi 7 detik...")
        self.io.tap_key_scancode(0x06)
        if self.interruptible_sleep(7.0): return
        print(">>> [AFK ROUTINE] Selesai secara berurutan.\n")

    def log_to_cmd(self, action_text):
        now = time.time()
        if now - self.last_cmd_log_time > 0.35: 
            afk_status = "ON" if self.afk_mode_enabled else "OFF"
            quit_status = "ON" if self.auto_quit_enabled else "OFF"
            sys.stdout.write(f"\r[DEBUG] State: {self.state:<15} | Action: {action_text:<45} | AFK: {afk_status} | Auto-Quit: {quit_status}")
            sys.stdout.flush()
            self.last_cmd_log_time = now

    def print_banner(self):
        print("========================================")
        print("      FISHING PIXEL BOT - VERSION 4.2   ")
        print("   Logic: Top-End Brake & Config Loaded ")
        print("========================================")
        print(f"[CONFIG] Monitor : {self.screen_w}x{self.screen_h} (DPI Fixed)")
        print(f"[CONFIG] DXCam   : {self.target_fps} FPS | Stall Limit: {self.config_stall_frames} Frm")
        print(f"[CONFIG] Max Grn : {self.MAX_GREEN} | Sukses: >{self.SUCCESS_THRESHOLD}")
        print(f"[CONFIG] Timeout : {self.timeout_sec} Detik (Berlapis Limit 6x)")
        print(f"[CONFIG] Cast Dly: {self.cast_delay} Detik")
        print("========================================")
        print("[8] - Toggle Live Text Debug Mode (CMD)")
        print("[9] - Exit Program")
        print("[7] - TOGGLE AUTO-EAT/AFK MODE")
        print("[6] - TOGGLE AUTO-QUIT GAME (PRO)")
        print("[3] - MANUALLY START FISHING")
        print("[X] - PANIC BUTTON (Instant Interrupt)")
        print("========================================")

    def run(self):
        self.print_banner()
        try:
            while True:
                if self.io.is_key_pressed(0x39): break 
                
                if self.io.is_key_pressed(0x38): 
                    if not self.debug_key_pressed:
                        self.is_debug_mode = not self.is_debug_mode
                        status = "DIPERLIHATKAN" if self.is_debug_mode else "DISEMBUNYIKAN"
                        print(f"\n[*] DEBUG TEXT DI CMD: {status}")
                        self.debug_key_pressed = True
                else:
                    self.debug_key_pressed = False

                if self.io.is_key_pressed(0x37): 
                    if not self.afk_key_pressed:
                        self.afk_mode_enabled = not self.afk_mode_enabled
                        status = "ON" if self.afk_mode_enabled else "OFF"
                        print(f"\n[!] AUTO-EAT / AFK MODE: {status}")
                        self.afk_key_pressed = True
                else:
                    self.afk_key_pressed = False

                if self.io.is_key_pressed(0x36): 
                    if not self.auto_quit_key_pressed:
                        self.auto_quit_enabled = not self.auto_quit_enabled
                        status = "ON (Kritis -> F8 Quit -> Exit)" if self.auto_quit_enabled else "OFF (Kritis -> Standby)"
                        print(f"\n[⚠️] FEATURE ATTACHED: AUTO-QUIT GAME IS {status}")
                        self.auto_quit_key_pressed = True
                else:
                    self.auto_quit_key_pressed = False

                if self.io.is_key_pressed(0x58): 
                    if self.state != "FASE_0_STANDBY":
                        print("\n[🚨] PANIC INTERRUPT! Kembali ke Standby...")
                        self.io.safe_mouse_up() 
                        self.state = "FASE_0_STANDBY"
                        self.reset_minigame_state()
                        self.timeout_strike_counter = 0
                        time.sleep(0.5) 
                        continue 

                frame = self.camera.get_latest_frame()
                if frame is None: continue
                action_text = "IDLE"

                try:
                    if self.state == "FASE_0_STANDBY":
                        action_text = "Menunggu pemicu tombol '3'..."
                        if self.io.is_key_pressed(0x33):
                            print("\n>>> Memulai siklus pemantauan...")
                            self.state = "FASE_1_WAITING"
                            self.fase1_start_time = time.time() 
                            self.timeout_strike_counter = 0
                            time.sleep(1.0) 

                    elif self.state == "FASE_1_WAITING":
                        if time.time() - self.fase1_start_time > self.timeout_sec: 
                            self.timeout_strike_counter += 1 
                            print(f"\n[⚠️] TIMEOUT Terdeteksi! Beruntun ke-{self.timeout_strike_counter}")
                            
                            if self.timeout_strike_counter == 1:
                                print("    -> Aksi: Mencoba tekan '3' untuk melempar ulang biasa...")
                                self.io.tap_key_scancode(0x04) 
                                self.fase1_start_time = time.time()
                                time.sleep(1.5)
                                continue
                                
                            elif self.timeout_strike_counter == 2:
                                print("    -> Aksi: Menganggap UI Error. Menjalankan FIXUI Ke-1 via F8...")
                                self.execute_fixui_recovery() 
                                print("    -> Memulai lempar kembali pasca-fixui...")
                                self.io.tap_key_scancode(0x04) 
                                self.fase1_start_time = time.time()
                                time.sleep(1.5)
                                continue
                                
                            elif self.timeout_strike_counter == 3:
                                print("    -> Aksi: Tetap tidak ada UI. Mencoba tekan '3' lagi untuk memastikan...")
                                self.io.tap_key_scancode(0x04) 
                                self.fase1_start_time = time.time()
                                time.sleep(1.5)
                                continue
                                
                            elif self.timeout_strike_counter == 4:
                                print("    -> Aksi: Masih tidak terlihat. Menjalankan FIXUI Ke-2 via F8...")
                                self.execute_fixui_recovery() 
                                print("    -> Memulai lempar kembali pasca-fixui Ke-2...")
                                self.io.tap_key_scancode(0x04) 
                                self.fase1_start_time = time.time()
                                time.sleep(1.5)
                                continue
                                
                            elif self.timeout_strike_counter == 5:
                                print("    -> Aksi: Pasca-fixui 2 tetap zonk. Tekan '3' untuk percobaan terakhir...")
                                self.io.tap_key_scancode(0x04) 
                                self.fase1_start_time = time.time()
                                time.sleep(1.5)
                                continue

                            elif self.timeout_strike_counter >= 6:
                                if self.auto_quit_enabled:
                                    self.execute_force_quit_game()
                                else:
                                    print("\n[🚨] KONDISI KRITIS: Sudah menjalankan FixUI 2x dan 2x Timeout beruntun setelahnya!")
                                    print("[🔒] Kembali ke MODE STANDBY...\n")
                                    self.io.safe_mouse_up()
                                    self.state = "FASE_0_STANDBY"
                                    self.reset_minigame_state()
                                    self.timeout_strike_counter = 0 
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
                                    action_text = "TARGET DETECTED! HOOKING..."
                                    self.io.single_click_instant()
                                    time.sleep(0.2) 
                                    self.io.safe_mouse_up() 
                                    
                                    self.timeout_strike_counter = 0 
                                    self.reset_minigame_state()
                                    self.state = "FASE_3_MINIGAME"
                                    self.phase3_start_time = time.time() 
                                    self.last_seen_time = time.time() 
                                else:
                                    action_text = f"NOISE REJECTED (W:{w} H:{h})"

                    elif self.state == "FASE_3_MINIGAME":
                        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                        mask_grad = cv2.inRange(hsv_frame, self.lower_grad, self.upper_grad)
                        mask_white = cv2.inRange(hsv_frame, self.lower_white, self.upper_white)
                        
                        contours_g, _ = cv2.findContours(mask_grad, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        contours_w, _ = cv2.findContours(mask_white, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        
                        valid_bar_found = False
                        grad_h, white_h = 0, 0
                        rescue_mode = False
                        white_rescue_mode = False

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
                                        white_h = h_tmp
                                        valid_bar_found = True  
                                        self.bar_ever_found = True 
                                        self.last_seen_time = time.time()
                                        if white_h > self.max_white_h: self.max_white_h = white_h
                                        break 

                        green_found_this_frame = False
                        if valid_bar_found and contours_g:
                            contours_g = sorted(contours_g, key=cv2.contourArea, reverse=True)
                            for cg in contours_g:
                                if cv2.contourArea(cg) >= 2: 
                                    xg, yg, wg, hg = cv2.boundingRect(cg)
                                    grad_h = hg
                                    green_found_this_frame = True
                                    if grad_h > self.max_grad_h: 
                                        self.max_grad_h = grad_h
                                    break

                        if valid_bar_found and not green_found_this_frame:
                            if self.prev_grad_h > 0:
                                grad_h = self.prev_grad_h 
                            else:
                                self.is_cooling_down = True

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
                                current_swing = int(80 * self.scale_y) 
                                BAND_HIGH = max(BAND_HIGH, int(80 * self.scale_y)) 
                            elif white_h < int(100 * self.scale_y):
                                current_swing = int(100 * self.scale_y) 
                                BAND_HIGH = max(BAND_HIGH, int(100 * self.scale_y))
                            elif white_h > (self.SUCCESS_THRESHOLD - int(40 * self.scale_y)):
                                current_swing = int(50 * self.scale_y) 
                            else:
                                current_swing = self.MIN_SWING

                            if white_h < self.TIGHT_GRIP_THRESHOLD:
                                current_swing = min(current_swing, self.TIGHT_GRIP_SWING) 

                            BAND_LOW = BAND_HIGH - current_swing
                            
                            if white_h > (self.SUCCESS_THRESHOLD - int(40 * self.scale_y)):
                                BAND_LOW = max(BAND_LOW, -int(170 * self.scale_y)) 
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
                                if selisih <= effective_band_low: self.is_cooling_down = False
                            else:
                                if selisih >= effective_band_high: self.is_cooling_down = True

                            # Rescue Bawah
                            if 0 < white_h < int(35 * self.scale_y):
                                if grad_h < (self.MAX_GREEN - int(25 * self.scale_y)):
                                    self.is_cooling_down = False
                                    white_rescue_mode = True
                                    self.hold_stall_counter = 0

                            # Rescue Atas
                            GREEN_RESCUE_ENTER = self.MAX_GREEN - int(5  * self.scale_y)
                            GREEN_RESCUE_EXIT  = self.MAX_GREEN - int(135 * self.scale_y) 
                            
                            if grad_h >= GREEN_RESCUE_ENTER: self.in_rescue_mode = True
                            elif grad_h <= GREEN_RESCUE_EXIT: self.in_rescue_mode = False

                            if self.in_rescue_mode:
                                self.is_cooling_down = True
                                rescue_mode = True
                                white_rescue_mode = False
                                self.hold_stall_counter = 0

                            # TOP-END CRITICAL BRAKE SYSTEM 
                            if white_h >= int(370 * self.scale_y):
                                if selisih >= int(5 * self.scale_y) or grad_h >= int(350 * self.scale_y):
                                    self.is_cooling_down = True
                                    rescue_mode = True

                            # --- [KUNCI BARU] SMART STALL DETECTION BERBASIS CONFIG ---
                            if not self.is_cooling_down and not white_rescue_mode:
                                if self.delta_selisih <= 1 and delta_white <= 1: 
                                    self.hold_stall_counter += 1
                                else: 
                                    self.hold_stall_counter = 0
                                    
                                # Menggunakan nilai dinamis self.config_stall_frames dari config.ini
                                if self.hold_stall_counter >= self.config_stall_frames:
                                    self.is_cooling_down = True
                                    self.hold_stall_counter = 0
                            else:
                                self.hold_stall_counter = 0

                            if self.is_cooling_down:
                                self.io.safe_mouse_up()
                                action_text = "RELEASE KEY" if not rescue_mode else "RESCUE RELEASE PAKSA"
                            else:
                                self.io.safe_mouse_down()
                                action_text = "HOLD KEY" if not white_rescue_mode else "RESCUE HOLD PAKSA"

                        if not valid_bar_found:
                            time_lost = time.time() - self.last_seen_time
                            time_in_phase3 = time.time() - self.phase3_start_time
                            
                            if time_in_phase3 < 2.0 and self.max_white_h < int(10 * self.scale_y):
                                self.io.safe_mouse_down()
                                action_text = "INITIAL PULL..."
                            elif self.bar_ever_found and time_lost < 0.6:
                                self.io.safe_mouse_up() 
                                self.is_cooling_down = True 
                                action_text = "FLICKER RECOVERY..."
                            else:
                                self.io.safe_mouse_up()
                                print(f"\n>>> UI Hilang.")
                                print(f"    HASIL: Max White: {self.max_white_h}px | Max Green: {self.max_grad_h}px | Target: >{self.SUCCESS_THRESHOLD}px")
                                
                                if self.max_white_h >= self.SUCCESS_THRESHOLD: 
                                    print(f"    STATUS: SUKSES\n")
                                    self.perform_auto_collect()
                                    
                                    if self.afk_mode_enabled and (time.time() - self.last_afk_time) >= (self.afk_interval * 60):
                                        print(f">>> Memberikan jeda aman sebelum rutinitas AFK...")
                                        if self.interruptible_sleep(self.cast_delay): continue
                                        self.perform_afk_routine()
                                        self.last_afk_time = time.time()
                                else:
                                    print(f"    STATUS: GAGAL / PUTUS\n")
                                    
                                print(f">>> Siklus Selesai. Melempar pancingan baru dalam {self.cast_delay} detik...")
                                if self.interruptible_sleep(self.cast_delay): continue 
                                    
                                self.io.tap_key_scancode(0x04) 
                                self.state = "FASE_1_WAITING" 
                                self.reset_minigame_state()
                                self.fase1_start_time = time.time() 
                                if self.interruptible_sleep(1.0): continue

                except Exception as inner_e:
                    pass

                if self.is_debug_mode:
                    self.log_to_cmd(action_text)

        except KeyboardInterrupt:
            print("\n[!] Dihentikan secara paksa oleh user (Ctrl + C). Membersihkan resource...")
        except Exception as e:
            print(f"\n[!] Fatal Error: {e}")
        finally:
            self.io.safe_mouse_up()
            self.camera.stop()
            os._exit(0)

if __name__ == "__main__":
    bot = FishingBot()
    bot.run()
