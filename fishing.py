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
# 1. SYSTEM ENVIRONMENT STABILIZATION (DPI CORE LOCK)
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
# 2. ANTI-HEURISTIC MEMORY ENTROPY SHIFTER
# ==============================================================================
def sys_allocate_polymorphic_buffer():
    """Spoofing RAM: Mengubah footprint Signature Hash proses secara konstan"""
    transient_entropy = []
    for _ in range(random.randint(3, 8)):
        transient_entropy.append(np.random.bytes(random.randint(10, 45)))
    del transient_entropy

# ==============================================================================
# 3. CORE INPUT DISPATCHER (Win32 SendInput Native Interface)
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

class IOStreamController:
    def __init__(self):
        self.io_state_active = False

    def trigger_down_event(self):
        if not self.io_state_active:
            extra = ctypes.c_ulong(0)
            ii_ = Input_I()
            ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, ctypes.pointer(extra))
            x = Input(ctypes.c_ulong(INPUT_MOUSE), ii_)
            ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
            self.io_state_active = True

    def trigger_up_event(self):
        if self.io_state_active:
            extra = ctypes.c_ulong(0)
            ii_ = Input_I()
            ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_LEFTUP, 0, ctypes.pointer(extra))
            x = Input(ctypes.c_ulong(INPUT_MOUSE), ii_)
            ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
            self.io_state_active = False

    def execute_single_signal(self):
        duration = random.uniform(0.021, 0.038) 
        self.trigger_down_event()
        time.sleep(duration)
        self.trigger_up_event()

    def transmit_key_hold(self, scan_code, hold_duration):
        extra = ctypes.c_ulong(0)
        ii_down = Input_I()
        ii_down.ki = KeyBdInput(0, scan_code, KEYEVENTF_SCANCODE, 0, ctypes.pointer(extra))
        x_down = Input(ctypes.c_ulong(INPUT_KEYBOARD), ii_down)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x_down), ctypes.sizeof(x_down))
        
        time.sleep(hold_duration + random.uniform(-0.003, 0.005))
        
        ii_up = Input_I()
        ii_up.ki = KeyBdInput(0, scan_code, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP, 0, ctypes.pointer(extra))
        x_up = Input(ctypes.c_ulong(INPUT_KEYBOARD), ii_up)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x_up), ctypes.sizeof(x_up))

    def dispatch_tap(self, scan_code):
        self.transmit_key_hold(scan_code, random.uniform(0.121, 0.174))

    def write_buffer_sequence(self, text_sequence: str):
        mapping_tables = {
            'f': 0x21, 'i': 0x17, 'x': 0x2D, 'u': 0x16,
            'r': 0x13, 'e': 0x12, 'l': 0x26, 'o': 0x18, 'a': 0x1E, 'd': 0x20,
            's': 0x1F, 'k': 0x25, 'n': 0x31, 'q': 0x10, 't': 0x14
        }
        for element in text_sequence.lower():
            if element in mapping_tables:
                self.dispatch_tap(mapping_tables[element])
                time.sleep(random.uniform(0.041, 0.075))

    def verify_hardware_state(self, virtual_key):
        return (ctypes.windll.user32.GetAsyncKeyState(virtual_key) & 0x8000) != 0

    def query_pointer_position(self):
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        pt = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.pointer(pt))
        return pt.x, pt.y

    def smooth_pointer_interpolation(self, target_x, target_y, steps=20, base_duration=0.20):
        start_x, start_y = self.query_pointer_position()
        delta_x = target_x - start_x
        delta_y = target_y - start_y
        
        dynamic_steps = steps + random.randint(-1, 3)
        dynamic_duration = base_duration + random.uniform(-0.02, 0.04)
        sleep_interval = dynamic_duration / dynamic_steps
        
        for idx in range(1, dynamic_steps + 1):
            progress = idx / dynamic_steps
            smooth_progress = progress * progress * (3 - 2 * progress)
            
            current_target_x = start_x + (delta_x * smooth_progress)
            current_target_y = start_y + (delta_y * smooth_progress)
            
            scale_factor = (1.0 - progress) * 2.5
            jitter_x = np.random.normal(0, scale_factor)
            jitter_y = np.random.normal(0, scale_factor)
            
            ctypes.windll.user32.SetCursorPos(int(current_target_x + jitter_x), int(current_target_y + jitter_y))
            time.sleep(sleep_interval)


