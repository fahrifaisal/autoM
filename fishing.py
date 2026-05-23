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
    duration = random.uniform(0.04, 0.08) 
    safe_mouse_down()
    time.sleep(duration)
    safe_mouse_up()

def press_key_3():
    hexKeyCode = 0x04 
    extra = ctypes.c_ulong(0)
    
    ii_down = Input_I()
    ii_down.ki = KeyBdInput(0, hexKeyCode, KEYEVENTF_SCANCODE, 0, ctypes.pointer(extra))
    x_down = Input(ctypes.c_ulong(INPUT_KEYBOARD), ii_down)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x_down), ctypes.sizeof(x_down))
    
    time.sleep(random.uniform(0.1, 0.2)) 
    
    ii_up = Input_I()
    ii_up.ki = KeyBdInput(0, hexKeyCode, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP, 0, ctypes.pointer(extra))
    x_up = Input(ctypes.c_ulong(INPUT_KEYBOARD), ii_up)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x_up), ctypes.sizeof(x_up))

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

def auto_collect_fish():
    print("\n>>> TARGET TERCAPAI! Mengeksekusi Auto-Collect...")
    time.sleep(0.8) 
    
    collect_x, collect_y = 800, 930
    smooth_move_mouse(collect_x, collect_y)
    
    time.sleep(random.uniform(0.1, 0.2)) 
    single_click()
    print(">>> Auto-Collect Selesai.\n")

