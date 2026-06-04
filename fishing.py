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
        # Mengunci resolusi koordinat layar murni 1:1 agar interpolasi mouse tidak meleset
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
    """Spoofing RAM: Menulis dan menghapus data bytes acak di memori secara konstan 
    agar Signature Hash biner proses berubah setiap detak loop di mata pemindai anticheat"""
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
        # Humanized micro-jitter duration penekanan klik tunggal
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
        
        time.sleep(hold_duration + random.uniform(-0.003, 0.005)) # Jitter input keyboard
        
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

    # ==============================================================================
    # 3A. GAUSSIAN HUMANIZATION MOUSE ENGINE (KURVA TERBAIK ANTI-BOT DETECTION)
    # ==============================================================================
    def smooth_pointer_interpolation(self, target_x, target_y, steps=20, base_duration=0.20):
        """Menggerakkan kursor menggunakan Distribusi Gaussian Normal meniru getaran otot (tremor) tangan asli manusia"""
        origin_x, origin_y = self.query_pointer_position()
        delta_x = target_x - origin_x
        delta_y = target_y - origin_y
        
        dynamic_steps = steps + random.randint(-1, 3)
        dynamic_duration = base_duration + random.uniform(-0.02, 0.04)
        sleep_interval = dynamic_duration / dynamic_steps
        
        for idx in range(1, dynamic_steps + 1):
            progress = idx / dynamic_steps
            smooth_progress = progress * progress * (3 - 2 * progress) # S-Curve Base
            
            current_target_x = origin_x + (delta_x * smooth_progress)
            current_target_y = origin_y + (delta_y * smooth_progress)
            
            # Faktor getaran tangan mengecil secara bertahap (linier) saat kursor mendekati target akhir
            scale_factor = (1.0 - progress) * 2.5
            jitter_x = np.random.normal(0, scale_factor)
            jitter_y = np.random.normal(0, scale_factor)
            
            final_x = int(current_target_x + jitter_x)
            final_y = int(current_target_y + jitter_y)
            
            ctypes.windll.user32.SetCursorPos(final_x, final_y)
            time.sleep(sleep_interval)


