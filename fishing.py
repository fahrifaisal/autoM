import cv2
import numpy as np
import dxcam
import ctypes
import time
import random
import configparser
import os
import sys

# ==========================================
# 1. SETUP MICROSOFT SENDINPUT (MOUSE & KEYBOARD)
# ==========================================
PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008 

mouse_is_pressed = False

def safe_mouse_down():
    global mouse_is_pressed
    if not mouse_is_pressed:
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(INPUT_MOUSE), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        mouse_is_pressed = True

def safe_mouse_up():
    global mouse_is_pressed
    if mouse_is_pressed:
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_LEFTUP, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(INPUT_MOUSE), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        mouse_is_pressed = False

def single_click():
    duration = random.uniform(0.04, 0.07) 
    safe_mouse_down()
    time.sleep(duration)
    safe_mouse_up()

def hold_key_scancode(hexKeyCode, duration):
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

def tap_key_scancode(hexKeyCode):
    hold_key_scancode(hexKeyCode, random.uniform(0.1, 0.2))

def is_key_pressed(vk_code):
    return (ctypes.windll.user32.GetAsyncKeyState(vk_code) & 0x8000) != 0

def get_cursor_pos():
    class POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.pointer(pt))
    return pt.x, pt.y

def smooth_move_mouse(target_x, target_y, steps=20, duration=0.25):
    start_x, start_y = get_cursor_pos()
    dx = target_x - start_x
    dy = target_y - start_y
    sleep_time = duration / steps
    for i in range(1, steps + 1):
        curr_x = int(start_x + (dx * i / steps))
        curr_y = int(start_y + (dy * i / steps))
        ctypes.windll.user32.SetCursorPos(curr_x, curr_y)
        time.sleep(sleep_time)

def auto_collect_fish(scale_x, scale_y):
    print("\n>>> TARGET TERCAPAI! Mengeksekusi Auto-Collect...")
    time.sleep(0.8) 
    base_x = random.randint(800, 850)
    base_y = random.randint(920, 940)
    collect_x = int(base_x * scale_x)
    collect_y = int(base_y * scale_y)
    smooth_move_mouse(collect_x, collect_y)
    time.sleep(random.uniform(0.1, 0.2)) 
    single_click()
    print(f">>> Auto-Collect Selesai di (X:{collect_x}, Y:{collect_y}).\n")

def perform_afk_routine():
    print("\n>>> [AFK ROUTINE] Memulai Anti-AFK & Makan/Minum...")
    print(">>> Menahan [D] selama 2 detik...")
    hold_key_scancode(0x20, 2.0)
    print(">>> Menahan [A] selama 2 detik...")
    hold_key_scancode(0x1E, 2.0)
    print(">>> Menahan [W] selama 1.0 detik...")
    hold_key_scancode(0x11, 1.0)
    print(">>> Makan (Tekan 4), jeda 6 detik...")
    tap_key_scancode(0x05)
    time.sleep(6.0)
    print(">>> Minum (Tekan 5), jeda 6 detik...")
    tap_key_scancode(0x06)
    time.sleep(6.0)
    print(">>> [AFK ROUTINE] Selesai.\n")