# ==========================================
# 2. LOGIKA UTAMA BOT PANCING
# ==========================================
def run_fishing_bot():
    # --- SISTEM CONFIG.INI ---
    # Memastikan file config berada di folder yang sama dengan file .exe
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    config_file_path = os.path.join(application_path, 'config.ini')
    config = configparser.ConfigParser()

    # Buat default config jika file tidak ada
    if not os.path.exists(config_file_path):
        config['ENGINE'] = {
            'ABSOLUTE_MAX_GREEN': '350',
            'SAFETY_BUFFER': '15',
            'MIN_SWING': '120',
            'MAX_BAND_HIGH': '100',
            'TIMEOUT_SECONDS': '60'
        }
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)

    config.read(config_file_path)
    
    # Load variabel dari config
    ABSOLUTE_MAX_GREEN = int(config['ENGINE'].get('ABSOLUTE_MAX_GREEN', '350'))
    SAFETY_BUFFER = int(config['ENGINE'].get('SAFETY_BUFFER', '15'))
    MIN_SWING = int(config['ENGINE'].get('MIN_SWING', '120'))
    MAX_BAND_HIGH = int(config['ENGINE'].get('MAX_BAND_HIGH', '100'))
    TIMEOUT_SECONDS = int(config['ENGINE'].get('TIMEOUT_SECONDS', '60'))

    # ---------------------------

    left, top, right, bottom = 500, 250, 1500, 1080 
    region = (left, top, right, bottom)
    
    camera = dxcam.create(output_color="BGR")
    camera.start(target_fps=60, region=region)
    
    state = "FASE_0_STANDBY"
    is_debug_mode = False
    debug_key_pressed = False
    
    phase3_start_time = 0
    last_seen_time = 0 
    fase1_start_time = 0 
    max_white_h = 0
    
    is_cooling_down = False 
    bar_ever_found = False 
    
    lower_grad = np.array([0, 120, 200]) 
    upper_grad = np.array([50, 255, 255])
    
    lower_white = np.array([0, 0, 160])
    upper_white = np.array([179, 50, 255])

    prev_grad_h = 0
    prev_white_h = 0
    prev_selisih = 0
    delta_selisih = 0

    print("========================================")
    print("      FISHING PIXEL BOT (OBFUSCATED)    ")
    print("  Logic: Extreme Momentum & Delta Ctrl  ")
    print("========================================")
    print(f"[CONFIG LOADED] Max Green: {ABSOLUTE_MAX_GREEN}, Swing: {MIN_SWING}")
    print("========================================")
    print("[8] - Toggle Live Debug View")
    print("[9] - Exit Program")
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
                    press_key_3()
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
                        
                        if (3 <= h <= 15) and w > 80 and w > (h * 5):
                            action_text = "FASE 2 DETECTED! HOOKING..."
                            single_click()
                            time.sleep(0.5) 
                            
                            safe_mouse_down() 
                            is_cooling_down = False 
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
                contours_g, _ = cv2.findContours(mask_grad, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                mask_white = cv2.inRange(hsv_frame, lower_white, upper_white)
                contours_w, _ = cv2.findContours(mask_white, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                valid_bar_found = False
                is_in_transition = (time.time() - phase3_start_time) < 1.0 
                
                grad_h = 0
                white_h = 0
                rescue_mode = False

                if contours_g:
                    c_g = max(contours_g, key=cv2.contourArea)
                    if cv2.contourArea(c_g) > 20: 
                        x, y, w, h = cv2.boundingRect(c_g)
                        
                        if h > 10 and h > (w * 1.5) and w < 60:
                            valid_bar_found = True
                            bar_ever_found = True 
                            last_seen_time = time.time() 
                            grad_h = h
                            
                            if contours_w:
                                for cw in contours_w:
                                    if cv2.contourArea(cw) >= 2: 
                                        xw, yw, ww, hw = cv2.boundingRect(cw)
                                        if hw >= 2 and ww < 30:
                                            gap = x - (xw + ww)
                                            if abs(y - yw) < 20 and (5 <= gap <= 40):
                                                white_h = hw
                                                if white_h > max_white_h: 
                                                    max_white_h = white_h
                                                
                                                if is_debug_mode:
                                                    cv2.rectangle(debug_frame, (xw, yw), (xw+ww, yw+hw), (200, 200, 200), 2)
                                                break 

                            selisih       = grad_h  - white_h
                            delta_selisih = selisih - prev_selisih

                            prev_grad_h  = grad_h
                            prev_white_h = white_h
                            prev_selisih = selisih

                            max_safe_selisih = ABSOLUTE_MAX_GREEN - white_h - SAFETY_BUFFER

                            BAND_HIGH = max(10, min(MAX_BAND_HIGH, max_safe_selisih))
                            BAND_LOW = BAND_HIGH - MIN_SWING

                            BAND_HIGH = int(BAND_HIGH * random.uniform(0.98, 1.02))
                            BAND_LOW  = int(BAND_LOW  * random.uniform(0.98, 1.02))

                            delta_clamp = max(-15, min(15, delta_selisih))
                            
                            effective_band_high = max(BAND_LOW + 10, BAND_HIGH - max(0, delta_clamp))
                            effective_band_low  = BAND_LOW + min(0, delta_clamp)

                            if is_cooling_down:
                                if selisih <= effective_band_low:
                                    is_cooling_down = False
                            else:
                                if selisih >= effective_band_high:
                                    is_cooling_down = True

                            if grad_h >= (ABSOLUTE_MAX_GREEN - 5):
                                is_cooling_down = True
                                rescue_mode = True

                            if is_cooling_down:
                                safe_mouse_up()
                                action_text = f"SEL:{selisih:+d} dSEL:{delta_selisih:+d} BND:[{BAND_LOW}~{BAND_HIGH}] -> RELEASE"
                                action_color = (0, 0, 255) 
                            else:
                                safe_mouse_down()
                                if rescue_mode:
                                    action_text = f"RESCUE! GREEN AT PEAK -> RELEASE PAKSA"
                                    action_color = (255, 100, 255) 
                                else:
                                    action_text = f"SEL:{selisih:+d} dSEL:{delta_selisih:+d} BND:[{BAND_LOW}~{BAND_HIGH}] -> HOLD"
                                    action_color = (0, 255, 0) 

                            if is_debug_mode:
                                cv2.rectangle(debug_frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                                cv2.putText(debug_frame, f"W:{white_h} G:{grad_h} SEL:{selisih:+d}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
                                cv2.putText(debug_frame, f"dSEL:{delta_selisih:+d} BAND:[{effective_band_low}~{effective_band_high}]", (x, y-25), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (200, 200, 100), 1)
                                
                                y_band_low  = y + white_h + effective_band_low
                                y_band_high = y + white_h + effective_band_high
                                cv2.line(debug_frame, (x-15, y_band_low),  (x+w+15, y_band_low),  (0, 255, 0), 2)
                                cv2.line(debug_frame, (x-15, y_band_high), (x+w+15, y_band_high), (0, 0, 255), 2)

                if not valid_bar_found:
                    time_lost = time.time() - last_seen_time
                    
                    if is_in_transition:
                        safe_mouse_down()
                        action_text = "TRANSISI: INITIAL PULL..."
                        action_color = (255, 100, 100)
                        
                    elif not bar_ever_found and time_lost < 2.5:
                        safe_mouse_down()
                        action_text = "MEMBANGUN TENSION AWAL DARI 0..."
                        action_color = (255, 100, 100)
                        
                    elif bar_ever_found and time_lost < 0.6:
                        safe_mouse_up() 
                        is_cooling_down = True 
                        action_text = "BAR HILANG / FLICKER..."
                        action_color = (0, 165, 255)
                        
                    else:
                        safe_mouse_up()
                        
                        if max_white_h >= 320: 
                            auto_collect_fish()
                        else:
                            print(f">>> Gagal / Putus (Max White Bar hanya: {max_white_h}px)\n")
                        
                        print(">>> Siklus Selesai. Melempar pancingan baru dalam 4 detik...")
                        time.sleep(4.0)
                        press_key_3()
                        
                        action_text = "AUTO-CASTING..."
                        state = "FASE_1_WAITING" 
                        max_white_h = 0 
                        fase1_start_time = time.time() 
                        time.sleep(1.0) 

            if is_debug_mode and debug_frame is not None:
                cv2.putText(debug_frame, f"State: {state}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                cv2.putText(debug_frame, f"Action: {action_text}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, action_color, 2)
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
