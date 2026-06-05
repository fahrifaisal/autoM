import sys
import ctypes
import time
import random
import numpy as np
import dxcam
import cv2

# ==============================================================================
# 1. DPI AWARENESS FIX
# ==============================================================================
if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

# ==============================================================================
# 2. HIGH-PRECISION INPUT ENGINE (Win32 API)
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

class WinNativeDispatcher:
    def __init__(self):
        self.mouse_pressed = False
        self.held_keys = set()

    def is_key_pressed(self, vk_code):
        return (ctypes.windll.user32.GetAsyncKeyState(vk_code) & 0x8000) != 0

    def get_cursor_pos(self):
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        pt = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.pointer(pt))
        return pt.x, pt.y

    def mouse_down(self):
        if not self.mouse_pressed:
            extra = ctypes.c_ulong(0)
            ii_ = Input_I()
            ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, ctypes.pointer(extra))
            x = Input(ctypes.c_ulong(INPUT_MOUSE), ii_)
            ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
            self.mouse_pressed = True

    def mouse_up(self):
        if self.mouse_pressed:
            extra = ctypes.c_ulong(0)
            ii_ = Input_I()
            ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_LEFTUP, 0, ctypes.pointer(extra))
            x = Input(ctypes.c_ulong(INPUT_MOUSE), ii_)
            ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
            self.mouse_pressed = False

    def click_instant(self, hold_time=0.10):
        self.mouse_down()
        time.sleep(hold_time + random.uniform(-0.003, 0.005))
        self.mouse_up()

    def key_down(self, scancode):
        if scancode not in self.held_keys:
            extra = ctypes.c_ulong(0)
            ii_ = Input_I()
            ii_.ki = KeyBdInput(0, scancode, KEYEVENTF_SCANCODE, 0, ctypes.pointer(extra))
            x = Input(ctypes.c_ulong(INPUT_KEYBOARD), ii_)
            ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
            self.held_keys.add(scancode)

    def key_up(self, scancode):
        if scancode in self.held_keys:
            extra = ctypes.c_ulong(0)
            ii_ = Input_I()
            ii_.ki = KeyBdInput(0, scancode, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP, 0, ctypes.pointer(extra))
            x = Input(ctypes.c_ulong(INPUT_KEYBOARD), ii_)
            ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
            self.held_keys.remove(scancode)

    def interpolate_vector_stream(self, raw_target_x, raw_target_y, steps=20, base_duration=0.18):
        """Mekanisme Pergerakan Mouse Gaussian Curve Adaptif Cepat dengan Micro-Jitter Spasial"""
        # Suntikkan acakan koordinat tipis-tipis (-2 s.d 2 piksel) untuk mengelabui deteksi statis
        target_x = raw_target_x + random.randint(-2, 2)
        target_y = raw_target_y + random.randint(-2, 2)
        
        start_x, start_y = self.get_cursor_pos()
        dx = target_x - start_x
        dy = target_y - start_y
        if dx == 0 and dy == 0: return
        
        fuzzed_steps = steps + random.randint(-2, 3)
        fuzzed_duration = base_duration + random.uniform(-0.015, 0.025)
        sleep_time = fuzzed_duration / fuzzed_steps
        
        for i in range(1, fuzzed_steps + 1):
            t = i / fuzzed_steps
            smooth_t = t * t * (3 - 2 * t)
            
            curr_x = start_x + (dx * smooth_t)
            curr_y = start_y + (dy * smooth_t)
            
            # Efek tremor motorik tangan biologis yang meredup linier mendekati target akhir
            damping_factor = (1.0 - t) * 1.6
            jitter_x = np.random.normal(0, damping_factor) if damping_factor > 0 else 0
            jitter_y = np.random.normal(0, damping_factor) if damping_factor > 0 else 0
            
            ctypes.windll.user32.SetCursorPos(int(curr_x + jitter_x), int(curr_y + jitter_y))
            time.sleep(sleep_time)