# ==========================================
# 2. LOGIKA UTAMA BOT PANCING
# ==========================================
def run_fishing_bot():
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
            'ABSOLUTE_MAX_GREEN': '400',   # [DIPERBAIKI] Dinaikkan dari 380 ke 400 agar kuat menampung bar putih 405px
            'SUCCESS_THRESHOLD': '380',    # [BARU] Batas riwayat max_white untuk deklarasi Sukses
            'SAFETY_BUFFER': '15',
            'MAX_BAND_HIGH': '100',
            'MIN_SWING': '120',
            'TIGHT_GRIP_THRESHOLD': '80',
            'TIGHT_GRIP_SWING': '50',
            'TIMEOUT_SECONDS': '60',
            'AFK_INTERVAL_MINUTES': '40'
        }
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)

    config.read(config_file_path)
    
    SCREEN_WIDTH = int(config['ENGINE'].get('SCREEN_WIDTH', '1920'))
    SCREEN_HEIGHT = int(config['ENGINE'].get('SCREEN_HEIGHT', '1080'))
    TIMEOUT_SECONDS = int(config['ENGINE'].get('TIMEOUT_SECONDS', '60'))
    AFK_INTERVAL_MINUTES = float(config['ENGINE'].get('AFK_INTERVAL_MINUTES', '40'))
    
    scale_x = SCREEN_WIDTH / 1920.0
    scale_y = SCREEN_HEIGHT / 1080.0

    ABSOLUTE_MAX_GREEN = int(int(config['ENGINE'].get('ABSOLUTE_MAX_GREEN', '400')) * scale_y)
    SUCCESS_THRESHOLD = int(int(config['ENGINE'].get('SUCCESS_THRESHOLD', '380')) * scale_y)
    SAFETY_BUFFER = int(int(config['ENGINE'].get('SAFETY_BUFFER', '15')) * scale_y)
    MIN_SWING = int(int(config['ENGINE'].get('MIN_SWING', '120')) * scale_y)
    MAX_BAND_HIGH = int(int(config['ENGINE'].get('MAX_BAND_HIGH', '100')) * scale_y)
    TIGHT_GRIP_THRESHOLD = int(int(config['ENGINE'].get('TIGHT_GRIP_THRESHOLD', '80')) * scale_y)
    TIGHT_GRIP_SWING = int(int(config['ENGINE'].get('TIGHT_GRIP_SWING', '50')) * scale_y)

    left   = int(400 * scale_x)
    top    = int(200 * scale_y)
    right  = int(1600 * scale_x)
    bottom = int(1000 * scale_y)
    region = (left, top, right, bottom)
    
    camera = dxcam.create(output_color="BGR")
    camera.start(target_fps=60, region=region)
    
    state = "FASE_0_STANDBY"
    is_debug_mode = False
    debug_key_pressed = False
    afk_mode_enabled = False
    afk_key_pressed = False
    last_afk_time = time.time()
    
    phase3_start_time = 0
    last_seen_time = 0 
    fase1_start_time = 0 
    max_white_h = 0
    
    is_cooling_down = False 
    bar_ever_found = False 
    
    lower_grad = np.array([0, 120, 165]) 
    upper_grad = np.array([50, 255, 255])
    
    lower_white = np.array([0, 0, 160])
    upper_white = np.array([100, 100, 255])

    prev_grad_h = 0
    prev_white_h = 0
    prev_selisih = 0
    delta_selisih = 0

    print("========================================")
    print("      FISHING PIXEL BOT (OBFUSCATED)    ")
    print(" Logic: Historical Vanish Trigger       ")
    print("========================================")
    print(f"[CONFIG] Monitor : {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    print(f"[CONFIG] Max Grn : {ABSOLUTE_MAX_GREEN} | Sukses: >{SUCCESS_THRESHOLD}")
    print(f"[CONFIG] AFK Int : {AFK_INTERVAL_MINUTES} Menit")
    print("========================================")
    print("[8] - Toggle Live Debug View")
    print("[9] - Exit Program")
    print("[7] - TOGGLE AUTO-EAT/AFK MODE")
    print("[3] - MANUALLY START FISHING")
    print("[X] - PANIC BUTTON (Reset to Standby)")
    print("========================================")
    
    try:
        while True:
            if is_key_pressed(0x39): break 
            
            if is_key_pressed(0x38): 
                if not debug_key_pressed:
                    is_debug_mode = not is_debug_mode
                    if not is_debug_mode: cv2.destroyWindow("Live Debug")
                    debug_key_pressed = True
            else:
                debug_key_pressed = False

            if is_key_pressed(0x37): 
                if not afk_key_pressed:
                    afk_mode_enabled = not afk_mode_enabled
                    status = "ON" if afk_mode_enabled else "OFF"
                    print(f"\n[!] AUTO-EAT / AFK MODE: {status}")
                    afk_key_pressed = True
            else:
                afk_key_pressed = False

            if is_key_pressed(0x58): 
                if state != "FASE_0_STANDBY":
                    print("\n[!] INTERRUPT! Kembali ke Standby...")
                    safe_mouse_up() 
                    state = "FASE_0_STANDBY"
                    max_white_h = 0
                    time.sleep(0.5) 
                    continue 

            frame = camera.get_latest_frame()
            if frame is None: continue
                
            debug_frame = frame.copy() if is_debug_mode else None
            action_text = "IDLE"
            action_color = (255, 255, 255)

            if state == "FASE_0_STANDBY":
                action_text = "STANDBY: Tekan '3' untuk mulai..."
                action_color = (0, 255, 255) 
                
                if is_key_pressed(0x33):
                    print("\n>>> Memulai siklus pemantauan...")
                    state = "FASE_1_WAITING"
                    fase1_start_time = time.time() 
                    time.sleep(1.0) 

            elif state == "FASE_1_WAITING":
                if time.time() - fase1_start_time > TIMEOUT_SECONDS: 
                    print(f"\n[!] TIMEOUT: Tidak ada ikan setelah {TIMEOUT_SECONDS} detik.")
                    tap_key_scancode(0x04)
                    fase1_start_time = time.time() 
                    time.sleep(1.0) 
                    continue 

                hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                mask_grad = cv2.inRange(hsv_frame, lower_grad, upper_grad)
                contours, _ = cv2.findContours(mask_grad, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                if contours:
                    c = max(contours, key=cv2.contourArea)
                    if cv2.contourArea(c) > 20: 
                        x, y, w, h = cv2.boundingRect(c)
                        
                        min_h = max(1, int(3 * scale_y))
                        max_h = int(15 * scale_y)
                        min_w = int(50 * scale_x) 
                        
                        if (min_h <= h <= max_h) and w > min_w and w > (h * 4):
                            action_text = "FASE 2 DETECTED! HOOKING..."
                            single_click()
                            
                            time.sleep(0.1) 
                            safe_mouse_up() 
                            
                            is_cooling_down = True 
                            bar_ever_found = False 
                            max_white_h = 0
                            prev_grad_h = 0
                            prev_white_h = 0
                            prev_selisih = 0
                            delta_selisih = 0
                            
                            state = "FASE_3_MINIGAME"
                            phase3_start_time = time.time() 
                            last_seen_time = time.time() 
                        else:
                            action_text = f"NOISE REJ (W:{w} H:{h})"

            elif state == "FASE_3_MINIGAME":
                hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                mask_grad = cv2.inRange(hsv_frame, lower_grad, upper_grad)
                mask_white = cv2.inRange(hsv_frame, lower_white, upper_white)
                
                contours_g, _ = cv2.findContours(mask_grad, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                contours_w, _ = cv2.findContours(mask_white, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                valid_bar_found = False
                grad_h = 0
                white_h = 0
                rescue_mode = False
                white_rescue_mode = False
                
                xw, yw, ww, hw = 0, 0, 0, 0

                if contours_w:
                    contours_w = sorted(contours_w, key=cv2.contourArea, reverse=True)
                    for cw in contours_w:
                        if cv2.contourArea(cw) >= 2: 
                            x_tmp, y_tmp, w_tmp, h_tmp = cv2.boundingRect(cw)
                            
                            if h_tmp >= int(5 * scale_y) and w_tmp <= int(18 * scale_x) and h_tmp >= (w_tmp * 1.5):
                                xw, yw, ww, hw = x_tmp, y_tmp, w_tmp, h_tmp
                                white_h = hw
                                valid_bar_found = True  
                                bar_ever_found = True 
                                last_seen_time = time.time()
                                if white_h > max_white_h: 
                                    max_white_h = white_h
                                if is_debug_mode:
                                    cv2.rectangle(debug_frame, (xw, yw), (xw+ww, yw+hw), (200, 200, 200), 2)
                                break 
                
                # Instan Win dihapus. Kita menunggu Bar Putih hilang.
                
                if valid_bar_found and contours_g:
                    contours_g = sorted(contours_g, key=cv2.contourArea, reverse=True)
                    for cg in contours_g:
                        if cv2.contourArea(cg) >= 2: 
                            xg, yg, wg, hg = cv2.boundingRect(cg)
                            
                            gap = xg - (xw + ww)
                            if abs(yg - yw) < int(30 * scale_y) and (int(5 * scale_x) <= gap <= int(50 * scale_x)):
                                grad_h = hg
                                if is_debug_mode:
                                    cv2.rectangle(debug_frame, (xg, yg), (xg+wg, yg+hg), (100, 255, 100), 2)
                                break

                # =================================================
                # CORE ENGINE MATEMATIKA
                # =================================================
                if valid_bar_found:
                    selisih       = grad_h  - white_h
                    delta_selisih = selisih - prev_selisih

                    prev_grad_h  = grad_h
                    prev_white_h = white_h
                    prev_selisih = selisih

                    max_safe_selisih = ABSOLUTE_MAX_GREEN - white_h - SAFETY_BUFFER

                    BAND_HIGH = max(int(10 * scale_y), min(MAX_BAND_HIGH, max_safe_selisih))
                    
                    if white_h < int(30 * scale_y):
                        current_swing = int(20 * scale_y) 
                        BAND_HIGH = max(BAND_HIGH, int(80 * scale_y)) 
                    elif white_h < int(100 * scale_y):
                        current_swing = int(55 * scale_y) 
                        BAND_HIGH = max(BAND_HIGH, int(100 * scale_y))
                    else:
                        current_swing = MIN_SWING

                    if white_h < TIGHT_GRIP_THRESHOLD:
                        current_swing = min(current_swing, TIGHT_GRIP_SWING) 

                    BAND_LOW = BAND_HIGH - current_swing

                    min_green_floor = int(45 * scale_y)
                    if (white_h + BAND_LOW) < min_green_floor:
                        BAND_LOW = min_green_floor - white_h

                    BAND_HIGH = int(BAND_HIGH * random.uniform(0.98, 1.02))
                    BAND_LOW  = int(BAND_LOW  * random.uniform(0.98, 1.02))

                    delta_clamp = max(int(-15 * scale_y), min(int(15 * scale_y), delta_selisih))
                    
                    effective_band_high = max(BAND_LOW + int(10 * scale_y), BAND_HIGH - max(0, delta_clamp))
                    effective_band_low  = BAND_LOW + min(0, delta_clamp)
                 

                    if white_h > int(380 * scale_y):
                        # MODE FINISH: Jangan berani ayun lebar! 
                        # Fokus menjaga bar hijau tetap di 390px-400px saja.
                        effective_band_high = int(5 * scale_y)
                        effective_band_low = int(-30 * scale_y)
                    if is_cooling_down:
                        if selisih <= effective_band_low:
                            is_cooling_down = False
                    else:
                        if selisih >= effective_band_high:
                            is_cooling_down = True

                    if 0 < white_h < int(35 * scale_y):
                        if grad_h < (ABSOLUTE_MAX_GREEN - int(25 * scale_y)):
                            is_cooling_down = False
                            white_rescue_mode = True

                    if grad_h >= (ABSOLUTE_MAX_GREEN - int(5 * scale_y)):
                        is_cooling_down = True
                        rescue_mode = True
                        white_rescue_mode = False

                    if is_cooling_down:
                        safe_mouse_up()
                        action_text = f"SEL:{selisih:+d} BND:[{BAND_LOW}~{BAND_HIGH}] -> RELEASE"
                        action_color = (0, 0, 255) 
                    else:
                        safe_mouse_down()
                        if rescue_mode:
                            action_text = f"RESCUE GREEN! -> RELEASE PAKSA"
                            action_color = (255, 100, 255) 
                        elif white_rescue_mode:
                            action_text = f"WHITE RESCUE! -> HOLD PAKSA"
                            action_color = (0, 255, 255)
                        else:
                            action_text = f"SEL:{selisih:+d} BND:[{BAND_LOW}~{BAND_HIGH}] -> HOLD"
                            action_color = (0, 255, 0) 

                    if is_debug_mode:
                        try:
                            cv2.putText(debug_frame, f"W:{white_h} G:{grad_h} SEL:{selisih:+d}", (xw, yw-10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
                            cv2.putText(debug_frame, f"dSEL:{delta_selisih:+d} BAND:[{effective_band_low}~{effective_band_high}]", (xw, yw-25), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (200, 200, 100), 1)
                            y_band_low  = yw + white_h + effective_band_low
                            y_band_high = yw + white_h + effective_band_high
                            cv2.line(debug_frame, (xw-15, y_band_low),  (xw+30, y_band_low),  (0, 255, 0), 2)
                            cv2.line(debug_frame, (xw-15, y_band_high), (xw+30, y_band_high), (0, 0, 255), 2)
                        except: pass

                # =================================================
                # [DIPERBAIKI] LOGIKA KEMATIAN UI (HISTORICAL TRIGGER)
                # =================================================
                if not valid_bar_found:
                    time_lost = time.time() - last_seen_time
                    
                    if not bar_ever_found and time_lost < 3.0:
                        safe_mouse_up()
                        action_text = "MENUNGGU UI FASE 3 MUNCUL..."
                        action_color = (255, 255, 0)
                        
                    elif bar_ever_found and time_lost < 0.6:
                        safe_mouse_up() 
                        is_cooling_down = True 
                        action_text = "BAR HILANG / FLICKER..."
                        action_color = (0, 165, 255)
                        
                    else:
                        # Bar putih benar-benar lenyap! Ini akhir minigame.
                        safe_mouse_up()
                        
                        # Cek jejak sejarah: Apakah sebelum lenyap bar putih pernah melampaui Threshold?
                        if max_white_h >= SUCCESS_THRESHOLD: 
                            print(f">>> UI Hilang. Mengonfirmasi: SUKSES (Riwayat Max White: {max_white_h}px | Batas Sukses: >{SUCCESS_THRESHOLD}px)\n")
                            auto_collect_fish(scale_x, scale_y)
                            
                            if afk_mode_enabled:
                                current_time = time.time()
                                if (current_time - last_afk_time) >= (AFK_INTERVAL_MINUTES * 60):
                                    perform_afk_routine()
                                    last_afk_time = time.time()
                        else:
                            print(f">>> UI Hilang. Mengonfirmasi: GAGAL / PUTUS (Riwayat Max White hanya: {max_white_h}px | Butuh: >{SUCCESS_THRESHOLD}px)\n")
                        
                        print(">>> Siklus Selesai. Melempar pancingan baru dalam 4 detik...")
                        time.sleep(4.7)
                        tap_key_scancode(0x04)
                        
                        # Langsung kembali ke Fase 1 (Aman dari jebakan Teks UI)
                        action_text = "AUTO-CASTING..."
                        state = "FASE_1_WAITING" 
                        max_white_h = 0 
                        fase1_start_time = time.time() 
                        time.sleep(1.0) 

            if is_debug_mode and debug_frame is not None:
                cv2.putText(debug_frame, f"State: {state}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                cv2.putText(debug_frame, f"Action: {action_text}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, action_color, 2)
                
                afk_status = "ON" if afk_mode_enabled else "OFF"
                cv2.putText(debug_frame, f"AFK Mode: {afk_status}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                if afk_mode_enabled:
                    time_left = max(0, (AFK_INTERVAL_MINUTES * 60) - (time.time() - last_afk_time))
                    cv2.putText(debug_frame, f"AFK Timer: {int(time_left)}s", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                
                cv2.imshow("Live Debug", debug_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"Error: {e}")
    finally:
        safe_mouse_up()
        camera.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    run_fishing_bot()
