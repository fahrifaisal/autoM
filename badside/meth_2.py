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

class MacroController:
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
        time.sleep(hold_time)
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

    def smooth_move_curve(self, target_x, target_y, steps=30, duration=0.20):
        start_x, start_y = self.get_cursor_pos()
        dx = target_x - start_x
        dy = target_y - start_y
        if dx == 0 and dy == 0: return
        
        sleep_time = duration / steps
        for i in range(1, steps + 1):
            t = i / steps
            smooth_t = t * t * (3 - 2 * t)
            curr_x = int(start_x + (dx * smooth_t))
            curr_y = int(start_y + (dy * smooth_t))
            ctypes.windll.user32.SetCursorPos(curr_x, curr_y)
            time.sleep(sleep_time)


# ==============================================================================
# 3. LOOPS PRODUCTION ENGINE FOR PHASE 2 (THE ULTIMATE HYBRID STABLE CORE)
# ==============================================================================
class MethPhase2Engine:
    def __init__(self):
        self.ctrl = MacroController()
        self.is_running = False
        self.loop_counter = 0
        
        self.camera = dxcam.create(output_color="BGR")
        
        # --- ROI PRECISI TABLE ---
        self.roi_left_table = (345, 640, 820, 900)
        
        # --- RANGE MULTI-COLOR TARGET (TANPA COKELAT MEJA) ---
        # 1. Orange Stiker (Konversi Emas Web Picker)
        self.lower_orange = np.array([10, 120, 100])
        self.upper_orange = np.array([22, 255, 220])
        
        # 2. Biru Stiker (Penembus Kamuflase Meja)
        self.lower_blue = np.array([95, 130, 80])
        self.upper_blue = np.array([112, 255, 180])
        
        # 3. Tutup Putih (Jangkar Pembantu Segala Posisi)
        self.lower_white = np.array([0, 0, 140])
        self.upper_white = np.array([180, 60, 255])

    def check_interrupt(self):
        if self.ctrl.is_key_pressed(0x30): 
            print("\n[🚨] PANIC STOP! Menghentikan alur kerja Fase 2...")
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

    def scan_and_click_bottles(self):
        """Memindai 10 botol (Orange & Biru) dengan mempertahankan mekanisme evakuasi kursor instan dari area tumpukan"""
        print("    -> [STEP 2] Menyapu Stiker Orange & Biru + Evakuasi Kursor Aktif...")
        self.camera.start(target_fps=60, region=self.roi_left_table)
        
        last_bottle_seen_time = time.time()
        BOTTLE_CLEAR_TIMEOUT = 1.5 
        total_clicked = 0
        
        clicked_blacklist = [] # List tuple: (target_x, target_y, timestamp)
        
        while True:
            if self.check_interrupt(): break
            
            frame = self.camera.get_latest_frame()
            if frame is None: continue
            
            blurred = cv2.GaussianBlur(frame, (3, 3), 0)
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
            
            # --- GENERATE MASKING STIKER MURNI ---
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
                        
                        # FILTER ANTI DOUBLE-CLICK
                        sudah_klik = False
                        for bx, by, t in clicked_blacklist:
                            if abs(target_x - bx) < 15 and abs(target_y - by) < 15:
                                sudah_klik = True
                                break
                        if sudah_klik: 
                            continue
                        
                        print(f"    [🎯] Stiker Terkunci -> ({target_x}, {target_y}) | Luas: {area:.0f}px")
                        self.ctrl.smooth_move_curve(target_x, target_y, steps=6, duration=0.06)
                        self.ctrl.click_instant(hold_time=0.04)
                        
                        total_clicked += 1
                        clicked_blacklist.append((target_x, target_y, time.time()))
                        last_bottle_seen_time = time.time() 
                        botol_diklik_di_frame_ini = True
                        
                        # --- ⚡ MEKANISME EVAKUASI INSTAN TETAP DIJAGA ⚡ ---
                        # Melempar kursor 500 piksel ke atas agar area tumpukan botol langsung bersih di frame selanjutnya
                        evac_y = max(self.roi_left_table[1], target_y - 200)
                        ctypes.windll.user32.SetCursorPos(target_x, evac_y)
                        
                        time.sleep(0.12)
                        break 
            
            if botol_diklik_di_frame_ini:
                continue
            
            # --- EVALUASI MEJA BERSIH ---
            if time.time() - last_bottle_seen_time > BOTTLE_CLEAR_TIMEOUT:
                print(f"    [📢] Meja kiri bersih sempurna! Total {total_clicked} botol stiker berhasil disapu.")
                break
                
            time.sleep(0.01)
            
        self.camera.stop()

    def execute_hammer_swings(self):
        """STEP 4: Pengambilan palu kanan dan eksekusi 3x hantaman vertikal murni"""
        print("    -> [STEP 4] Mengambil palu di meja kanan (1240, 737)...")
        self.ctrl.smooth_move_curve(1240, 737, steps=15, duration=0.15)
        self.ctrl.mouse_down() 
        if self.smart_sleep(0.12): return
        
        print("    -> Menyeret palu ke posisi jangkar atas (940, 500)...")
        self.ctrl.smooth_move_curve(940, 500, steps=25, duration=0.25)
        if self.smart_sleep(0.15): return

        print("    -> Mengeksekusi 3x rangkaian ayunan hantaman palu...")
        for i in range(3):
            if self.check_interrupt(): return
            
            print(f"       Ayunan {i+1}: Meluncur Hantam BAWAH -> (940, 780)")
            self.ctrl.smooth_move_curve(940, 780, steps=10, duration=0.3)
            if self.smart_sleep(0.06): return
            
            print(f"       Ayunan {i+1}: Mengangkat ke ATAS -> (940, 500)")
            self.ctrl.smooth_move_curve(940, 500, steps=10, duration=0.3)
            if self.smart_sleep(0.06): return
            
        self.ctrl.mouse_up() 
        print("    -> Tahap pemukulan selesai. Minigame berakhir secara otomatis.")

    def run_production_cycle(self):
        """Satu rantai siklus produksi penuh Fase 2"""
        print(f"\n[🔄] Menjalankan Siklus Produksi Fase 2 Ke-{self.loop_counter + 1}...")
        
        # ----------------------------------------------------------------------
        # STEP 1: MEMBUKA MENU RADIAL
        # ----------------------------------------------------------------------
        if self.smart_sleep(0.60): return
        self.ctrl.key_down(0x38) 
        if self.smart_sleep(0.74): return
        
        self.ctrl.mouse_down()
        if self.smart_sleep(0.11): return
        self.ctrl.mouse_up()
        
        self.ctrl.smooth_move_curve(817, 471, steps=15, duration=0.15)
        self.ctrl.click_instant(hold_time=0.122)
        if self.smart_sleep(0.48): return
        self.ctrl.key_up(0x38) 
        
        if self.smart_sleep(1.2): return

        # ----------------------------------------------------------------------
        # STEP 2: SCAN & AUTOMATICALLY CLICK ALL DETECTED BOTTLES
        # ----------------------------------------------------------------------
        self.scan_and_click_bottles()
        if self.check_interrupt(): return

        # ----------------------------------------------------------------------
        # STEP 3: OVEN WAIT PROCESS (15 DETIK)
        # ----------------------------------------------------------------------
        print("    -> [STEP 3] Menunggu proses pematangan Oven selama 15 detik...")
        if self.smart_sleep(13.00): return

        # ----------------------------------------------------------------------
        # STEP 4: GRAB HAMMER & SWING 3 TIMES
        # ----------------------------------------------------------------------
        self.execute_hammer_swings()
        
        self.loop_counter += 1
        print(f"[✅] SIKLUS FASE 2 KE-{self.loop_counter} SELESAI. MERESET ALUR...")
        
        print("    -> Menunggu transisi 6 detik untuk perulangan berikutnya...")
        if self.smart_sleep(1.00): return

    def start_engine(self):
        print("==================================================")
        print("        METH AUTOMATION PHASE 2 ENGINE V3.2       ")
        print("     The Ultimate Hybrid Stable Core (Anti-Wood)  ")
        print("==================================================")
        print(" [9] - MULAI EKSEKUSI PENGULANGAN (INFINITE)      ")
        print(" [0] - HALT ENGINE & RESET KE MODE STANDBY         ")
        print("==================================================")
        print("Status: STANDBY (Menunggu perintah input '9'...)\n")

        try:
            while True:
                time.sleep(0.1)
                if self.ctrl.is_key_pressed(0x39): 
                    if not self.is_running:
                        print("\n[🟢] ENGINE PHASE 2 ACTIVE: Menjalankan...")
                        self.is_running = True
                        
                        while self.is_running:
                            self.run_production_cycle()
                            time.sleep(0.5)
                            if self.check_interrupt():
                                break

                        print("\n[🔒] Engine Dimatikan. Kembali ke Mode Standby...")
                        print("Tekan '9' jika ingin menjalankan kembali.\n")

        except KeyboardInterrupt:
            sys.exit(0)

if __name__ == "__main__":
    engine = MethPhase2Engine()
    engine.start_engine()