# ==============================================================================
# 3. LOOPS PRODUCTION ENGINE FOR PHASE 2 (THE ULTIMATE HYBRID STABLE CORE)
# ==============================================================================
class HostDiagnosticMonitor:
    def __init__(self):
        self.ctrl = WinNativeDispatcher()
        self.is_running = False
        self.loop_counter = 0
        
        # Inisialisasi Ring Buffer sirkular diperluas untuk mengamankan data stream OpenCV
        self.camera = dxcam.create(output_color="BGR", max_buffer_len=8)
        self.roi_left_table = (345, 640, 820, 900)
        
        self.lower_orange = np.array([10, 120, 100])
        self.upper_orange = np.array([22, 255, 220])
        self.lower_blue = np.array([95, 130, 80])
        self.upper_blue = np.array([112, 255, 180])
        self.lower_white = np.array([0, 0, 140])
        self.upper_white = np.array([180, 60, 255])

    def check_interrupt(self):
        if self.ctrl.is_key_pressed(0x30): # Tombol '0' Panic Stop
            print("\n[🚨] SYSTEM INTERRUPT: Resetting task queues to Standby context...")
            self.ctrl.mouse_up()
            self.ctrl.key_up(0x38)
            self.is_running = False
            return True
        return False

    def smart_sleep(self, duration):
        start = time.time()
        while time.time() - start < duration:
            if self.check_interrupt():
                return True
            time.sleep(0.03)
        return False

    def analyze_surface_contours(self):
        """Memindai kontur warna stiker botol secara asinkron dengan penanganan evakuasi kursor cepat"""
        print("    -> [STAGE 2] Committing contour matrix scan for target surface elements...")
        self.camera.start(target_fps=60, region=self.roi_left_table)
        
        last_bottle_seen_time = time.time()
        BOTTLE_CLEAR_TIMEOUT = 1.5 
        total_clicked = 0
        clicked_blacklist = [] 
        
        while True:
            if self.check_interrupt(): break
            
            frame = self.camera.get_latest_frame()
            if frame is None: continue
            
            blurred = cv2.GaussianBlur(frame, (3, 3), 0)
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
            
            mask_o = cv2.inRange(hsv, self.lower_orange, self.upper_orange)
            mask_bl = cv2.inRange(hsv, self.lower_blue, self.upper_blue)
            mask_master = cv2.bitwise_or(mask_o, mask_bl)
            
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 5))
            mask_cleaned = cv2.morphologyEx(mask_master, cv2.MORPH_CLOSE, kernel)
            contours, _ = cv2.findContours(mask_cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            now = time.time()
            clicked_blacklist = [b for b in clicked_blacklist if now - b[2] < 1.3]
            botol_diklik_di_frame_ini = False
            
            if contours:
                contours = sorted(contours, key=cv2.contourArea, reverse=True)
                
                for c in contours:
                    area = cv2.contourArea(c)
                    if 20 < area < 4000:
                        x_local, y_local, w, h = cv2.boundingRect(c)
                        
                        target_x = self.roi_left_table[0] + x_local + (w // 2)
                        target_y = self.roi_left_table[1] + y_local + (h // 2)
                        
                        sudah_klik = False
                        for bx, by, t in clicked_blacklist:
                            if abs(target_x - bx) < 15 and abs(target_y - by) < 15:
                                sudah_klik = True
                                break
                        if sudah_klik: 
                            continue
                        
                        print(f"    [🎯] Target Lock Acquired -> ({target_x}, {target_y}) | Extent: {area:.0f}px")
                        # Transisi cepat meluncur menuju botol menggunakan interpolasi teracak mikro
                        self.ctrl.interpolate_vector_stream(target_x, target_y, steps=5, base_duration=0.05)
                        self.ctrl.click_instant(hold_time=0.04)
                        
                        total_clicked += 1
                        clicked_blacklist.append((target_x, target_y, time.time()))
                        last_bottle_seen_time = time.time() 
                        botol_diklik_di_frame_ini = True
                        
                        # --- MEKANISME EVAKUASI KURSOR CEPAT ---
                        evac_y = max(self.roi_left_table[1], target_y - 200)
                        ctypes.windll.user32.SetCursorPos(target_x, evac_y)
                        
                        time.sleep(0.12)
                        break 
            
            if botol_diklik_di_frame_ini:
                continue
            
            if time.time() - last_bottle_seen_time > BOTTLE_CLEAR_TIMEOUT:
                print(f"    [📢] Surface cleared successfully. Total {total_clicked} targets processed.")
                break
                
            time.sleep(0.01)
            
        self.camera.stop()

    def dispatch_axis_pulses(self):
        """STEP 4: Rangkaian pemukulan objek vertikal murni dengan penyesuaian fuzzed delay"""
        print("    -> [STAGE 4] Intercepting secondary physical tool at matrix (1240, 737)...")
        self.ctrl.interpolate_vector_stream(1240, 737, steps=12, base_duration=0.12)
        self.ctrl.mouse_down() 
        if self.smart_sleep(0.12): return
        
        print("    -> Dragging tool to central anchor node (940, 500)...")
        self.ctrl.interpolate_vector_stream(940, 500, steps=20, base_duration=0.20)
        if self.smart_sleep(0.15): return

        print("    -> Dispatching sequential physical pulses to target matrix...")
        for i in range(3):
            if self.check_interrupt(): return
            
            print(f"       Pulse {i+1}: Accelerating downward vector -> (940, 780)")
            self.ctrl.interpolate_vector_stream(940, 780, steps=8, base_duration=0.22)
            if self.smart_sleep(0.06 + random.uniform(-0.005, 0.01)): return
            
            print(f"       Pulse {i+1}: Pulling upward vector -> (940, 500)")
            self.ctrl.interpolate_vector_stream(940, 500, steps=8, base_duration=0.22)
            if self.smart_sleep(0.06 + random.uniform(-0.005, 0.01)): return
            
        self.ctrl.mouse_up() 
        print("    -> Pulse sequence finished. Context closing autonomously.")

    def execute_subsystem_routine(self):
        """Satu rantai siklus produksi penuh Fase 2"""
        print(f"\n[🔄] Processing production sequence iteration -> {self.loop_counter + 1}...")
        
        # ----------------------------------------------------------------------
        # STEP 1: MEMBUKA MENU RADIAL
        # ----------------------------------------------------------------------
        if self.smart_sleep(0.60 + random.uniform(-0.02, 0.03)): return
        self.ctrl.key_down(0x38) 
        if self.smart_sleep(0.74 + random.uniform(-0.01, 0.04)): return
        
        self.ctrl.mouse_down()
        if self.smart_sleep(0.11): return
        self.ctrl.mouse_up()
        
        self.ctrl.interpolate_vector_stream(817, 471, steps=12, base_duration=0.12)
        self.ctrl.click_instant(hold_time=0.122)
        if self.smart_sleep(0.48): return
        self.ctrl.key_up(0x38) 
        
        if self.smart_sleep(1.2): return

        # ----------------------------------------------------------------------
        # STEP 2: SCAN & AUTOMATICALLY CLICK ALL DETECTED BOTTLES
        # ----------------------------------------------------------------------
        self.analyze_surface_contours()
        if self.check_interrupt(): return

        # ----------------------------------------------------------------------
        # STEP 3: OVEN WAIT PROCESS (15 DETIK)
        # ----------------------------------------------------------------------
        print("    -> [STAGE 3] Holding core pipeline for oven crystallization (15 seconds)...")
        if self.smart_sleep(13.00 + random.uniform(0.05, 0.25)): return

        # ----------------------------------------------------------------------
        # STEP 4: GRAB HAMMER & SWING 3 TIMES
        # ----------------------------------------------------------------------
        self.dispatch_axis_pulses()
        
        self.loop_counter += 1
        print(f"[✅] ALL SUB-ROUTINES FOR CYCLE {self.loop_counter} COMMITTED SUCCESSFULLY.")
        
        print("    -> Awaiting cooldown gate transition (6 seconds)...")
        if self.smart_sleep(1.00 + random.uniform(0.02, 0.08)): return

    def start_engine(self):
        print("==================================================")
        print("        CORE SUBSYSTEM TASK ALLOCATOR V3.2        ")
        print("       Win32 Kernel SendInput Infrastructure       ")
        print("==================================================")
        print(" [9] - ALLOCATE SUB-ROUTINE STREAM PIPELINE       ")
        print(" [0] - HALT ACTIVE CONTEXTS & RESET STANDBY       ")
        print("==================================================")
        print("Status: SERVICE_STANDBY (Awaiting opcode signal '9'...)\n")

        try:
            while True:
                time.sleep(0.1)
                if self.ctrl.is_key_pressed(0x39): 
                    if not self.is_running:
                        print("\n[🟢] SERVICE_ACTIVE: Spawning task allocation routines...")
                        self.is_running = True
                        
                        while self.is_running:
                            self.execute_subsystem_routine()
                            time.sleep(0.5)
                            if self.check_interrupt():
                                break

                        print("\n[🔒] SERVICE_SUSPENDED: Task queues rolled back to standby state.")
                        print("Awaiting opcode signal '9' to initialize pipeline context.\n")

        except KeyboardInterrupt:
            sys.exit(0)

if __name__ == "__main__":
    engine = HostDiagnosticMonitor()
    engine.start_engine()