# ==============================================================================
# 4. MAIN DATA STREAM PIPELINE (Anti-Heuristic System Architecture)
# ==============================================================================
class OperationalDataPipeline:
    def __init__(self, output_to_console=True):
        self.handler = IOStreamController()
        self.output_to_console = output_to_console
        self.initialize_configuration_profile()
        
        self.capture_bounds = (
            int(600 * self.scale_factor_x), 
            int(250 * self.scale_factor_y), 
            int(1200 * self.scale_factor_x), 
            int(900 * self.scale_factor_y)
        )
        self.dx_capture_session = dxcam.create(output_color="BGR")
        self.dx_capture_session.start(target_fps=self.pipeline_fps, region=self.capture_bounds)
        
        time.sleep(1.0)
        
        self.lower_tier_g = np.array([0, 120, 165]) 
        self.upper_tier_g = np.array([50, 255, 255])
        self.lower_tier_w = np.array([0, 0, 160])
        self.upper_tier_w = np.array([179, 50, 255])
        
        self.current_node_state = "NODE_0_IDLE"
        self.verbosity_log_active = False
        self.sys_flag_8 = False
        self.routine_switch_active = False
        self.sys_flag_7 = False
        
        self.termination_protocol_active = False
        self.sys_flag_6 = False
        
        self.last_routine_execution_timestamp = time.time()
        self.awaiting_node_start_time = 0
        self.sequential_timeout_anomalies = 0
        self.last_terminal_flush_time = time.time() 

        self.purge_pipeline_buffers()

    def initialize_configuration_profile(self):
        base_dir = os.getcwd()
        
        config_path = os.path.join(base_dir, 'config.ini')
        parser = configparser.ConfigParser()

        if not os.path.exists(config_path):
            parser['ENGINE'] = {
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
            with open(config_path, 'w') as configfile:
                parser.write(configfile)

        parser.read(config_path)
        
        self.display_width = int(parser['ENGINE'].get('SCREEN_WIDTH', '1920'))
        self.display_height = int(parser['ENGINE'].get('SCREEN_HEIGHT', '1080'))
        
        self.pipeline_fps = int(parser['ENGINE'].get('TARGET_FPS', '120'))
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
            if self.handler.verify_hardware_state(0x58): # Hotkey 'X' Panic Interrupt
                return True
            time.sleep(0.05)
        return False

    def execute_interface_sync(self):
        self.handler.dispatch_tap(0x42) # Open Terminal F8
        time.sleep(0.5)                
        self.handler.write_buffer_sequence("fixui")   
        time.sleep(0.2)
        self.handler.dispatch_tap(0x1C) # Enter
        time.sleep(0.6)                
        self.handler.dispatch_tap(0x42) # Close Terminal F8
        time.sleep(0.8)                

    def force_pipeline_shutdown(self):
        if self.output_to_console:
            print("\n[🚨] CRITICAL RECOVERY EXHAUSTED: SEVERING RESOURCE LINKS...")
        self.handler.trigger_up_event()
        
        self.handler.dispatch_tap(0x42) 
        time.sleep(0.4)
        self.handler.write_buffer_sequence("quit")    
        self.handler.dispatch_tap(0x1C) 
        
        time.sleep(1.0)
        self.dx_capture_session.stop()
        os._exit(0) 

    def dispatch_payload_collection(self):
        # Pengacak mikro konstan (+10ms - +30ms) agar mouse tetap sinkron sempurna dengan UI game Anda
        time.sleep(0.8 + random.uniform(0.01, 0.03)) 
        base_x = random.randint(800, 850)
        base_y = random.randint(920, 940)
        target_abs_x = int(base_x * self.scale_factor_x)
        target_abs_y = int(base_y * self.scale_factor_y)
        
        # Eksekusi pergerakan kurva biologis manusia (Gaussian)
        self.handler.smooth_pointer_interpolation(target_abs_x, target_abs_y, steps=20, base_duration=0.20)
        time.sleep(random.uniform(0.1, 0.15)) 
        self.handler.execute_single_signal()

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
        timestamp_now = time.time()
        if timestamp_now - self.last_terminal_flush_time > 0.35: 
            mt_flag = "ACTIVE" if self.routine_switch_active else "STABLE"
            term_flag = "ARMED" if self.termination_protocol_active else "STANDBY"
            sys.stdout.write(f"\r[STATUS] Node: {self.current_node_state:<22} | Operation: {process_text:<45} | Routine: {mt_flag} | Protection: {term_flag}")
            sys.stdout.flush()
            self.last_terminal_flush_time = timestamp_now

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
        print("[3] - Manual Inject Sync Thread Input")
        print("[X] - Instant Hardware Panic Breakpoint Rollback")
        print("==================================================")

    def run(self):
        self.print_initialization_manifest()
        try:
            while True:
                if self.handler.verify_hardware_state(0x39): break # Key '9' Safe Exit
                
                if self.handler.verify_hardware_state(0x38): # Key '8'
                    if not self.sys_flag_8:
                        self.verbosity_log_active = not self.verbosity_log_active
                        self.sys_flag_8 = True
                else:
                    self.sys_flag_8 = False

                if self.handler.verify_hardware_state(0x37): # Key '7'
                    if not self.sys_flag_7:
                        self.routine_switch_active = not self.routine_switch_active
                        self.sys_flag_7 = True
                else:
                    self.sys_flag_7 = False

                if self.handler.verify_hardware_state(0x36): # Key '6'
                    if not self.sys_flag_6:
                        self.termination_protocol_active = not self.termination_protocol_active
                        self.sys_flag_6 = True
                else:
                    self.sys_flag_6 = False

                if self.handler.verify_hardware_state(0x58): # Key 'X' Reset Breakpoint
                    if self.current_node_state != "NODE_0_IDLE":
                        self.handler.trigger_up_event() 
                        self.current_node_state = "NODE_0_IDLE"
                        self.purge_pipeline_buffers()
                        self.sequential_timeout_anomalies = 0
                        time.sleep(0.5) 
                        continue 

                frame_packet = self.dx_capture_session.get_latest_frame()
                if frame_packet is None: 
                    time.sleep(0.002)
                    continue
                process_text = "STANDBY_METRIC"

                self.sys_allocate_polymorphic_buffer() # Mutasi alokasi RAM konstan setiap siklus loop

                try:
                    if self.current_node_state == "NODE_0_IDLE":
                        process_text = "Awaiting physical inject activation trigger '3'..."
                        if self.handler.verify_hardware_state(0x33): # Key '3'
                            self.current_node_state = "NODE_1_SCANNING"
                            self.awaiting_node_start_time = time.time() 
                            self.sequential_timeout_anomalies = 0
                            time.sleep(1.0) 

                    elif self.current_node_state == "NODE_1_SCANNING":
                        if time.time() - self.awaiting_node_start_time > self.max_timeout_threshold: 
                            self.sequential_timeout_anomalies += 1 
                            
                            if self.sequential_timeout_anomalies == 1:
                                self.handler.dispatch_tap(0x04) # Tap 3 Re-cast
                                self.awaiting_node_start_time = time.time()
                                time.sleep(1.5)
                                continue
                                
                            elif self.sequential_timeout_anomalies == 2:
                                self.execute_interface_sync() 
                                self.handler.dispatch_tap(0x04) 
                                self.awaiting_node_start_time = time.time()
                                time.sleep(1.5)
                                continue
                                
                            elif self.sequential_timeout_anomalies == 3:
                                self.handler.dispatch_tap(0x04) 
                                self.awaiting_node_start_time = time.time()
                                time.sleep(1.5)
                                continue
                                
                            elif self.sequential_timeout_anomalies == 4:
                                self.execute_interface_sync() 
                                self.handler.dispatch_tap(0x04) 
                                self.awaiting_node_start_time = time.time()
                                time.sleep(1.5)
                                continue
                                
                            elif self.sequential_timeout_anomalies == 5:
                                self.handler.dispatch_tap(0x04) 
                                self.awaiting_node_start_time = time.time()
                                time.sleep(1.5)
                                continue

                            elif self.sequential_timeout_anomalies >= 6:
                                if self.termination_protocol_active:
                                    self.force_pipeline_shutdown()
                                else:
                                    self.handler.trigger_up_event()
                                    self.current_node_state = "NODE_0_IDLE"
                                    self.purge_pipeline_buffers()
                                    self.sequential_timeout_anomalies = 0 
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
                                    # ------------------------------------------------------------------
                                    # KUNCI TIMING FIX: MEMPERTAHANKAN JEDA EMAS 200MS MICRO-FUZZED
                                    # ------------------------------------------------------------------
                                    self.handler.execute_single_signal() # Klik pemicu masuk
                                    
                                    # Rentang mikro-jitter 205ms - 215ms untuk melompati blank frame LUA
                                    time.sleep(0.2 + random.uniform(0.005, 0.015)) 
                                    
                                    self.sequential_timeout_anomalies = 0 
                                    self.purge_pipeline_buffers()
                                    self.current_node_state = "NODE_2_STREAM_PROCESSING"
                                    self.phase3_start_time = time.time() 
                                    self.last_frame_verification_time = time.time() 
                                else:
                                    process_text = f"FILTER_NOISE_OVERRIDE (W:{w_b} H:{h_b})"

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
                                    self.stagnant_frame_accumulation = 0

                            CEILING_ALERT_ENTER = self.LIMIT_G - int(5  * self.scale_factor_y)
                            CEILING_ALERT_EXIT  = self.LIMIT_G - int(135 * self.scale_factor_y) 
                            
                            if current_g_h >= CEILING_ALERT_ENTER: self.recovery_bypass_active = True
                            elif current_g_h <= CEILING_ALERT_EXIT: self.recovery_bypass_active = False

                            if self.recovery_bypass_active:
                                self.state_cooldown_active = True
                                forced_fallback_active = True
                                floor_override_active = False
                                self.stagnant_frame_accumulation = 0

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
                            
                            # ------------------------------------------------------------------
                            # KUNCI TIMING FIX: INITIAL PULL BERTAHAN DI 2 DETIK FLUKTUATIF MIKRO
                            # ------------------------------------------------------------------
                            fuzzed_pull_limit = 2.0 + random.uniform(-0.04, 0.03) # 1.96 - 2.03 Detik
                            
                            if pipeline_active_duration < fuzzed_pull_limit and self.peak_buffer_w_h < int(10 * self.scale_factor_y):
                                self.handler.trigger_down_event()
                                process_text = "INITIAL PACKET INTEGRATION ROUTINE"
                            elif self.stream_ever_validated and verification_loss_duration < 0.6:
                                self.handler.trigger_up_event() 
                                self.state_cooldown_active = True 
                                process_text = "CARRIER FLICKER FRAME INTERPOLATION"
                            else:
                                self.handler.trigger_up_event()
                                self.current_node_state = "NODE_0_IDLE"
                                
                                # Siklus Minigame Berakhir
                                if self.peak_buffer_w_h >= self.VAL_THRESHOLD: 
                                    self.dispatch_payload_collection() # Eksekusi pergerakan mouse otomatis
                                    
                                    if self.routine_switch_active and (time.time() - self.last_routine_execution_timestamp) >= (self.routine_delay_interval * 60):
                                        fuzzed_sleep = self.allocation_sleep_delay + random.uniform(0.05, 0.15)
                                        if self.secure_sleep_interceptor(fuzzed_sleep): continue
                                        self.execute_maintenance_sequence()
                                        self.last_routine_execution_timestamp = time.time()
                                
                                # ------------------------------------------------------------------
                                # KUNCI TIMING FIX: PENGACAK RECAST DELAY AMAN DAN RAPID
                                # ------------------------------------------------------------------
                                fuzzed_reconnect_delay = self.allocation_sleep_delay + random.uniform(0.04, 0.15)
                                if self.secure_sleep_interceptor(fuzzed_reconnect_delay): continue 
                                    
                                self.handler.dispatch_tap(0x04) # Lemparkan kembali pancingan (Tap 3)
                                self.current_node_state = "NODE_1_SCANNING" 
                                self.purge_pipeline_buffers()
                                self.awaiting_node_start_time = time.time() 
                                if self.secure_sleep_interceptor(1.0): continue

                except Exception as inner_error:
                    pass

                if self.verbosity_log_active:
                    self.print_pipeline_statistics(process_text)

        except KeyboardInterrupt:
            pass
        finally:
            self.handler.trigger_up_event()
            self.dx_capture_session.stop()
            os._exit(0)

if __name__ == "__main__":
    console_mode_active = True
    if "--silent-mode" in sys.argv:
        console_mode_active = False

    bot = OperationalDataPipeline(output_to_console=console_mode_active)
    bot.run()
