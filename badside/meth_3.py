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

    def smooth_move_curve(self, target_x, target_y, steps=35, duration=0.25):
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
# 3. LOOPS PRODUCTION ENGINE FOR PHASE 3 (FIXED CLASS STRUCTURE)
# ==============================================================================
class MethPhase3Engine:
    def __init__(self):
        self.ctrl = MacroController()
        self.is_running = False
        self.loop_counter = 0
        
        self.camera = dxcam.create(output_color="BGR")
        self.roi_left_table = (250, 350, 850, 650)
        
        self.drop_target_x = 960
        self.drop_target_y = 365
        
        # Pengetatan range HSV dasar untuk menyaring transisi tembok abu-abu redup
        self.lower_gray_strict = np.array([12, 10, 105])
        self.upper_gray_strict = np.array([25, 50, 185])

    def check_interrupt(self):
        if self.ctrl.is_key_pressed(0x30): 
            print("\n[🚨] PANIC STOP! Menghentikan alur kerja Fase 3...")
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

    def scan_and_drag_materials(self, target_count=10):
        """Memindai bahan abu-abu dengan pelindung geometri absolut untuk memisahkan tumpukan dempet raksasa"""
        print(f"    -> [STEP 2] Menyapu Bahan Abu-abu (Absolute Twin-Shield Core Active)...")
        self.camera.start(target_fps=60, region=self.roi_left_table)
        
        last_material_seen_time = time.time()
        MATERIAL_CLEAR_TIMEOUT = 1.6 # Dinaikkan sedikit ke 1.6s agar memberikan napas transisi saat pemisahan objek
        success_drag_count = 0
        
        lower_gray_strict = np.array([12, 10, 105])
        upper_gray_strict = np.array([25, 50, 185])
        
        while success_drag_count < target_count:
            if self.check_interrupt(): break
            
            frame = self.camera.get_latest_frame()
            if frame is None: continue
            
            blurred = cv2.GaussianBlur(frame, (3, 3), 0)
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
            
            mask = cv2.inRange(hsv, lower_gray_strict, upper_gray_strict)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            mask_cleaned = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            contours, _ = cv2.findContours(mask_cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            bahan_ditemukan_di_frame_ini = False
            
            if contours:
                valid_materials = []
                
                for c in contours:
                    area = cv2.contourArea(c)
                    
                    # --- [KOREKSI LUAS] DILEBARKAN HINGGA 1200PX ---
                    # Menjamin dua bahan besar (~250px + ~250px) yang menyatu tidak akan terbuang
                    if 10 < area < 1200:
                        x_local, y_local, w, h = cv2.boundingRect(c)
                        
                        # --- [KOREKSI DIMENSI] KHUSUS GEOMETRI DEMPET RAQPAT ---
                        # Lebar (w) dilonggarkan hingga 90px karena dua bahan dempet mendatar pasti melebar.
                        # Tinggi (h) tetap dikunci ketat di 42px agar potongan tembok abu-abu vertikal tetap terblokir!
                        if w > 90 or h > 42:
                            continue
                            
                        # Batas atas aspek rasio dinaikkan ke 2.85 untuk menangkap kelonjongan dua objek dempet
                        aspect_ratio = float(w) / h
                        if not (0.60 <= aspect_ratio <= 2.85):
                            continue
                        
                        valid_materials.append((c, area, w, h, x_local, y_local))
                
                if valid_materials:
                    valid_materials = sorted(valid_materials, key=lambda x: x[1], reverse=True)
                    best_contour, area, w, h, x_local, y_local = valid_materials[0]
                    
                    # Tentukan koordinat tengah default
                    target_x = self.roi_left_table[0] + x_local + (w // 2)
                    target_y = self.roi_left_table[1] + y_local + (h // 2)
                    
                    # --- ⚡ TWIN-SPLITTER ADAPTIF SKALA BESAR ⚡ ---
                    # Jika area gabungan terdeteksi masif (> 340px) ATAU w memanjang (> 26px)
                    if area > 340 or w > 26:
                        print(f"    [⚠️] Target Dempet Terkunci (Luas: {area:.0f}px, Lebar: {w}px) -> Memotong Sisi Kiri...")
                        # Paksa ambil koordinat 25% dari sisi kiri kontur gabungan
                        target_x = self.roi_left_table[0] + x_local + int(w * 0.25)
                    
                    success_drag_count += 1
                    print(f"    [⚡] TURBO DRAG KE-{success_drag_count} -> ({target_x}, {target_y}) | Dim: {w}x{h}")
                    
                    # 1. Meluncur cepat ke posisi objek
                    self.ctrl.smooth_move_curve(target_x, target_y, steps=12, duration=0.08)
                    
                    # 2. Genggam barang solid
                    self.ctrl.mouse_down() 
                    time.sleep(0.03) 
                    
                    # 3. Menyeret cepat ke titik drop tengah meja
                    self.ctrl.smooth_move_curve(self.drop_target_x, self.drop_target_y, steps=18, duration=0.14)
                    time.sleep(0.03) 
                    self.ctrl.mouse_up() 
                    
                    last_material_seen_time = time.time() # Segarkan detak timeout secara valid!
                    bahan_ditemukan_di_frame_ini = True
                    
                    if self.smart_sleep(0.50): 
                        break
            
            if bahan_ditemukan_di_frame_ini:
                continue
                
            # --- EVALUASI TIMEOUT EMERGENCY MURNI ---
            if time.time() - last_material_seen_time > MATERIAL_CLEAR_TIMEOUT:
                print(f"    [📢] Meja bersih sempurna! Total {success_drag_count} bahan berhasil dipindahkan.")
                break
                
            time.sleep(0.01)
            
        self.camera.stop()
        
    def run_production_cycle(self):
        """Satu rantai siklus produksi penuh Fase 3"""
        print(f"\n[🔄] Menjalankan Siklus Produksi Fase 3 Ke-{self.loop_counter + 1}...")
        
        # ----------------------------------------------------------------------
        # STEP 1: OPEN INTERACTION RADIAL MENU
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
        
        if self.smart_sleep(1.50): return 

        # ----------------------------------------------------------------------
        # STEP 2: SCAN & EXECUTE DRAG AND DROP 10 TIMES
        # ----------------------------------------------------------------------
        self.scan_and_drag_materials(target_count=10)
        if self.check_interrupt(): return
        
        self.loop_counter += 1
        print(f"[✅] SIKLUS FASE 3 KE-{self.loop_counter} SELESAI. MERESET ALUR...")
        
        # --- [PERBAIKAN TRANSISI] DIKUNCI MURNI 1 DETIK PASCA SIKLUS SELESAI ---
        print("    -> Menunggu cooldown transisi ultra cepat selama 1 detik...")
        if self.smart_sleep(1.00): return

    def start_engine(self):
        print("==================================================")
        print("        METH AUTOMATION PHASE 3 ENGINE V1.4       ")
        print("     Fixed Object Attributes & Strict S-Curve     ")
        print("==================================================")
        print(" [9] - MULAI EKSEKUSI PENGULANGAN PHASE 3 (INFINITE)")
        print(" [0] - HALT ENGINE & RESET KE MODE STANDBY         ")
        print("==================================================")
        print("Status: STANDBY (Menunggu perintah input '9'...)\n")

        try:
            while True:
                time.sleep(0.1)
                if self.ctrl.is_key_pressed(0x39): 
                    if not self.is_running:
                        print("\n[🟢] ENGINE PHASE 3 ACTIVE: Menjalankan...")
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
    engine = MethPhase3Engine()
    engine.start_engine()