# ==============================================================================
# 4. MAIN DATA STREAM PIPELINE (Anti-Heuristic System Architecture)
# ==============================================================================
class OperationalDataPipeline:
    def __init__(self, output_to_console=True):
        self.handler = IOStreamController()
        self.output_to_console = output_to_console
        
        self.initialize_configuration_profile()
        
        # Batas vertikal dikunci di 1050px murni agar mencakup area bawah layar game
        self.capture_bounds = (
            int(600 * self.scale_factor_x), 
            int(250 * self.scale_factor_y), 
            int(1200 * self.scale_factor_x), 
            int(1050 * self.scale_factor_y)
        )
        
        self.dx_capture_session = None
        try:
            self.dx_capture_session = dxcam.create(output_color="BGR", max_buffer_len=8)
        except Exception as primary_gpu_fault:
            if self.output_to_console:
                print(f"\n[⚠️] Native API Link Refused: {primary_gpu_fault}. Swapping to Output Channel-0...")
            try:
                if hasattr(dxcam, "Instance") and dxcam.Instance is not None:
                    dxcam.Instance = None
                self.dx_capture_session = dxcam.create(device_idx=0, output_idx=0, output_color="BGR")
            except Exception as fatal_exception:
                print(f"\n[🚨] MULTI-DEVICE HANDSHAKE CRITICAL LOSS: {fatal_exception}")
                print("     SOLUSI: Masuk Graphics Settings Windows, set biner .exe ke 'Power Saving'!")
                time.sleep(6.0)
                sys.exit(1)
            
        self.dx_capture_session.start(target_fps=self.pipeline_fps, region=self.capture_bounds)
        time.sleep(1.5)

        self.lower_tier_g = np.array([0, 120, 165])
        self.upper_tier_g = np.array([50, 255, 255])
        self.lower_tier_w = np.array([0, 0, 160])
        self.upper_tier_w = np.array([179, 50, 255])
        
        # Range HSV fleksibel menangkap piksel putih teks (0, 0, 100) hingga batas atas bender
        self.lower_collect_white = np.array([0, 0, 180])
        self.upper_collect_white = np.array([0, 0, 255])
        
        self.current_node_state = "NODE_0_IDLE"
        self.verbosity_log_active = True
        
        self.sys_flag_8 = False
        self.routine_switch_active = False
        self.sys_flag_7 = False
        self.termination_protocol_active = False
        self.sys_flag_6 = False
        
        self.last_routine_execution_timestamp = time.time()
        self.awaiting_node_start_time = 0
        self.sequential_timeout_anomalies = 0
        
        self.last_printed_state = None
        self.last_printed_text = None

        self.purge_pipeline_buffers()

    def initialize_configuration_profile(self):
        application_path = os.getcwd()
        config_path = os.path.join(application_path, 'config.ini')
        parser = configparser.ConfigParser()

        if not os.path.exists(config_path):
            parser['ENGINE'] = {
                'SCREEN_WIDTH': '1920',
                'SCREEN_HEIGHT': '1080',
                'TARGET_FPS': '60',            
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
            try:
                with open(config_path, 'w') as configfile:
                    parser.write(configfile)
            except Exception:
                config_path = os.path.join(os.getcwd(), 'config.ini')
                with open(config_path, 'w') as configfile:
                    parser.write(configfile)

        parser.read(config_path)
        
        self.display_width = int(parser['ENGINE'].get('SCREEN_WIDTH', '1920'))
        self.display_height = int(parser['ENGINE'].get('SCREEN_HEIGHT', '1080'))
        self.pipeline_fps = int(parser['ENGINE'].get('TARGET_FPS', '60'))
        self.runtime_stall_limit = int(parser['ENGINE'].get('STALL_FRAMES', '9999'))
        self.max_timeout_threshold = int(parser['ENGINE'].get('TIMEOUT_SECONDS', '30'))
        self.routine_delay_interval = float(parser['ENGINE'].get('AFK_INTERVAL_MINUTES', '40'))
        self.allocation_sleep_delay = float(parser['ENGINE'].get('CAST_DELAY_SECONDS', '5.0'))
        
        self.scale_factor_x = self.display_width / 1920.0
        self.scale_factor_y = self.display_height / 1080.0

        self.LIMIT_G = int(int(parser['ENGINE'].get('ABSOLUTE_MAX_GREEN', '360')) * self.scale_factor_y)
        self.VAL_THRESHOLD = int(int(parser['ENGINE'].get('SUCCESS_THRESHOLD', '390')) * self.scale_factor_y)
        self.BUFFER_S = int(int(parser['ENGINE'].get('SAFETY_BUFFER', '15')) * self.scale_factor_y)
        self.SWING_MIN_BOUND = int(int(parser['ENGINE'].get('MIN_SWING', '120')) * self.scale_factor_y)
        self.HIGH_BAND_LIMIT = int(int(parser['ENGINE'].get('MAX_BAND_HIGH', '100')) * self.scale_factor_y)
        self.CRIT_GRIP_LIMIT = int(int(parser['ENGINE'].get('TIGHT_GRIP_THRESHOLD', '80')) * self.scale_factor_y)
        self.CRIT_GRIP_SWING = int(int(parser['ENGINE'].get('TIGHT_GRIP_SWING', '50')) * self.scale_factor_y)

    def purge_pipeline_buffers(self):
        self.node_runtime_start = 0
        self.last_frame_verification_time = 0
        self.peak_buffer_w_h = 0
        self.peak_buffer_g_h = 0
        self.history_g_h = 0
        self.history_w_h = 0
        self.history_variance = 0
        self.incremental_variance = 0
        self.state_cooldown_active = True
        self.stream_ever_validated = False
        self.recovery_bypass_active = False
        self.stagnant_frame_accumulation = 0

    def secure_sleep_interceptor(self, duration_period):
        checkpoint = time.time()
        while time.time() - checkpoint < duration_period:
            if self.handler.verify_hardware_state(0x58): 
                return True
            time.sleep(0.04)
        return False

    def execute_interface_sync(self):
        self.handler.dispatch_tap(0x42) # F8
        time.sleep(0.5)                
        self.handler.write_buffer_sequence("fixui")  
        time.sleep(0.2)
        self.handler.dispatch_tap(0x1C) # Enter
        time.sleep(0.6)                
        self.handler.dispatch_tap(0x42) # F8
        time.sleep(0.8)                

    def force_pipeline_shutdown(self):
        if self.output_to_console:
            print("\n[🚨] TIMEOUT CRITICAL EXHAUSTED: SEVERING RESOURCE LINKS...")
        self.handler.trigger_up_event()
        self.handler.dispatch_tap(0x42) 
        time.sleep(0.4)
        self.handler.write_buffer_sequence("quit")    
        self.handler.dispatch_tap(0x1C) 
        time.sleep(1.0)
        self.dx_capture_session.stop()
        sys.exit(0)
        
    # ==========================================================================
    # CORE OPENCV SCANNER ENGINE: HIGH-RELIABILITY TEXT DETECTOR V5.5 (PURE GATE)
    # ==========================================================================
    def dispatch_payload_collection(self):
        if self.output_to_console:
            print("\n[🔍] Fase 3 Sukses. Memulai Pemindaian Blok Karakter Teks 'Keep'...")
            
        start_scan_window = time.time()
        button_clicked = False
        
        while time.time() - start_scan_window < 4.0: 
            if self.handler.verify_hardware_state(0x58): return
            
            collect_frame = self.dx_capture_session.get_latest_frame()
            if collect_frame is None:
                time.sleep(0.005)
                continue
                
            hsv_canvas = cv2.cvtColor(collect_frame, cv2.COLOR_BGR2HSV)
            collect_mask = cv2.inRange(hsv_canvas, self.lower_collect_white, self.upper_collect_white)
            contours, _ = cv2.findContours(collect_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for c in contours:
                area = cv2.contourArea(c)

                if 3 < area < 100:
                    x_loc, y_loc, w_dim, h_dim = cv2.boundingRect(c)
                    
                    # Proyeksi ke koordinat fisik monitor absolut global Windows
                    abs_x = self.capture_bounds[0] + x_loc + (w_dim // 2)
                    abs_y = self.capture_bounds[1] + y_loc + (h_dim // 2)
                    
                    # --- FILTER GEOMETRI 2: GERBANG ROI GEOMETRIS KOORDINAT UTAMA ---
                    min_allowed_x = int(800 * self.scale_factor_x)
                    max_allowed_x = int(930 * self.scale_factor_x)
                    min_allowed_y = int(930 * self.scale_factor_y)
                    max_allowed_y = int(1010 * self.scale_factor_y)
                    
                    # Eksekusi interupsi hanya jika lolos uji kecerahan HSV murni dan masuk gerbang sakral
                    if (min_allowed_x <= abs_x <= max_allowed_x) and (min_allowed_y <= abs_y <= max_allowed_y):
                        if self.output_to_console:
                            print(f"[🎯] TARGET 'KEEP' SECURED -> Abs(X: {abs_x}, Y: {abs_y}) | Pure Contour Area: {area:.0f}px")
                        
                        # Jeda ketukan natural meniru waktu reaksi mata biologis manusia
                        time.sleep(random.uniform(0.15, 0.25))
                        self.handler.smooth_pointer_interpolation(abs_x, abs_y, steps=18, base_duration=0.18)
                        
                        time.sleep(random.uniform(0.08, 0.12))
                        self.handler.execute_single_signal() # KLIK KIRI UTAMA PENGUMPULAN IKAN
                        
                        button_clicked = True
                        break
            
            if button_clicked:
                break
            time.sleep(0.02)
            
        if not button_clicked and self.output_to_console:
            print("\n[⚠️] Jendela waktu scan habis. Karakter teks 'Keep' tidak terwujud di dalam gerbang ROI.")

    def execute_maintenance_sequence(self):
        self.handler.transmit_key_hold(0x20, 1.0)
        if self.secure_sleep_interceptor(0.05): return
        self.handler.transmit_key_hold(0x1E, 1.0)
        if self.secure_sleep_interceptor(0.05): return
        
        self.handler.dispatch_tap(0x05)
        if self.secure_sleep_interceptor(7.0): return
        self.handler.dispatch_tap(0x06)
        if self.secure_sleep_interceptor(7.0): return

    def print_pipeline_statistics(self, process_text):
        if not self.output_to_console: return
        if self.current_node_state == self.last_printed_state and process_text == self.last_printed_text:
            return
            
        mt_flag = "ACTIVE" if self.routine_switch_active else "STABLE"
        term_flag = "ARMED" if self.termination_protocol_active else "STANDBY"
        
        print(f"[STATUS] Node: {self.current_node_state:<22} | Log: {process_text:<45} | Schedule: {mt_flag} | Protection: {term_flag}")
        
        self.last_printed_state = self.current_node_state
        self.last_printed_text = process_text

    def print_initialization_manifest(self):
        if not self.output_to_console: return
        print("==================================================")
        print("        SYSTEM DX-PIPELINE SERVICE ENGINE V4.3    ")
        print("      Sub-Architecture: Pure Asynchronous TUI     ")
        print("==================================================")
        print(f"[INIT] Display Grid Matrix : {self.display_width}x{self.display_height} (Scale Lock)")
        print(f"[INIT] Video Stream Engine : {self.pipeline_fps} FPS | Allocation Core: {self.runtime_stall_limit} Frm")
        print(f"[INIT] Upper Sync Floor    : {self.LIMIT_G} | Bounds Target: >{self.VAL_THRESHOLD}")
        print(f"[INIT] Interceptor Timeout : {self.max_timeout_threshold}s Layer-control Active")
        print("==================================================")
        print("[8] - Toggle Live Console TUI Monitor Viewports (CMD)")
        print("[9] - Safe Exit Thread Allocation")
        print("[7] - Toggle Internal Schedule Cycles")
        print("[6] - Toggle Layer-6 Emergency Safe Shutdown")
        print("[3] - MANUAL INJECT SYNC THREAD START")
        print("[X] - Instant Hardware Panic Breakpoint Rollback")
        print("==================================================")

    def run(self):
        self.print_initialization_manifest()
        process_text = "Awaiting inject activation trigger '3'..."
        
        try:
            while True:
                # ==============================================================
                # SEKTOR PRIORITAS 1: GERBANG INTERUPSI HOTKEY GLOBAL (INSTAN)
                # ==============================================================
                if self.handler.verify_hardware_state(0x39): break # Key '9' Safe Exit
                
                if self.handler.verify_hardware_state(0x38): # Key '8'
                    if not self.sys_flag_8:
                        self.verbosity_log_active = not self.verbosity_log_active
                        status_msg = "SHOW STATS" if self.verbosity_log_active else "HIDE STATS"
                        print(f"\n[*] MONITOR SYSTEM INTERFACE LOG: {status_msg}")
                        self.sys_flag_8 = True
                else:
                    self.sys_flag_8 = False

                if self.handler.verify_hardware_state(0x37): # Key '7'
                    if not self.sys_flag_7:
                        self.routine_switch_active = not self.routine_switch_active
                        status_msg = "ON" if self.routine_switch_active else "OFF"
                        print(f"\n[!] INTERNAL AUTO-SCHEDULE ENGINE: {status_msg}")
                        self.sys_flag_7 = True
                else:
                    self.sys_flag_7 = False

                if self.handler.verify_hardware_state(0x36): # Key '6'
                    if not self.sys_flag_6:
                        self.termination_protocol_active = not self.termination_protocol_active
                        status_msg = "ON" if self.termination_protocol_active else "OFF"
                        print(f"\n[⚠️] PROTECTION PROTOCOL INTERCEPTOR LAYER-6: {status_msg}")
                        self.sys_flag_6 = True
                else:
                    self.sys_flag_6 = False

                if self.handler.verify_hardware_state(0x58): # Key 'X' Reset Panic
                    if self.current_node_state != "NODE_0_IDLE":
                        print("\n[🚨] PANIC BREAKPOINT INTERRUPT! Rolling back to idle engine state...")
                        self.handler.trigger_up_event() 
                        self.current_node_state = "NODE_0_IDLE"
                        self.purge_pipeline_buffers()
                        self.sequential_timeout_anomalies = 0
                        process_text = "Awaiting inject activation trigger '3'..."
                        time.sleep(0.5) 
                        continue

                if self.current_node_state == "NODE_0_IDLE":
                    process_text = "Awaiting inject activation trigger '3'..."
                    if self.handler.verify_hardware_state(0x33): # Key '3'
                        print("\n>>> INJECT SIGNALS RECOGNIZED: INITIALIZING STREAM MONITOR SIKLUS-1...")
                        self.current_node_state = "NODE_1_SCANNING"
                        self.awaiting_node_start_time = time.time() 
                        self.sequential_timeout_anomalies = 0
                        process_text = "SCANNING ENGINE ACTIVE"
                        time.sleep(1.0) 

                if self.verbosity_log_active:
                    self.print_pipeline_statistics(process_text)

                # ==============================================================
                # SEKTOR PRIORITAS 2: PENANGKAPAN CITRA DAN MANAGEMENT MEMORI
                # ==============================================================
                frame_packet = self.dx_capture_session.get_latest_frame()
                if frame_packet is None:
                    time.sleep(0.001)
                    continue
                    
                sys_allocate_polymorphic_buffer()

                try:
                    if self.current_node_state == "NODE_1_SCANNING":
                        if time.time() - self.awaiting_node_start_time > self.max_timeout_threshold: 
                            self.sequential_timeout_anomalies += 1 
                            print(f"\n[⚠️] ANOMALOUS TIMEOUT: Stream lost iteration -> {self.sequential_timeout_anomalies}")
                            
                            if self.sequential_timeout_anomalies == 1:
                                self.handler.dispatch_tap(0x04) 
                                self.awaiting_node_start_time = time.time()
                                time.sleep(1.5)
                                continue
                            elif self.sequential_timeout_anomalies == 2:
                                self.execute_interface_sync() 
                                self.handler.dispatch_tap(0x04) 
                                self.awaiting_node_start_time = time.time()
                                time.sleep(1.5)
                                continue
                            elif self.sequential_timeout_anomalies >= 6:
                                if self.termination_protocol_active:
                                    self.force_pipeline_shutdown()
                                else:
                                    print("\n[🔒] MAXIMUM LAYER INTERCEPT EXHAUSTED: FORCING STANDBY PACKET STATE...")
                                    self.handler.trigger_up_event()
                                    self.current_node_state = "NODE_0_IDLE"
                                    self.purge_pipeline_buffers()
                                    self.sequential_timeout_anomalies = 0 
                                    process_text = "Awaiting inject activation trigger '3'..."
                                    time.sleep(1.0)
                                    continue

                        hsv_converted_matrix = cv2.cvtColor(frame_packet, cv2.COLOR_BGR2HSV)
                        data_mask_g = cv2.inRange(hsv_converted_matrix, self.lower_tier_g, self.upper_tier_g)
                        extracted_contours_g, _ = cv2.findContours(data_mask_g, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                        if extracted_contours_g:
                            prominent_contour = max(extracted_contours_g, key=cv2.contourArea)
                            if cv2.contourArea(prominent_contour) > 20: 
                                x_b, y_b, w_b, h_b = cv2.boundingRect(prominent_contour)
                                calc_h_min, calc_h_max = max(1, int(3 * self.scale_factor_y)), int(15 * self.scale_factor_y)
                                calc_w_min = int(50 * self.scale_factor_x) 
                                
                                if (calc_h_min <= h_b <= calc_h_max) and w_b > calc_w_min and w_b > (h_b * 4):
                                    process_text = "VALID TRANSITION ACQUIRED! MERGING CHANNEL..."
                                    self.handler.execute_single_signal() 
                                    time.sleep(0.2 + random.uniform(0.005, 0.015)) 
                                    
                                    self.sequential_timeout_anomalies = 0 
                                    self.purge_pipeline_buffers()
                                    self.current_node_state = "NODE_2_STREAM_PROCESSING"
                                    self.phase3_start_time = time.time() 
                                    self.last_frame_verification_time = time.time() 
                                else:
                                    process_text = "FILTER_NOISE_OVERRIDE"

                    elif self.current_node_state == "NODE_2_STREAM_PROCESSING":
                        hsv_converted_matrix = cv2.cvtColor(frame_packet, cv2.COLOR_BGR2HSV)
                        data_mask_g = cv2.inRange(hsv_converted_matrix, self.lower_tier_g, self.upper_tier_g)
                        data_mask_w = cv2.inRange(hsv_converted_matrix, self.lower_tier_w, self.upper_tier_w)
                        
                        extracted_contours_g, _ = cv2.findContours(data_mask_g, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        extracted_contours_w, _ = cv2.findContours(data_mask_w, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        
                        packet_stream_valid = False
                        current_g_h, current_w_h = 0, 0
                        forced_fallback_active = False
                        floor_override_active = False

                        if extracted_contours_w:
                            extracted_contours_w = sorted(extracted_contours_w, key=cv2.contourArea, reverse=True)
                            for segment_w in extracted_contours_w:
                                if cv2.contourArea(segment_w) >= 2: 
                                    x_t, y_t, w_t, h_t = cv2.boundingRect(segment_w)
                                    computed_w_min = max(1, int(2 * self.scale_factor_x))
                                    computed_w_max = int(25 * self.scale_factor_x)
                                    
                                    if h_t >= int(5 * self.scale_factor_y) and computed_w_min <= w_t <= computed_w_max and h_t >= (w_t * 1.2):
                                        if self.stream_ever_validated and h_t < (self.history_w_h - int(80 * self.scale_factor_y)):
                                            continue
                                        current_w_h = h_t
                                        packet_stream_valid = True  
                                        self.stream_ever_validated = True 
                                        self.last_frame_verification_time = time.time()
                                        if current_w_h > self.peak_buffer_w_h: self.peak_buffer_w_h = current_w_h
                                        break 

                        matrix_g_valid_this_tick = False
                        if packet_stream_valid and extracted_contours_g:
                            extracted_contours_g = sorted(extracted_contours_g, key=cv2.contourArea, reverse=True)
                            for segment_g in extracted_contours_g:
                                if cv2.contourArea(segment_g) >= 2: 
                                    _, _, _, hg = cv2.boundingRect(segment_g)
                                    current_g_h = hg
                                    matrix_g_valid_this_tick = True
                                    if current_g_h > self.peak_buffer_g_h: 
                                        self.peak_buffer_g_h = current_g_h
                                    break

                        if packet_stream_valid and not matrix_g_valid_this_tick:
                            if self.history_g_h > 0:
                                current_g_h = self.history_g_h 
                            else:
                                self.state_cooldown_active = True

                        if packet_stream_valid:
                            current_discrepancy = current_g_h - current_w_h
                            self.incremental_variance = current_discrepancy - self.history_variance
                            delta_w_height = current_w_h - self.history_w_h 

                            self.history_g_h = current_g_h
                            self.history_w_h = current_w_h
                            self.history_variance = current_discrepancy

                            available_safe_margin = self.LIMIT_G - current_w_h - self.BUFFER_S
                            BAND_HIGH = max(int(10 * self.scale_factor_y), min(self.HIGH_BAND_LIMIT, available_safe_margin))
                            
                            if current_w_h < int(30 * self.scale_factor_y):
                                dynamically_computed_swing = int(80 * self.scale_factor_y) 
                                BAND_HIGH = max(BAND_HIGH, int(80 * self.scale_factor_y)) 
                            elif current_w_h < int(100 * self.scale_factor_y):
                                dynamically_computed_swing = int(100 * self.scale_factor_y) 
                                BAND_HIGH = max(BAND_HIGH, int(100 * self.scale_factor_y))
                            elif current_w_h > (self.VAL_THRESHOLD - int(40 * self.scale_factor_y)):
                                dynamically_computed_swing = int(50 * self.scale_factor_y) 
                            else:
                                dynamically_computed_swing = self.SWING_MIN_BOUND

                            if current_w_h < self.CRIT_GRIP_LIMIT:
                                dynamically_computed_swing = min(dynamically_computed_swing, self.CRIT_GRIP_SWING) 

                            BAND_LOW = BAND_HIGH - dynamically_computed_swing
                            
                            if current_w_h > (self.VAL_THRESHOLD - int(40 * self.scale_factor_y)):
                                BAND_LOW = max(BAND_LOW, -int(170 * self.scale_factor_y)) 
                            else:
                                BAND_LOW = max(BAND_LOW, -int(60 * self.scale_factor_y))

                            computed_floor = int(45 * self.scale_factor_y)
                            if (current_w_h + BAND_LOW) < computed_floor:
                                BAND_LOW = computed_floor - current_w_h

                            BAND_HIGH = int(BAND_HIGH * random.uniform(0.98, 1.02))
                            BAND_LOW  = int(BAND_LOW  * random.uniform(0.98, 1.02))

                            clamped_variance = max(int(-15 * self.scale_factor_y), min(int(15 * self.scale_factor_y), self.incremental_variance))
                            effective_band_high = max(BAND_LOW + int(10 * self.scale_factor_y), BAND_HIGH - max(0, clamped_variance))
                            effective_band_low  = BAND_LOW + min(0, clamped_variance)
                                 
                            if self.state_cooldown_active:
                                if current_discrepancy <= effective_band_low: self.state_cooldown_active = False
                            else:
                                if current_discrepancy >= effective_band_high: self.state_cooldown_active = True

                            if 0 < current_w_h < int(35 * self.scale_factor_y):
                                if current_g_h < (self.LIMIT_G - int(25 * self.scale_factor_y)):
                                    self.state_cooldown_active = False
                                    floor_override_active = True

                            CEILING_ALERT_ENTER = self.LIMIT_G - int(5  * self.scale_factor_y)
                            CEILING_ALERT_EXIT  = self.LIMIT_G - int(135 * self.scale_factor_y) 
                            
                            if current_g_h >= CEILING_ALERT_ENTER: self.recovery_bypass_active = True
                            elif current_g_h <= CEILING_ALERT_EXIT: self.recovery_bypass_active = False

                            if self.recovery_bypass_active:
                                self.state_cooldown_active = True
                                forced_fallback_active = True
                                floor_override_active = False

                            if current_w_h >= int(370 * self.scale_factor_y):
                                if current_discrepancy >= int(5 * self.scale_factor_y) or current_g_h >= int(350 * self.scale_factor_y):
                                    self.state_cooldown_active = True
                                    forced_fallback_active = True

                            if not self.state_cooldown_active and not floor_override_active:
                                if self.incremental_variance <= 1 and delta_w_height <= 1: 
                                    self.stagnant_frame_accumulation += 1
                                else: 
                                    self.stagnant_frame_accumulation = 0
                                    
                                if self.stagnant_frame_accumulation >= self.runtime_stall_limit:
                                    self.state_cooldown_active = True
                                    self.stagnant_frame_accumulation = 0
                            else:
                                self.stagnant_frame_accumulation = 0

                            if self.state_cooldown_active:
                                self.handler.trigger_up_event()
                                process_text = "TRANSMITTING CONTROL RELEASE"
                            else:
                                self.handler.trigger_down_event()
                                process_text = "TRANSMITTING CONTROL HOLD"

                        if not packet_stream_valid:
                            verification_loss_duration = time.time() - self.last_frame_verification_time
                            pipeline_active_duration = time.time() - self.phase3_start_time
                            
                            fuzzed_pull_limit = 2.0 + random.uniform(-0.04, 0.03) 
                            
                            if pipeline_active_duration < fuzzed_pull_limit and self.peak_buffer_w_h < int(10 * self.scale_factor_y):
                                self.handler.trigger_down_event()
                                process_text = "INITIAL PACKET INTEGRATION ROUTINE"
                            elif self.stream_ever_validated and verification_loss_duration < 0.6:
                                self.handler.trigger_up_event() 
                                self.state_cooldown_active = True 
                                process_text = "CARRIER FLICKER FRAME INTERPOLATION"
                            else:
                                print(f"\n>>> PIPELINE TRANSITION LOSS.")
                                print(f"    METRICS: Peak White: {self.peak_buffer_w_h}px | Peak Green: {self.peak_buffer_g_h}px | Target Base: >{self.VAL_THRESHOLD}px")
                                
                                if self.peak_buffer_w_h >= self.VAL_THRESHOLD: 
                                    print(f"    CYCLE STATUS: VALIDATED SUCCESS\n")
                                    
                                    # Memicu pemindaian teks adaptif OpenCV baru
                                    self.dispatch_payload_collection() 
                                    
                                    if self.routine_switch_active and (time.time() - self.last_routine_execution_timestamp) >= (self.routine_delay_interval * 60):
                                        if self.secure_sleep_interceptor(self.allocation_sleep_delay): continue
                                        self.execute_maintenance_sequence()
                                        self.last_routine_execution_timestamp = time.time()
                                else:
                                    print(f"    CYCLE STATUS: LOSS / BROKEN SIGNAL\n")
                                    
                                print(f">>> Siklus Selesai. Melempar kembali pancingan baru dalam {self.allocation_sleep_delay} detik...")
                                if self.secure_sleep_interceptor(self.allocation_sleep_delay): continue 
                                    
                                self.handler.dispatch_tap(0x04) 
                                self.current_node_state = "NODE_1_SCANNING" 
                                self.purge_pipeline_buffers()
                                self.awaiting_node_start_time = time.time() 
                                process_text = "SCANNING ENGINE ACTIVE"
                                if self.secure_sleep_interceptor(1.0): continue

                except Exception as inner_error:
                    if self.verbosity_log_active:
                        print(f"\n[⚠️ Inner Error] Logic execution context failure: {inner_error}")

        except KeyboardInterrupt:
            pass
        except Exception as global_fatal_error:
            print(f"\n[🚨 CRITICAL ENGINE RECOVERY] Fatal initialization fault: {global_fatal_error}")
            time.sleep(8.0)
        finally:
            if self.output_to_console:
                print("\n[*] De-allocating hardware resources and releasing DXGI hooks...")
                
            try:
                self.handler.trigger_up_event() 
                if hasattr(self, 'dx_capture_session') and self.dx_capture_session is not None:
                    self.dx_capture_session.stop() 
                    if hasattr(self.dx_capture_session, 'device') and self.dx_capture_session.device is not None:
                        del self.dx_capture_session.device
                    del self.dx_capture_session
                    self.dx_capture_session = None
                if hasattr(dxcam, "Instance"):
                    dxcam.Instance = None
                print("[✅] Memory buffer cleared successfully. Thread safe to terminate.")
            except Exception as cleanup_error:
                if self.output_to_console:
                    print(f"[!] Error during hardware de-allocation: {cleanup_error}")
            sys.exit(0)

if __name__ == "__main__":
    console_mode_active = True
    if "--silent-mode" in sys.argv:
        console_mode_active = False

    bot = OperationalDataPipeline(output_to_console=console_mode_active)
    bot.run()
