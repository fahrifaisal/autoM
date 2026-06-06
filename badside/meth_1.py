import sys
import ctypes
import time
import random
import numpy as np

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
        time.sleep(hold_time + random.uniform(-0.004, 0.006))
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

    def interpolate_vector_stream(self, raw_target_x, raw_target_y, steps=25, base_duration=0.18):
        """Mekanisme Pergerakan Mouse Gaussian Curve Adaptif dengan Micro-Jitter Spasial"""
        # 1. Suntikkan randomizer tipis pada koordinat akhir (Penyimpangan Spasial Alami)
        target_x = raw_target_x + random.randint(-2, 2)
        target_y = raw_target_y + random.randint(-2, 2)
        
        start_x, start_y = self.get_cursor_pos()
        dx = target_x - start_x
        dy = target_y - start_y
        if dx == 0 and dy == 0: return
        
        # Pengacak dinamis untuk total langkah dan durasi keseluruhan agar fluktuatif
        fuzzed_steps = steps + random.randint(-2, 3)
        fuzzed_duration = base_duration + random.uniform(-0.015, 0.025)
        sleep_interval = fuzzed_duration / fuzzed_steps
        
        for i in range(1, fuzzed_steps + 1):
            t = i / fuzzed_steps
            # S-Curve Sinusoidal dasar
            smooth_t = t * t * (3 - 2 * t)
            
            curr_x = start_x + (dx * smooth_t)
            curr_y = start_y + (dy * smooth_t)
            
            # Suntikkan getaran motorik mikro (Bio-Tremor) yang mengecil secara linear menjelang target akhir
            damping_factor = (1.0 - t) * 1.8
            jitter_x = np.random.normal(0, damping_factor) if damping_factor > 0 else 0
            jitter_y = np.random.normal(0, damping_factor) if damping_factor > 0 else 0
            
            ctypes.windll.user32.SetCursorPos(int(curr_x + jitter_x), int(curr_y + jitter_y))
            time.sleep(sleep_interval)


