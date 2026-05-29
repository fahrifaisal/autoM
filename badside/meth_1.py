import sys
import ctypes
import time
import random

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
# 2. HIGH-PRECISION INPUT ENGINE (Win32 API - Hardware Level Emulator)
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
MOUSEEVENTF_WHEEL = 0x0800
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

    def scroll_wheel(self, clicks):
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.mi = MouseInput(0, 0, clicks * 120, MOUSEEVENTF_WHEEL, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(INPUT_MOUSE), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

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

    def smooth_move_curve(self, target_x, target_y, steps=40, duration=0.25):
        """Pergerakan kursor berbasis interpolasi S-Curve sinusoidal antimacet"""
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
# 3. LOOPS PRODUCTION CORE ENGINE
# ==============================================================================
class MethMacroEngine:
    def __init__(self):
        self.ctrl = MacroController()
        self.is_running = False
        self.loop_counter = 0

    def check_interrupt(self):
        """Panic Button [0] untuk menghentikan makro secara instan ke Standby"""
        if self.ctrl.is_key_pressed(0x30): # Tombol '0'
            print("\n[🚨] PANIC STOP! Melepas kuncian kontrol dan kembali ke Standby...")
            self.ctrl.mouse_up()
            self.ctrl.key_up(0x38) # Lepas Alt jika masih tertahan
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

    def run_production_cycle(self):
        """Eksekusi loop berkelanjutan berdasarkan alur mekanis koreksi murni"""
        print(f"\n[🔄] Menjalankan Siklus Produksi Ke-{self.loop_counter + 1}...")
        
        # ----------------------------------------------------------------------
        # STEP 1: MEMBUKA MENU (Mekanik Murni Instan)
        # ----------------------------------------------------------------------
        if self.smart_sleep(0.60): return
        self.ctrl.key_down(0x38) # Tombol Alt ditekan (Kursor otomatis di tengah oleh game)
        if self.smart_sleep(0.74): return
        
        # Klik kiri ditahan di posisi tengah bawaan game untuk memicu radial menu
        self.ctrl.mouse_down()
        if self.smart_sleep(0.11): return
        self.ctrl.mouse_up()
        
        # Langsung meluncur halus ke tombol start di (817, 471) tanpa gerakan memutar
        self.ctrl.smooth_move_curve(817, 471, steps=15, duration=0.15)
        self.ctrl.click_instant(hold_time=0.122)
        if self.smart_sleep(0.48): return
        
        self.ctrl.key_up(0x38) # Lepas Alt untuk konfirmasi masuk minigame
        
        print("    -> Menunggu UI minigame memuat sempurna...")
        if self.smart_sleep(1.50): return

        # ----------------------------------------------------------------------
        # STEP 2: BAHAN 1 PROCESSING
        # ----------------------------------------------------------------------
        print("    -> Memproses Bahan 1 (Hold -> Drag ke Tengah -> Scroll 18x)...")
        self.ctrl.smooth_move_curve(1177, 574, steps=15, duration=0.15)
        self.ctrl.mouse_down()
        if self.smart_sleep(0.10): return
        
        self.ctrl.smooth_move_curve(948, 337, steps=80, duration=0.30)
        self.ctrl.smooth_move_curve(948, 336, steps=5, duration=0.05)
        
        start_scroll_b1 = time.time()
        for _ in range(18):
            self.ctrl.scroll_wheel(-1)
            time.sleep(0.04) 
            
        elapsed_scroll_b1 = time.time() - start_scroll_b1
        remaining_hold_b1 = max(0.01, 3.55 - 0.35 - elapsed_scroll_b1)
        if self.smart_sleep(remaining_hold_b1): return
        
        self.ctrl.mouse_up() 
        if self.smart_sleep(0.20): return 

        # ----------------------------------------------------------------------
        # STEP 3: BAHAN 2 PROCESSING
        # ----------------------------------------------------------------------
        print("    -> Memproses Bahan 2 (Hold -> Drag ke Tengah -> Scroll 18x)...")
        self.ctrl.smooth_move_curve(1283, 591, steps=15, duration=0.15)
        self.ctrl.mouse_down()
        if self.smart_sleep(0.10): return
        
        self.ctrl.smooth_move_curve(953, 322, steps=80, duration=0.30)
        self.ctrl.smooth_move_curve(953, 320, steps=5, duration=0.05)
        
        start_scroll_b2 = time.time()
        for _ in range(18):
            self.ctrl.scroll_wheel(-1)
            time.sleep(0.04)
            
        elapsed_scroll_b2 = time.time() - start_scroll_b2
        remaining_hold_b2 = max(0.01, 3.55 - 0.35 - elapsed_scroll_b2)
        if self.smart_sleep(remaining_hold_b2): return
        
        self.ctrl.mouse_up() 
        if self.smart_sleep(0.20): return 

        # ----------------------------------------------------------------------
        # STEP 4: BAHAN 3 PROCESSING
        # ----------------------------------------------------------------------
        print("    -> Memproses Bahan 3 (Hold -> Drag ke Tengah -> Release)...")
        self.ctrl.smooth_move_curve(1394, 590, steps=15, duration=0.15)
        self.ctrl.mouse_down()
        if self.smart_sleep(0.10): return
        
        self.ctrl.smooth_move_curve(970, 341, steps=40, duration=0.60) 
        if self.smart_sleep(0.15): return
        self.ctrl.mouse_up() 
        if self.smart_sleep(0.56): return
        
        # ----------------------------------------------------------------------
        # STEP 5: FINALISASI
        # ----------------------------------------------------------------------
        print("    -> Menjalankan Tahap Finalisasi Rakitan Akhir...")
        print("    -> Mengeklik Tombol Adu...")
        self.ctrl.smooth_move_curve(856, 578, steps=15, duration=0.12)
        self.ctrl.click_instant(hold_time=0.166)
        if self.smart_sleep(3.00): return

        print("    -> Mengeklik Tombol Masak (Siklus Sukses).")
        self.ctrl.smooth_move_curve(666, 222, steps=15, duration=0.12)
        self.ctrl.click_instant(hold_time=0.152)
        
        self.loop_counter += 1
        print(f"[✅] SIKLUS KE-{self.loop_counter} SELESAI SEMPURNA.")
        
        print("    -> Menunggu cooldown transisi 6 detik untuk perulangan berikutnya...")
        if self.smart_sleep(6.00): return

    def start_engine(self):
        print("==================================================")
        print("        METH AUTOMATION PRODUCTION CORE V1.5      ")
        print("       Win32 SendInput Hardware Emulation         ")
        print("==================================================")
        print(" [9] - MULAI PENGULANGAN MAKRO UTUH (INFINITE)    ")
        print(" [0] - HALT ENGINE & RESET KE MODE STANDBY         ")
        print("==================================================")
        print("Status: STANDBY (Menunggu perintah input '9'...)\n")

        try:
            while True:
                time.sleep(0.1)
                if self.ctrl.is_key_pressed(0x39): # Tombol '9' Start
                    if not self.is_running:
                        print("\n[🟢] ENGINE ACTIVE: Menjalankan Rantai Makro Otomatis...")
                        self.is_running = True
                        
                        while self.is_running:
                            self.run_production_cycle()
                            time.sleep(0.5)
                            if self.check_interrupt():
                                break

                        print("\n[🔒] Engine Dimatikan. Kembali ke Mode Standby...")
                        print("Tekan '9' jika ingin menjalankan kembali.\n")

        except KeyboardInterrupt:
            print("\n[!] Program ditutup melalui terminal.")
            sys.exit(0)

if __name__ == "__main__":
    engine = MethMacroEngine()
    engine.start_engine()