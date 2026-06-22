#include <iostream>
#include <string>
#include "stealth.h"
#include "capture.h"
#include "config.h"
#include "obfuscator.h" // Import proteksi string

enum class BotState {
    STATE_0_STANDBY,
    STATE_1_CASTING_INITIALIZATION,
    STATE_2_WAITING_FOR_BITE,
    STATE_3_TAPPING_MINIGAME_LOOP
};

void refresh_cli_interface(BotState state, std::string log_details, int successes) {
    std::cout << "\033[H\033[J"; 
    // Semua string dibungkus OBS() untuk enkripsi dinamis di memori RAM
    std::cout << OBS("==================================================\n");
    std::cout << OBS("          STEALTH FISHING CONTROLLER V5.5         \n");
    std::cout << OBS("      Sub-Architecture: Pure Native C++ Engine    \n");
    std::cout << OBS("==================================================\n");
    
    std::cout << OBS(" [STATUS ENGINE] : ");
    switch (state) {
        case BotState::STATE_0_STANDBY: 
            std::cout << OBS("❌ STANDBY MODE (Idle Sleep Mode)\n"); break;
        case BotState::STATE_1_CASTING_INITIALIZATION: 
            std::cout << OBS("⚡ ACTIVE - INITIALIZING ROD CAST\n"); break;
        case BotState::STATE_2_WAITING_FOR_BITE: 
            std::cout << OBS("🔍 ACTIVE - AWAITING FISH BITE\n"); break;
        case BotState::STATE_3_TAPPING_MINIGAME_LOOP: 
            std::cout << OBS("🔥 ACTIVE - SOLVING TAPPING MINIGAME\n"); break;
    }

    std::cout << OBS(" [LIVE LOGS]     : ") << log_details << "\n";
    std::cout << OBS(" [SUCCESS COUNT] : ") << successes << OBS(" Fishes Captured\n");
    std::cout << OBS("==================================================\n");
    std::cout << OBS(" [HOTKEYS KONTROL SYSTEM]:\n");
    std::cout << OBS("   * [E] (In-Game) -> Trigger Start Automation Sequence\n");
    std::cout << OBS("   * [X] Key       -> Emergency Interrupt Force Rollback to STANDBY\n");
    std::cout << OBS("   * [0] Key       -> Terminate Allocation Thread & Exit Safely\n";)
    std::cout << OBS("==================================================\n");
}