# ==============================================================================
# 3. LOOPS PRODUCTION CORE ENGINE
# ==============================================================================
class KernelTaskScheduler:
    def __init__(self):
        self.ctrl = WinNativeDispatcher()
        self.is_running = False
        self.loop_counter = 0

    def check_interrupt(self):
        """Panic Button [0] untuk menghentikan makro secara instan ke Standby"""
        if self.ctrl.is_key_pressed(0x30): 
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

    def execute_subsystem_routine(self):
        """Eksekusi rangkaian makro berbasis koordinat teracak tipis antimacet"""
        print(f"\n[🔄] Processing production sequence iteration -> {self.loop_counter + 1}...")
        
        # ----------------------------------------------------------------------
        # STEP 1: MEMBUKA MENU (Mekanik Murni Instan)
        # ----------------------------------------------------------------------
        if self.smart_sleep(0.60 + random.uniform(-0.02, 0.03)): return
        self.ctrl.key_down(0x38) 
        if self.smart_sleep(0.74 + random.uniform(-0.01, 0.04)): return
        
        self.ctrl.mouse_down()
        if self.smart_sleep(0.11 + random.uniform(-0.005, 0.01)): return
        self.ctrl.mouse_up()
        
        # Meluncur cepat-halus ke tombol start radial menu
        self.ctrl.interpolate_vector_stream(817, 471, steps=12, base_duration=0.12)
        self.ctrl.click_instant(hold_time=0.122)
        if self.smart_sleep(0.48): return
        
        self.ctrl.key_up(0x38) 
        
        print("    -> [INFO] Awaiting interface canvas initialization...")
        if self.smart_sleep(1.50 + random.uniform(-0.03, 0.05)): return

        # ----------------------------------------------------------------------
        # STEP 2: BAHAN 1 PROCESSING
        # ----------------------------------------------------------------------
        print("    -> [STAGE 1] Merging channel element-1 to core axis...")
        self.ctrl.interpolate_vector_stream(1177, 574, steps=12, base_duration=0.12)
        self.ctrl.mouse_down()
        if self.smart_sleep(0.10): return
        
        self.ctrl.interpolate_vector_stream(948, 337, steps=65, base_duration=0.24)
        self.ctrl.interpolate_vector_stream(948, 336, steps=4, base_duration=0.04)
        
        start_scroll_b1 = time.time()
        for _ in range(18):
            self.ctrl.scroll_wheel(-1)
            time.sleep(0.04 + random.uniform(-0.003, 0.002)) 
            
        elapsed_scroll_b1 = time.time() - start_scroll_b1
        remaining_hold_b1 = max(0.01, 4.6 - 0.35 - elapsed_scroll_b1)
        if self.smart_sleep(remaining_hold_b1): return
        
        self.ctrl.mouse_up() 
        if self.smart_sleep(0.20 + random.uniform(0.01, 0.03)): return 

        # ----------------------------------------------------------------------
        # STEP 3: BAHAN 2 PROCESSING
        # ----------------------------------------------------------------------
        print("    -> [STAGE 2] Merging channel element-2 to core axis...")
        self.ctrl.interpolate_vector_stream(1283, 591, steps=12, base_duration=0.12)
        self.ctrl.mouse_down()
        if self.smart_sleep(0.10): return
        
        self.ctrl.interpolate_vector_stream(953, 322, steps=65, base_duration=0.24)
        self.ctrl.interpolate_vector_stream(953, 320, steps=4, base_duration=0.04)
        
        start_scroll_b2 = time.time()
        for _ in range(18):
            self.ctrl.scroll_wheel(-1)
            time.sleep(0.04 + random.uniform(-0.003, 0.002))
            
        elapsed_scroll_b2 = time.time() - start_scroll_b2
        remaining_hold_b2 = max(0.01, 4.6 - 0.35 - elapsed_scroll_b2)
        if self.smart_sleep(remaining_hold_b2): return
        
        self.ctrl.mouse_up() 
        if self.smart_sleep(0.20 + random.uniform(0.01, 0.03)): return 

        # ----------------------------------------------------------------------
        # STEP 4: BAHAN 3 PROCESSING
        # ----------------------------------------------------------------------
        print("    -> [STAGE 3] Dragging structural binder-3 to allocation zone...")
        self.ctrl.interpolate_vector_stream(1394, 590, steps=12, base_duration=0.12)
        self.ctrl.mouse_down()
        if self.smart_sleep(0.10): return
        
        self.ctrl.interpolate_vector_stream(970, 341, steps=35, base_duration=0.45) 
        if self.smart_sleep(0.15): return
        self.ctrl.mouse_up() 
        if self.smart_sleep(0.56 + random.uniform(-0.02, 0.02)): return
        
        # ----------------------------------------------------------------------
        # STEP 5: FINALISASI
        # ----------------------------------------------------------------------
        print("    -> [FINAL] Executing synthesis link verification...")
        self.ctrl.interpolate_vector_stream(856, 578, steps=12, base_duration=0.10)
        self.ctrl.click_instant(hold_time=0.166)
        if self.smart_sleep(3.00 + random.uniform(0.02, 0.08)): return

        print("    -> [SUCCESS] Verification accepted. Committing persistent logs.")
        self.ctrl.interpolate_vector_stream(666, 222, steps=12, base_duration=0.10)
        self.ctrl.click_instant(hold_time=0.152)
        
        self.loop_counter += 1
        print(f"[✅] ALL SUB-ROUTINES FOR CYCLE {self.loop_counter} COMMITTED SUCCESSFULLY.")
        
        print("    -> Awaiting cooldown gate transition (6 seconds)...")
        if self.smart_sleep(6.50 + random.uniform(-0.05, 0.15)): return

    def start_engine(self):
        print("==================================================")
        print("        CORE SUBSYSTEM TASK ALLOCATOR V2.1        ")
        print("       Win32 Kernel SendInput Infrastructure       ")
        print("==================================================")
        print(" [9] - ALLOCATE SUB-ROUTINE STREAM PIPELINE       ")
        print(" [0] - HALT ACTIVE CONTEXTS & RESET STANDBY       ")
        print("==================================================")
        print("Status: SERVICE_STANDBY (Awaiting opcode signal '9'...)\n")

        try:
            while True:
                time.sleep(0.1)
                if self.ctrl.is_key_pressed(0x39): # Tombol '9' Start
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
            print("\n[!] Connection closed via remote terminal signal.")
            sys.exit(0)

if __name__ == "__main__":
    engine = KernelTaskScheduler()
    engine.start_engine()
