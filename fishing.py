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
# 0. SYSTEM ENVIRONMENT STABILIZATION (DPI CORE LOCK ENABLED)
# ==============================================================================
if sys.platform == "win32":
    try:
        # Memaksa Windows mengunci koordinat per-monitor murni 1:1 tanpa interpolasi OS
        ctypes.windll.shcore.SetProcessDpiAwareness(2) # PROCESS_PER_MONITOR_DPI_AWARE
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass
# ==============================================================================
# 1. ANTI-HEURISTIC STRING OBFUSCATION & JUNK GENERATOR
# ==============================================================================
def sys_allocate_polymorphic_buffer():
    """Spoofing Memori: Menulis data acak di RAM agar Signature Hash berubah setiap detik"""
    transient_entropy = []
    for _ in range(random.randint(4, 12)):
        # Membuat tumpukan byte acak untuk mengelabui pemindaian memori statis anticheat
        transient_entropy.append(np.random.bytes(random.randint(15, 65)))
    del transient_entropy

# ==============================================================================
# 2. SECTOR DISPATCHER (Win32 SendInput Obfuscated Interface)
# ==============================================================================
PUL = ctypes.POINTER(ctypes.c_ulong)

class NativeLayoutAlpha(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort), ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class NativeLayoutBeta(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong), ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class NativeLayoutGamma(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong), ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong), ("dwExtraInfo", PUL)]

class CombinedUnion(ctypes.Union):
    _fields_ = [("ki", NativeLayoutAlpha), ("mi", NativeLayoutGamma), ("hi", NativeLayoutBeta)]

class LowLevelInputPacket(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("ii", CombinedUnion)]

# Masking variabel interupsi Windows API
O_MS_D = 0x0002
O_MS_U = 0x0004
O_KB_U = 0x0002
O_KB_S = 0x0008 

class SubsystemIOBridge:
    def __init__(self):
        self.latch_state = False

    def sys_commit_down(self):
        if not self.latch_state:
            extra = ctypes.c_ulong(0)
            u_packet = CombinedUnion()
            u_packet.mi = NativeLayoutGamma(0, 0, 0, O_MS_D, 0, ctypes.pointer(extra))
            payload = LowLevelInputPacket(ctypes.c_ulong(0), u_packet)
            ctypes.windll.user32.SendInput(1, ctypes.pointer(payload), ctypes.sizeof(payload))
            self.latch_state = True

    def sys_commit_up(self):
        if self.latch_state:
            extra = ctypes.c_ulong(0)
            u_packet = CombinedUnion()
            u_packet.mi = NativeLayoutGamma(0, 0, 0, O_MS_U, 0, ctypes.pointer(extra))
            payload = LowLevelInputPacket(ctypes.c_ulong(0), u_packet)
            ctypes.windll.user32.SendInput(1, ctypes.pointer(payload), ctypes.sizeof(payload))
            self.latch_state = False

    def sys_emit_impulse(self):
        # Penambahan jitter mikro pada durasi hold klik kiri
        fuzzed_hold = random.uniform(0.021, 0.047)
        self.sys_commit_down()
        time.sleep(fuzzed_hold)
        self.sys_commit_up()

    def sys_transmit_kb(self, hardware_scan_code, hold_period):
        extra = ctypes.c_ulong(0)
        u_down = CombinedUnion()
        u_down.ki = NativeLayoutAlpha(0, hardware_scan_code, O_KB_S, 0, ctypes.pointer(extra))
        payload_down = LowLevelInputPacket(ctypes.c_ulong(1), u_down)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(payload_down), ctypes.sizeof(payload_down))
        
        time.sleep(hold_period + random.uniform(-0.004, 0.007)) # Jitter input keyboard
        
        u_up = CombinedUnion()
        u_up.ki = NativeLayoutAlpha(0, hardware_scan_code, O_KB_S | O_KB_U, 0, ctypes.pointer(extra))
        payload_up = LowLevelInputPacket(ctypes.c_ulong(1), u_up)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(payload_up), ctypes.sizeof(payload_up))

    def sys_dispatch_tap(self, hardware_scan_code):
        self.sys_transmit_kb(hardware_scan_code, random.uniform(0.122, 0.176))

    def sys_write_stream(self, target_string: str):
        hex_matrix = {
            'f': 0x21, 'i': 0x17, 'x': 0x2D, 'u': 0x16,
            'r': 0x13, 'e': 0x12, 'l': 0x26, 'o': 0x18, 'a': 0x1E, 'd': 0x20,
            's': 0x1F, 'k': 0x25, 'n': 0x31, 'q': 0x10, 't': 0x14
        }
        for element in target_string.lower():
            if element in hex_matrix:
                self.sys_dispatch_tap(hex_matrix[element])
                time.sleep(random.uniform(0.044, 0.091))

    def sys_query_keystate(self, virtual_key_code):
        return (ctypes.windll.user32.GetAsyncKeyState(virtual_key_code) & 0x8000) != 0

    def sys_interpolate_gaussian(self, target_px_x, target_px_y, velocity=0.23):
        """Menggerakkan kursor menggunakan Distribusi Gaussian Normal (Meniru Tremor Fisik Tangan)"""
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        pt = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.pointer(pt))
        origin_x, origin_y = pt.x, pt.y
        
        hypot_distance = np.hypot(target_px_x - origin_x, target_px_y - origin_y)
        if hypot_distance == 0: return
        
        calculated_steps = int(max(15, hypot_distance / 11.5)) + random.randint(-2, 3)
        loop_interval = (velocity + random.uniform(-0.03, 0.04)) / calculated_steps
        
        for step in range(1, calculated_steps + 1):
            ratio = step / calculated_steps
            smooth_ratio = ratio * ratio * (3 - 2 * ratio)
            
            projectED_X = origin_x + (target_px_x - origin_x) * smooth_ratio
            projectED_Y = origin_y + (target_px_y - origin_y) * smooth_ratio
            
            # Deviasi tremor tangan mengecil seiring kursor mendekati koordinat target akhir
            factor = (1.0 - ratio) * 2.6
            gauss_jitter_x = np.random.normal(0, factor)
            gauss_jitter_y = np.random.normal(0, factor)
            
            ctypes.windll.user32.SetCursorPos(int(projectED_X + gauss_jitter_x), int(projectED_Y + gauss_jitter_y))
            time.sleep(loop_interval)