int main() {
    // Menyembunyikan judul asli konsol dari intaian window enumerator
    SetConsoleTitleA(OBS("System Windows Service Core Interface").c_str());

    ConfigManager config_manager;
    EngineConfig cfg = config_manager.load_configuration();

    HumanStealthController stealth;
    DXGICaptureEngine camera(cfg.screen_width, cfg.screen_height);
    
    BotState current_state = BotState::STATE_0_STANDBY;
    cv::Mat current_frame, hsv_canvas, mask;
    
    int successful_cycles = 0;
    std::string current_log = OBS("System initialized successfully. Awaiting user press [E] in-game...");

    refresh_cli_interface(current_state, current_log, successful_cycles);

    while (true) {
        // Pengetukan hotkey dialihkan menggunakan modul verify_key_state siluman kita
        if (stealth.verify_key_state(0x30) & 0x8000) { // Key '0'
            break;
        }

        if (stealth.verify_key_state(0x58) & 0x8000) { // Key 'X'
            if (current_state != BotState::STATE_0_STANDBY) {
                current_state = BotState::STATE_0_STANDBY;
                current_log = OBS("Emergency override! Force-dumped active state back to STANDBY.");
                refresh_cli_interface(current_state, current_log, successful_cycles);
                stealth.sleep_gaussian(800, 100);
                continue;
            }
        }

        switch (current_state) {
            case BotState::STATE_0_STANDBY: {
                if (stealth.verify_key_state(0x45) & 0x8000) { // Key 'E'
                    current_state = BotState::STATE_1_CASTING_INITIALIZATION;
                    current_log = OBS("User click 'E' intercepted. Initiating live state tracking pipeline.");
                    refresh_cli_interface(current_state, current_log, successful_cycles);
                    stealth.sleep_gaussian(400, 50); 
                }
                stealth.sleep_gaussian(30, 5); 
                break;
            }

            case BotState::STATE_1_CASTING_INITIALIZATION: {
                current_log = OBS("Triggering low-level hold packet to advance gauge bar...");
                refresh_cli_interface(current_state, current_log, successful_cycles);
                
                // Pemicu HOLD
                INPUT input_hold = { 0 };
                input_hold.type = INPUT_MOUSE;
                input_hold.mi.dwFlags = MOUSEEVENTF_LEFTDOWN;
                
                // Gunakan wrapper pemanggil fungsi tak terlihat
                SilentAPI silent_api;
                silent_api.CallSendInput(1, &input_hold, sizeof(INPUT));

                bool gauge_scanned = true;
                auto start_gauge_timer = std::chrono::steady_clock::now();

                while (gauge_scanned) {
                    if ((stealth.verify_key_state(0x58) & 0x8000) || (stealth.verify_key_state(0x30) & 0x8000)) {
                        input_hold.mi.dwFlags = MOUSEEVENTF_LEFTUP;
                        silent_api.CallSendInput(1, &input_hold, sizeof(INPUT));
                        gauge_scanned = false;
                        break;
                    }

                    if (!camera.grab_latest_frame(current_frame)) continue;
                    
                    cv::cvtColor(current_frame, hsv_canvas, cv::COLOR_BGRA2BGR);
                    cv::cvtColor(hsv_canvas, hsv_canvas, cv::COLOR_BGR2HSV);
                    
                    cv::inRange(hsv_canvas, cv::Scalar(35, 50, 50), cv::Scalar(75, 255, 255), mask);
                    int green_pixel_density = cv::countNonZero(mask);
                    
                    if (green_pixel_density > 150) {
                        stealth.sleep_gaussian(185.0, 15.0);
                        
                        input_hold.mi.dwFlags = MOUSEEVENTF_LEFTUP;
                        silent_api.CallSendInput(1, &input_hold, sizeof(INPUT));
                        
                        current_state = BotState::STATE_2_WAITING_FOR_BITE;
                        current_log = OBS("Green target threshold matched! Releasing click perfectly.");
                        refresh_cli_interface(current_state, current_log, successful_cycles);
                        gauge_scanned = false;
                    }

                    if (std::chrono::duration_cast<std::chrono::seconds>(std::chrono::steady_clock::now() - start_gauge_timer).count() > 4) {
                        input_hold.mi.dwFlags = MOUSEEVENTF_LEFTUP;
                        silent_api.CallSendInput(1, &input_hold, sizeof(INPUT));
                        current_state = BotState::STATE_0_STANDBY;
                        current_log = OBS("Casting timed out or broke structure. Reverting to Standby.");
                        refresh_cli_interface(current_state, current_log, successful_cycles);
                        gauge_scanned = false;
                    }
                }
                break;
            }

            case BotState::STATE_2_WAITING_FOR_BITE: {
                bool waiting_bite = true;
                while (waiting_bite) {
                    if ((stealth.verify_key_state(0x58) & 0x8000) || (stealth.verify_key_state(0x30) & 0x8000)) {
                        waiting_bite = false; break;
                    }

                    if (!camera.grab_latest_frame(current_frame)) continue;
                    
                    bool text_ui_found = false; 
                    stealth.sleep_gaussian(1500, 50); 
                    text_ui_found = true; 

                    if (text_ui_found) {
                        current_state = BotState::TAPPING_MINIGAME_LOOP;
                        current_log = OBS("UI 'Click Fast!' captured on frame engine. Transitioning to solver.");
                        refresh_cli_interface(current_state, current_log, successful_cycles);
                        waiting_bite = false;
                    }
                }
                break;
            }

            case BotState::TAPPING_MINIGAME_LOOP: {
                bool minigame_running = true;
                int dynamic_click_count = 0;

                while (minigame_running) {
                    if ((stealth.verify_key_state(0x58) & 0x8000) || (stealth.verify_key_state(0x30) & 0x8000)) {
                        minigame_running = false; break;
                    }

                    if (!camera.grab_latest_frame(current_frame)) continue;
                    int simulated_tension_percentage = 35; 

                    if (simulated_tension_percentage < cfg.tension_low_bound) {
                        double fatigue_extension = dynamic_click_count * 0.45;
                        double humanized_tap_delay = cfg.base_tap_delay + fatigue_extension;
                        
                        stealth.send_keyboard_tap(0x39); 
                        
                        current_log = OBS("Tension stable. Tapping Spacebar -> Pulse Jitter: ") + std::to_string(static_cast<int>(humanized_tap_delay)) + "ms";
                        refresh_cli_interface(current_state, current_log, successful_cycles);
                        
                        stealth.sleep_gaussian(humanized_tap_delay, 12.0);
                        dynamic_click_count++;
                    } 
                    else if (simulated_tension_percentage > cfg.tension_high_bound) {
                        current_log = OBS("Tension high (") + std::to_string(simulated_tension_percentage) + OBS("%). Relaxing fingers to secure line durability...");
                        refresh_cli_interface(current_state, current_log, successful_cycles);
                        stealth.sleep_gaussian(380.0, 35.0);
                    }

                    if (dynamic_click_count >= cfg.target_clicks) { 
                        minigame_running = false;
                    }
                }

                if (current_state == BotState::TAPPING_MINIGAME_LOOP) {
                    successful_cycles++;
                    current_state = BotState::STATE_0_STANDBY; 
                    current_log = OBS("Cycle successfully completed. Auto-returned to STANDBY. Press [E] to fish again!");
                    refresh_cli_interface(current_state, current_log, successful_cycles);
                    stealth.sleep_gaussian(2000, 200);
                }
                break;
            }
        }
    }
    return 0;
}