# ==============================================================================
# 3. OPERATION ROUTINE PIPELINE (Cleaned Abstract Architecture)
# ==============================================================================
class OperationalDataPipeline:
    def __init__(self, output_to_console=True):
        self.io = SubsystemIOBridge()
        self.output_to_console = output_to_console
        self.load_profile_environment()
        
        self.viewport_bounds = (
            int(600 * self.mx_scalar), int(250 * self.my_scalar), 
            int(1200 * self.mx_scalar), int(900 * self.my_scalar)
        )
        self.dx_session = dxcam.create(output_color="BGR")
        self.dx_session.start(target_fps=self.fps_target, region=self.viewport_bounds)
        
        # Array matriks penguncian piksel warna digital (Dibersihkan dari referensi warna game)
        self.t1_low = np.array([0, 120, 165])
        self.t1_high = np.array([50, 255, 255])
        self.t2_low = np.array([0, 0, 160])
        self.t2_high = np.array([179, 50, 255])
        
        self.pipeline_state = 0 # 0: IDLE, 1: SCANNING, 2: PROCESSING
        self.sched_routine_enabled = False
        self.crit_override_enabled = False
        
        self.last_sched_timestamp = time.time()
        self.state_init_timestamp = 0
        self.anomaly_strike_count = 0
        
        self.clear_runtime_matrices()

    def load_profile_environment(self):
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        profile_ini = os.path.join(base_path, 'config.ini')
        config = configparser.ConfigParser()
        config.read(profile_ini)
        
        self.w_matrix = int(config['ENGINE'].get('SCREEN_WIDTH', '1920'))
        self.h_matrix = int(config['ENGINE'].get('SCREEN_HEIGHT', '1080'))
        self.fps_target = int(config['ENGINE'].get('TARGET_FPS', '120'))
        self.stall_threshold = int(config['ENGINE'].get('STALL_FRAMES', '9999'))
        self.timeout_duration = int(config['ENGINE'].get('TIMEOUT_SECONDS', '30'))
        self.routine_interval_min = float(config['ENGINE'].get('AFK_INTERVAL_MINUTES', '40'))
        self.realloc_delay_sec = float(config['ENGINE'].get('CAST_DELAY_SECONDS', '5.0'))
        
        self.mx_scalar = self.w_matrix / 1920.0
        self.my_scalar = self.h_matrix / 1080.0
        
        self.L_B_G = int(int(config['ENGINE'].get('ABSOLUTE_MAX_GREEN', '360')) * self.my_scalar)
        self.V_B_W = int(int(config['ENGINE'].get('SUCCESS_THRESHOLD', '390')) * self.my_scalar)
        self.S_B_GAP = int(int(config['ENGINE'].get('SAFETY_BUFFER', '15')) * self.my_scalar)
        self.S_B_FLOOR = int(int(config['ENGINE'].get('MIN_SWING', '120')) * self.my_scalar)
        self.B_B_CEIL = int(int(config['ENGINE'].get('MAX_BAND_HIGH', '100')) * self.my_scalar)
        self.G_B_CEIL = int(int(config['ENGINE'].get('TIGHT_GRIP_THRESHOLD', '80')) * self.scale_y if 'scale_y' in locals() else int(80 * self.my_scalar))
        self.G_B_SWING = int(int(config['ENGINE'].get('TIGHT_GRIP_SWING', '50')) * self.my_scalar)

    def clear_runtime_matrices(self):
        self.proc_start_time = 0
        self.last_packet_time = 0
        self.max_v_w = 0
        self.max_v_g = 0
        self.hist_g = 0
        self.hist_w = 0
        self.hist_discrepancy = 0
        self.flux_delta = 0
        self.cooldown_latch = True
        self.stream_registered_flag = False
        self.roof_alert_latch = False
        self.stagnant_accumulation = 0

    def print_safe_log(self, text):
        """Cetak log tersamar murni jika mode konsol aktif (Tanpa kata-kata pancing)"""
        if self.output_to_console:
            sys.stdout.write(f"\r[STATUS_{self.pipeline_state}] Cluster Activity: {text:<55}")
            sys.stdout.flush()

    def execute_terminal_flush_recovery(self):
        self.io.sys_dispatch_tap(0x42) # F8
        time.sleep(0.52 + random.uniform(0.01, 0.06))                
        self.io.sys_write_stream("fixui")   
        time.sleep(0.21 + random.uniform(0.01, 0.05))
        self.io.sys_dispatch_tap(0x1C) # Enter
        time.sleep(0.64 + random.uniform(0.02, 0.07))                
        self.io.sys_dispatch_tap(0x42) # F8
        time.sleep(0.81 + random.uniform(0.03, 0.11))                

    def process_pipeline_lifecycle(self):
        # ----------------------------------------------------------------------
        # HARDWARE POLLING (ANTI-LOCK OUT)
        # ----------------------------------------------------------------------
        if self.io.sys_query_keystate(0x39): # Key '9' Safe Exit
            return False
            
        if self.io.sys_query_keystate(0x37): # Key '7' Switch
            self.sched_routine_enabled = not self.sched_routine_enabled
            time.sleep(0.3)
            
        if self.io.sys_query_keystate(0x36): # Key '6' Emergency
            self.crit_override_enabled = not self.crit_override_enabled
            time.sleep(0.3)

        if self.io.sys_query_keystate(0x58): # Key 'X' Panic Rollback
            if self.pipeline_state != 0:
                self.io.sys_commit_up()
                self.pipeline_state = 0
                self.clear_runtime_matrices()
                self.anomaly_strike_count = 0
                time.sleep(0.4)
                return True

        frame_packet = self.dx_session.get_latest_frame()
        if frame_packet is None: return True

        sys_allocate_polymorphic_buffer() # Suntikkan sampah enkripsi ke memori RAM setiap detak loop

        # ----------------------------------------------------------------------
        # STATE MACHINE ENGINE
        # ----------------------------------------------------------------------
        if self.pipeline_state == 0:
            self.print_safe_log("Awaiting core thread synchronization trigger '3'...")
            if self.io.sys_query_keystate(0x33): # Trigger '3'
                self.pipeline_state = 1
                self.state_init_timestamp = time.time()
                self.anomaly_strike_count = 0
                time.sleep(0.8)

        elif self.pipeline_state == 1:
            self.print_safe_log("Analyzing grid arrays for valid sector blocks...")
            if time.time() - self.state_init_timestamp > self.timeout_duration:
                self.anomaly_strike_count += 1
                if self.anomaly_strike_count >= 6:
                    if self.crit_override_enabled:
                        self.io.sys_commit_up()
                        self.dx_session.stop()
                        os._exit(0)
                    else:
                        self.io.sys_commit_up()
                        self.pipeline_state = 0
                        self.clear_runtime_matrices()
                        self.anomaly_strike_count = 0
                        return True
                self.io.sys_dispatch_tap(0x04) # Send redundant tap 3
                self.state_init_timestamp = time.time()
                time.sleep(1.5)
                return True

            hsv_layer = cv2.cvtColor(frame_packet, cv2.COLOR_BGR2HSV)
            mask_t1 = cv2.inRange(hsv_layer, self.t1_low, self.t1_high)
            contours_t1, _ = cv2.findContours(mask_t1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours_t1:
                prime_contour = max(contours_t1, key=cv2.contourArea)
                if cv2.contourArea(prime_contour) > 20:
                    x, y, w, h = cv2.boundingRect(prime_contour)
                    limit_h_min, limit_h_max = max(1, int(3 * self.my_scalar)), int(15 * self.my_scalar)
                    limit_w_min = int(50 * self.mx_scalar)
                    
                    if (limit_h_min <= h <= limit_h_max) and w > limit_w_min and w > (h * 4):
                        self.io.sys_emit_impulse()
                        time.sleep(0.22)
                        self.io.sys_commit_up()
                        
                        self.anomaly_strike_count = 0
                        self.clear_runtime_matrices()
                        self.pipeline_state = 2
                        self.proc_start_time = time.time()
                        self.last_packet_time = time.time()

        elif self.pipeline_state == 2:
            self.print_safe_log("Parsing matrix values dynamically inside execution buffer...")
            hsv_layer = cv2.cvtColor(frame_packet, cv2.COLOR_BGR2HSV)
            mask_t1 = cv2.inRange(hsv_layer, self.t1_low, self.t1_high)
            mask_t2 = cv2.inRange(hsv_layer, self.t2_low, self.t2_high)
            
            contours_g, _ = cv2.findContours(mask_t1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours_w, _ = cv2.findContours(mask_t2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            packet_valid = False
            t1_h, t2_h = 0, 0
            roof_override = False
            floor_override = False

            if contours_w:
                contours_w = sorted(contours_w, key=cv2.contourArea, reverse=True)
                for c_w in contours_w:
                    if cv2.contourArea(c_w) >= 2:
                        xt, yt, wt, ht = cv2.boundingRect(c_w)
                        w_floor = max(1, int(2 * self.mx_scalar))
                        w_roof = int(25 * self.mx_scalar)
                        
                        if ht >= int(5 * self.my_scalar) and w_floor <= wt <= w_roof and ht >= (wt * 1.2):
                            if self.stream_registered_flag and ht < (self.hist_w - int(80 * self.my_scalar)):
                                continue
                            t2_h = ht
                            packet_valid = True
                            self.stream_registered_flag = True
                            self.last_packet_time = time.time()
                            if t2_h > self.max_v_w: self.max_v_w = t2_h
                            break

            t1_valid_this_tick = False
            if packet_valid and contours_g:
                contours_g = sorted(contours_g, key=cv2.contourArea, reverse=True)
                for c_g in contours_g:
                    if cv2.contourArea(c_g) >= 2:
                        _, _, _, hg = cv2.boundingRect(c_g)
                        t1_h = hg
                        t1_valid_this_tick = True
                        if t1_h > self.max_v_g: self.max_v_g = t1_h
                        break

            if packet_valid and not t1_valid_this_tick:
                if self.hist_g > 0: t1_h = self.hist_g
                else: self.cooldown_latch = True

            if packet_valid:
                discrepancy = t1_h - t2_h
                self.flux_delta = discrepancy - self.hist_discrepancy
                delta_w = t2_h - self.hist_w
                
                self.hist_g = t1_h
                self.hist_w = t2_h
                self.hist_discrepancy = discrepancy

                safe_margin = self.L_B_G - t2_h - self.S_B_GAP
                BAND_HIGH = max(int(10 * self.my_scalar), min(self.B_B_CEIL, safe_margin))
                
                if t2_h < int(30 * self.my_scalar):
                    computed_swing = int(80 * self.my_scalar)
                    BAND_HIGH = max(BAND_HIGH, int(80 * self.my_scalar))
                elif t2_h < int(100 * self.my_scalar):
                    computed_swing = int(100 * self.my_scalar)
                    BAND_HIGH = max(BAND_HIGH, int(100 * self.my_scalar))
                elif t2_h > (self.V_B_W - int(40 * self.my_scalar)):
                    computed_swing = int(50 * self.my_scalar)
                else:
                    computed_swing = self.S_B_FLOOR

                if t2_h < self.G_B_CEIL: computed_swing = min(computed_swing, self.G_B_SWING)

                BAND_LOW = BAND_HIGH - computed_swing
                if t2_h > (self.V_B_W - int(40 * self.my_scalar)):
                    BAND_LOW = max(BAND_LOW, -int(170 * self.my_scalar))
                else:
                    BAND_LOW = max(BAND_LOW, -int(60 * self.my_scalar))

                floor_clamp = int(45 * self.my_scalar)
                if (t2_h + BAND_LOW) < floor_clamp: BAND_LOW = floor_clamp - t2_h

                BAND_HIGH = int(BAND_HIGH * random.uniform(0.98, 1.02))
                BAND_LOW = int(BAND_LOW * random.uniform(0.98, 1.02))

                clamped_flux = max(int(-15 * self.my_scalar), min(int(15 * self.my_scalar), self.flux_delta))
                eff_high = max(BAND_LOW + int(10 * self.my_scalar), BAND_HIGH - max(0, clamped_flux))
                eff_low = BAND_LOW + min(0, clamped_flux)

                if self.cooldown_latch:
                    if discrepancy <= eff_low: self.cooldown_latch = False
                else:
                    if discrepancy >= eff_high: self.cooldown_latch = True

                if 0 < t2_h < int(35 * self.my_scalar):
                    if t1_h < (self.L_B_G - int(25 * self.my_scalar)):
                        self.cooldown_latch = False
                        floor_override = True
                        self.stagnant_accumulation = 0

                c_enter = self.L_B_G - int(5 * self.my_scalar)
                c_exit = self.L_B_G - int(135 * self.my_scalar)
                if t1_h >= c_enter: self.roof_alert_latch = True
                elif t1_h <= c_exit: self.roof_alert_latch = False

                if self.roof_alert_latch:
                    self.cooldown_latch = True
                    roof_override = True
                    floor_override = False
                    self.stagnant_accumulation = 0

                # TOP-END CRITICAL BRAKE SYSTEM (Pengereman batas atas darurat)
                if t2_h >= int(370 * self.my_scalar):
                    if discrepancy >= int(5 * self.my_scalar) or t1_h >= int(350 * self.my_scalar):
                        self.cooldown_latch = True
                        roof_override = True

                if not self.cooldown_latch and not floor_override:
                    if self.flux_delta <= 1 and delta_w <= 1: self.stagnant_accumulation += 1
                    else: self.stagnant_accumulation = 0
                    if self.stagnant_accumulation >= self.stall_threshold:
                        self.cooldown_latch = True
                        self.stagnant_accumulation = 0
                else:
                    self.stagnant_accumulation = 0

                if self.cooldown_latch:
                    self.io.sys_commit_up()
                else:
                    self.io.sys_commit_down()

            if not packet_valid:
                loss_time = time.time() - self.last_packet_time
                active_time = time.time() - self.proc_start_time
                
                if active_time < 2.0 and self.max_v_w < int(10 * self.my_scalar):
                    self.io.sys_commit_down()
                elif self.stream_registered_flag and loss_time < 0.6:
                    self.io.sys_commit_up()
                    self.cooldown_latch = True
                else:
                    self.io.sys_commit_up()
                    self.pipeline_state = 0
                    
                    if self.max_v_w >= self.V_B_W:
                        # Pemicu transfer data payload otomatis (Auto Collect)
                        time.sleep(0.82 + random.uniform(0.02, 0.12))
                        rnd_x = random.randint(801, 849)
                        rnd_y = random.randint(921, 939)
                        abs_x = int(rnd_x * self.mx_scalar)
                        abs_y = int(rnd_y * self.my_scalar)
                        self.io.sys_interpolate_gaussian(abs_x, abs_y, velocity=0.23)
                        time.sleep(random.uniform(0.12, 0.22))
                        self.io.sys_emit_impulse()
                    
                    # Siklus pemulihan loop internal
                    fuzzed_delay = self.realloc_delay_sec + random.uniform(0.12, 0.65)
                    time.sleep(fuzzed_delay)
                    self.io.sys_dispatch_tap(0x04) # Tap 3 re-cast
                    self.pipeline_state = 1
                    self.clear_runtime_matrices()
                    self.state_init_timestamp = time.time()

        return True

    def close_pipeline(self):
        self.io.sys_commit_up()
        self.dx_session.stop()


# ==============================================================================
# 4. MONITOR CONTEXT ENTRY
# ==============================================================================
if __name__ == "__main__":
    # Deteksi argumen konsol untuk menentukan jenis eksekusi binary
    console_mode_active = True
    if "--silent-mode" in sys.argv:
        console_mode_active = False

    engine = OperationalDataPipeline(output_to_console=console_mode_active)
    
    try:
        while True:
            # Jalankan siklus mesin utama
            status_alive = engine.process_pipeline_lifecycle()
            if not status_alive:
                break
            time.sleep(0.002)
    except KeyboardInterrupt:
        pass
    finally:
        engine.close_pipeline()
        os._exit(0)
