#include <iostream>
#include <string>
#include <chrono>
#include <thread>
#include <random>
#include <opencv2/opencv.hpp>
#include "telemetry.h"
#include "viewport.h"
#include "runtime_env.h"
#include "crypto_core.h"

// ====================================================================================
// ⚡ SAKLAR MATRIX BUILDS TARGET CONTROL
// ====================================================================================
// AKTIFKAN (Jangan di-comment): Untuk kompilasi versi DEBUG (Ada Jendela & Hotkey 9 aktif).
// MATIKAN (Beri tanda //): Untuk kompilasi versi STEALTH RELEASE (Headless murni, Jendela dihapus total).
#define ENABLE_DEBUG_GUI 
// ====================================================================================

enum class PipelineStatus {
    LIFECYCLE_STANDBY,
    LIFECYCLE_INITIALIZE_PULSE,
    LIFECYCLE_AWAIT_STREAM_SIGNAL,
    LIFECYCLE_PROCESS_TELEMETRY
};

double generate_humanized_jitter(double base, double variance) {
    static std::random_device rd;
    static std::mt19937 eng(rd()); 
    std::uniform_real_distribution<double> distr(-variance, variance);
    return base + distr(eng);
}

void update_system_diagnostic_display(PipelineStatus status, std::string log_details, int processed_packets, bool debug_active) {
    std::cout << "\033[H\033[J"; 
    std::cout << "==================================================\n";
    std::cout << "       WINDOWS SYSTEM CORE SERVICE SUBSYSTEM       \n";
    
#ifdef ENABLE_DEBUG_GUI
    std::cout << "    Sub-Architecture: Interactive Debug Subsystem \n";
#else
    std::cout << "    Sub-Architecture: Stealth Headless Production \n";
#endif

    std::cout << "==================================================\n";
    std::cout << " [SERVICE STATUS]  : ";
    switch (status) {
        case PipelineStatus::LIFECYCLE_STANDBY:            std::cout << "[STANDBY] Subsystem Armed (Awaiting Hotkey)\n"; break;
        case PipelineStatus::LIFECYCLE_INITIALIZE_PULSE:   std::cout << "[RUNNING] Realtime Pasting Analysis Engaged\n"; break;
        case PipelineStatus::LIFECYCLE_AWAIT_STREAM_SIGNAL: std::cout << "[WAITING] Passive Surveillance for Peeling UI\n"; break;
        case PipelineStatus::LIFECYCLE_PROCESS_TELEMETRY:  std::cout << "[PEELING] Stateful Hysteresis Tension Pumping\n"; break;
    }

#ifdef ENABLE_DEBUG_GUI
    std::cout << " [VISUAL DEBUG 9]  : " << (debug_active ? "🟢 ACTIVE (60 FPS Safe-Throttle Render)\n" : "🔴 DISABLED (Headless High-Performance Mode)\n");
#else
    std::cout << " [VISUAL DEBUG 9]  : 🔒 COMPILED OUT (Stealth Safe Production Profile)\n";
#endif

    std::cout << " [DIAGNOSTIC LOGS] : " << log_details << "\n";
    std::cout << " [PACKETS COUNTER] : " << processed_packets << " Data Bursts Transmitted\n";
    std::cout << "==================================================\n";
    std::cout << " [HARDWARE CONTROLLER INTERRUPT]:\n";
    std::cout << "   * [E] Key -> Pulse Start Automation Signal Loop\n";
    std::cout << "   * [X] Key -> Flush Queue Buffer & Standby Recovery\n";
    
#ifdef ENABLE_DEBUG_GUI
    std::cout << "   * [9] Key -> Debug Window\n";
#endif

    std::cout << "   * [0] Key -> Terminate Thread Allocator & Safe Exit\n";
    std::cout << "==================================================\n";
}

int main() {
    SetConsoleTitleA("System Windows Service Core Interface");
    EnvironmentProfile environment;
    RuntimeProfile env_cfg = environment.initialize_environment();
    TelemetryInputProcessor telemetry;
    ViewportBufferContext camera(env_cfg.buffer_width, env_cfg.buffer_height);
    SilentAPI silent_api;
    
    PipelineStatus current_lifecycle = PipelineStatus::LIFECYCLE_STANDBY;
    cv::Mat current_matrix, hsv_canvas, debug_canvas;
    int successful_bursts = 0;
    bool debug_mode_active = false; 
    std::string operational_log = "Service link established. Subsystem listener armed.";

    // Mengunci parameter sweet-spot hasil eksperimen terbaik kamu[cite: 1]
    env_cfg.tension_y = 558; //[cite: 1]
    env_cfg.tension_start_x = 290; //[cite: 1]  
    env_cfg.tension_end_x = 540; //[cite: 1]    
    env_cfg.template_threshold = 0.9; 

    cv::Mat gray_template = cv::imread("template_e.png", cv::IMREAD_GRAYSCALE);
    update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts, debug_mode_active);

    INPUT pulse_up = { 0 };
    pulse_up.type = INPUT_KEYBOARD;
    pulse_up.ki.wScan = 0x39; 
    pulse_up.ki.dwFlags = KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP;

    int global_target_box_y = -1;
    int global_live_indicator_y = -1;
    int global_highest_tension_x = env_cfg.tension_start_x;

    auto verify_solid_white_block = [&](const cv::Mat& hsv_img, int center_x, int y_coord, int radius, int max_s, int min_v) {
        int solid_hits = 0;
        int total_checks = 0;
        for (int dx = -radius; dx <= radius; ++dx) {
            int check_x = center_x + dx;
            if (check_x >= 0 && check_x < hsv_img.cols) {
                cv::Vec3b p = hsv_img.at<cv::Vec3b>(y_coord, check_x);
                if (p[1] <= max_s && p[2] >= min_v) {
                    solid_hits++;
                }
                total_checks++;
            }
        }
        return (solid_hits == total_checks); 
    };

    auto pulse_visual_debugger_frame = [&](const cv::Mat& frame) {
#ifdef ENABLE_DEBUG_GUI
        if (!debug_mode_active) return;

        static auto last_gui_refresh = std::chrono::steady_clock::now();
        auto current_time = std::chrono::steady_clock::now();
        
        if (std::chrono::duration_cast<std::chrono::milliseconds>(current_time - last_gui_refresh).count() < 16) {
            return; 
        }
        last_gui_refresh = current_time;

        debug_canvas = frame.clone();

        // 1. Radar Vertikal pasting
        cv::line(debug_canvas, cv::Point(345, 30), cv::Point(345, 331), cv::Scalar(255, 255, 0), 2);
        cv::line(debug_canvas, cv::Point(355, 30), cv::Point(355, 331), cv::Scalar(0, 255, 255), 2);
        cv::line(debug_canvas, cv::Point(365, 30), cv::Point(365, 331), cv::Scalar(255, 255, 0), 2);

        // 2. Kotak Target Box Hijau
        if (global_target_box_y != -1) {
            cv::rectangle(debug_canvas, cv::Point(340, global_target_box_y - 15), cv::Point(370, global_target_box_y + 15), cv::Scalar(0, 255, 0), 2);
        }

        // 3. Titik Indikator Merah
        if (global_live_indicator_y != -1) {
            cv::circle(debug_canvas, cv::Point(355, global_live_indicator_y), 6, cv::Scalar(0, 0, 255), -1);
        }

        // 4. Garis Radar Horizontal Tension Bar
        cv::line(debug_canvas, cv::Point(env_cfg.tension_start_x, env_cfg.tension_y), cv::Point(env_cfg.tension_end_x, env_cfg.tension_y), cv::Scalar(255, 0, 255), 3);
        cv::circle(debug_canvas, cv::Point(global_highest_tension_x, env_cfg.tension_y), 5, cv::Scalar(0, 255, 255), -1);

        // 5. Area Validasi E HUD Bawah
        cv::rectangle(debug_canvas, cv::Rect(290, 645, 345, 45), cv::Scalar(255, 0, 255), 2);

        cv::imshow("Subsystem Integrated Diagnostic Window", debug_canvas);
        cv::waitKey(1); 
#endif
    };

#define CHECK_GLOBAL_INTERRUPTS() \
    if (telemetry.intercept_hardware_state(0x30) & 0x8000) { silent_api.CallSendInput(1, &pulse_up, sizeof(INPUT)); cv::destroyAllWindows(); return 0; } \
    if (telemetry.intercept_hardware_state(0x58) & 0x8000) { \
        silent_api.CallSendInput(1, &pulse_up, sizeof(INPUT)); \
        current_lifecycle = PipelineStatus::LIFECYCLE_STANDBY; \
        operational_log = "Subsystem emergency flush active. Returned to STANDBY."; \
        update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts, debug_mode_active); \
        telemetry.inject_delay_distribution(800, 100); \
        break; \
    }

    while (true) {
        if (telemetry.intercept_hardware_state(0x30) & 0x8000) break; 

        // ⚡ PROSTRATE GATING: Logika Hotkey 9 hanya akan dicetak ke biner jika mode debug dinyalakan
#ifdef ENABLE_DEBUG_GUI
        if (telemetry.intercept_hardware_state(0x39) & 0x8000) { 
            debug_mode_active = !debug_mode_active;
            if (!debug_mode_active) {
                cv::destroyAllWindows(); 
            } else {
                cv::namedWindow("Subsystem Integrated Diagnostic Window", cv::WINDOW_NORMAL | cv::WINDOW_KEEPRATIO);
            }
            update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts, debug_mode_active);
            std::this_thread::sleep_for(std::chrono::milliseconds(250)); 
        }
#endif

        if (camera.fetch_active_matrix(current_matrix)) {
            pulse_visual_debugger_frame(current_matrix);
        }

        switch (current_lifecycle) {
            case PipelineStatus::LIFECYCLE_STANDBY: {
                static auto last_reload = std::chrono::steady_clock::now();
                auto current_time = std::chrono::steady_clock::now();
                if (std::chrono::duration_cast<std::chrono::seconds>(current_time - last_reload).count() >= 1) {
                    env_cfg = environment.initialize_environment();
                    env_cfg.tension_start_x = 290; //[cite: 1]
                    env_cfg.tension_end_x = 540; //[cite: 1]
                    env_cfg.template_threshold = 0.9;
                    last_reload = current_time;
                }

                if (telemetry.intercept_hardware_state(0x45) & 0x8000) { 
                    current_lifecycle = PipelineStatus::LIFECYCLE_INITIALIZE_PULSE;
                    operational_log = "Initial interrupt context captured. Starting core automation pipeline.";
                    update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts, debug_mode_active);
                    telemetry.inject_delay_distribution(300, 30); 
                }
                telemetry.inject_delay_distribution(16, 2); 
                break;
            }

            case PipelineStatus::LIFECYCLE_INITIALIZE_PULSE: {
                global_target_box_y = -1;
                global_live_indicator_y = -1;
                int localized_target_y = -1;
                
                // --- FASE 1: SCANNING TARGET BOX ---
                auto scan_timer = std::chrono::steady_clock::now();
                while (localized_target_y == -1) {
                    CHECK_GLOBAL_INTERRUPTS();
                    if (std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - scan_timer).count() > 3500) break;
                    
                    if (!camera.fetch_active_matrix(current_matrix)) continue;
                    pulse_visual_debugger_frame(current_matrix);
                    
                    cv::cvtColor(current_matrix, hsv_canvas, cv::COLOR_BGRA2BGR);
                    cv::cvtColor(hsv_canvas, hsv_canvas, cv::COLOR_BGR2HSV);

                    int current_run_length = 0;
                    int run_start_y = -1;

                    for (int y = 30; y <= 331; ++y) {
                        cv::Vec3b p1 = hsv_canvas.at<cv::Vec3b>(y, 345);
                        cv::Vec3b p2 = hsv_canvas.at<cv::Vec3b>(y, 355); 
                        cv::Vec3b p3 = hsv_canvas.at<cv::Vec3b>(y, 365);
                        
                        bool is_vibrant_ui = (p1[1] >= 45 && p1[2] >= env_cfg.pasting_bright_v) || //[cite: 1]
                                             (p2[1] >= 45 && p2[2] >= env_cfg.pasting_bright_v) || //[cite: 1]
                                             (p3[1] >= 45 && p3[2] >= env_cfg.pasting_bright_v); //[cite: 1]

                        if (is_vibrant_ui) {
                            if (current_run_length == 0) run_start_y = y;
                            current_run_length++;
                        } else {
                            if (current_run_length >= 24 && current_run_length <= 40) {
                                localized_target_y = (run_start_y + y - 1) / 2;
                                global_target_box_y = localized_target_y; 
                                break; 
                            }
                            current_run_length = 0; 
                        }
                    }
                    
                    if (localized_target_y == -1 && current_run_length >= 24 && current_run_length <= 40) {
                        localized_target_y = (run_start_y + 331) / 2;
                        global_target_box_y = localized_target_y;
                    }

                    if (localized_target_y != -1) break; 
                    telemetry.inject_delay_distribution(4.0, 1.0);
                }

                if (localized_target_y == -1) {
                    operational_log = "[🚨] Structural Target Box absent from viewport! repasting line...";
                    update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts, debug_mode_active);
                    telemetry.inject_delay_distribution(env_cfg.repast_delay, env_cfg.repast_var); //[cite: 1]
                    telemetry.dispatch_hardware_stroke(0x12, env_cfg.key_hold_base, env_cfg.key_hold_var); //[cite: 1]
                    break;
                }

                // --- FASE 2: pastING ENGAGED ---
                INPUT pulse_down = { 0 };
                pulse_down.type = INPUT_KEYBOARD;
                pulse_down.ki.wScan = 0x39;
                pulse_down.ki.dwFlags = KEYEVENTF_SCANCODE;
                silent_api.CallSendInput(1, &pulse_down, sizeof(INPUT));
                
                auto pulse_timer = std::chrono::steady_clock::now();
                bool release_triggered = false;
                int last_indicator_y = -1; 

                while (current_lifecycle == PipelineStatus::LIFECYCLE_INITIALIZE_PULSE) {
                    CHECK_GLOBAL_INTERRUPTS(); 
                    if (!camera.fetch_active_matrix(current_matrix)) continue;
                    pulse_visual_debugger_frame(current_matrix);
                    
                    cv::cvtColor(current_matrix, hsv_canvas, cv::COLOR_BGRA2BGR);
                    cv::cvtColor(hsv_canvas, hsv_canvas, cv::COLOR_BGR2HSV);
                    
                    int current_indicator_y = -1;
                    int ind_run = 0, ind_start = -1;

                    for (int y = 30; y <= 331; ++y) {
                        cv::Vec3b p1 = hsv_canvas.at<cv::Vec3b>(y, 345);
                        cv::Vec3b p2 = hsv_canvas.at<cv::Vec3b>(y, 355); 
                        cv::Vec3b p3 = hsv_canvas.at<cv::Vec3b>(y, 365);
                        
                        bool is_vibrant_ui = (p1[1] >= 25 && p1[2] >= env_cfg.pasting_bright_v) || //[cite: 1]
                                             (p2[1] >= 25 && p2[2] >= env_cfg.pasting_bright_v) || //[cite: 1]
                                             (p3[1] >= 25 && p3[2] >= env_cfg.pasting_bright_v); //[cite: 1]

                        if (is_vibrant_ui) {
                            if (ind_run == 0) ind_start = y;
                            ind_run++;
                        } else {
                            if (ind_run >= 2 && ind_run <= 15) {
                                int mid_point_y = (ind_start + y - 1) / 2;
                                if (std::abs(mid_point_y - localized_target_y) > 12) {
                                    current_indicator_y = mid_point_y;
                                    global_live_indicator_y = current_indicator_y; 
                                }
                            }
                            ind_run = 0;
                        }
                    }

                    if (current_indicator_y != -1) {
                        int current_velocity_y = 0;
                        if (last_indicator_y != -1 && current_indicator_y > last_indicator_y) {
                            current_velocity_y = current_indicator_y - last_indicator_y; 
                        }
                        last_indicator_y = current_indicator_y; 

                        int predicted_next_frame_y = current_indicator_y + current_velocity_y;
                        int brake_threshold_boundary = localized_target_y - env_cfg.past_brake_offset; //[cite: 1]

                        if (current_indicator_y >= brake_threshold_boundary || 
                            (current_velocity_y > 0 && predicted_next_frame_y >= brake_threshold_boundary)) { 
                            silent_api.CallSendInput(1, &pulse_up, sizeof(INPUT)); 
                            release_triggered = true;
                            break; 
                        }
                    }

                    if (std::chrono::duration_cast<std::chrono::seconds>(std::chrono::steady_clock::now() - pulse_timer).count() > 4) {
                        silent_api.CallSendInput(1, &pulse_up, sizeof(INPUT));
                        telemetry.inject_delay_distribution(env_cfg.repast_delay, env_cfg.repast_var); //[cite: 1]
                        telemetry.dispatch_hardware_stroke(0x12, env_cfg.key_hold_base, env_cfg.key_hold_var); //[cite: 1]
                        break; 
                    }
                }

                // --- FASE 3: ONE-TIME TEMPLATE MATCHING ---
                if (release_triggered) {
                    double humanized_wait = generate_humanized_jitter(650.0, 45.0);
                    std::this_thread::sleep_for(std::chrono::milliseconds(static_cast<int>(humanized_wait))); 
                    
                    if (camera.fetch_active_matrix(current_matrix)) {
                        bool e_button_is_present = false;

                        cv::Mat hud_roi = current_matrix(cv::Rect(290, 645, 345, 45));
                        cv::Mat gray_roi;
                        cv::cvtColor(hud_roi, gray_roi, cv::COLOR_BGRA2GRAY);

                        if (!gray_template.empty()) {
                            cv::Mat match_result;
                            cv::matchTemplate(gray_roi, gray_template, match_result, cv::TM_CCOEFF_NORMED);

                            double min_val, max_val;
                            cv::Point min_loc, max_loc;
                            cv::minMaxLoc(match_result, &min_val, &max_val, &min_loc, &max_loc);

                            operational_log = "[📊] Template Match Score Captured: " + std::to_string(max_val) + " (Req Threshold: " + std::to_string(env_cfg.template_threshold) + ")"; //[cite: 1]
                            update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts, debug_mode_active);

                            if (max_val >= env_cfg.template_threshold) { //[cite: 1]
                                e_button_is_present = true;
                            }
                        }

                        if (e_button_is_present) {
                            operational_log = "[❌] pasting Failed Verified by Template! repasting...";
                            update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts, debug_mode_active);
                            
                            telemetry.inject_delay_distribution(env_cfg.repast_delay, env_cfg.repast_var); //[cite: 1]
                            telemetry.dispatch_hardware_stroke(0x12, env_cfg.key_hold_base, env_cfg.key_hold_var); //[cite: 1]
                            current_lifecycle = PipelineStatus::LIFECYCLE_INITIALIZE_PULSE;
                        } else {
                            current_lifecycle = PipelineStatus::LIFECYCLE_AWAIT_STREAM_SIGNAL;
                            operational_log = "pasting clear! HUD template absent (Success). Watching for White Box...";
                            update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts, debug_mode_active);
                        }
                    }
                }
                break;
            }

            case PipelineStatus::LIFECYCLE_AWAIT_STREAM_SIGNAL: {
                global_target_box_y = -1;
                global_live_indicator_y = -1;
                while (current_lifecycle == PipelineStatus::LIFECYCLE_AWAIT_STREAM_SIGNAL) {
                    CHECK_GLOBAL_INTERRUPTS(); 
                    if (!camera.fetch_active_matrix(current_matrix)) continue;
                    pulse_visual_debugger_frame(current_matrix);
                    
                    cv::cvtColor(current_matrix, hsv_canvas, cv::COLOR_BGRA2BGR);
                    cv::cvtColor(hsv_canvas, hsv_canvas, cv::COLOR_BGR2HSV);
                    
                    bool block1_solid = verify_solid_white_block(hsv_canvas, 412, 440, 4, 30, env_cfg.peeling_white_v); //[cite: 1]
                    bool block2_solid = verify_solid_white_block(hsv_canvas, 507, 440, 4, 30, env_cfg.peeling_white_v); //[cite: 1]
                    
                    bool white_box_appeared = block1_solid || block2_solid;

                    if (white_box_appeared) { 
                        current_lifecycle = PipelineStatus::LIFECYCLE_PROCESS_TELEMETRY;
                        operational_log = "True Solid White Box verified. Deploying Stateful Hysteresis Pump.";
                        update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts, debug_mode_active);
                        telemetry.inject_delay_distribution(80, 15);
                        break; 
                    }
                    telemetry.inject_delay_distribution(20.0, 4.0); 
                }
                break;
            }

            case PipelineStatus::LIFECYCLE_PROCESS_TELEMETRY: {
                int ui_absence_frames = 0;
                bool tension_cooling_down = false; 

                while (current_lifecycle == PipelineStatus::LIFECYCLE_PROCESS_TELEMETRY) {
                    CHECK_GLOBAL_INTERRUPTS(); 
                    if (!camera.fetch_active_matrix(current_matrix)) continue;
                    pulse_visual_debugger_frame(current_matrix); 

                    cv::cvtColor(current_matrix, hsv_canvas, cv::COLOR_BGRA2BGR);
                    cv::cvtColor(hsv_canvas, hsv_canvas, cv::COLOR_BGR2HSV);
                    
                    bool ui_is_still_open = verify_solid_white_block(hsv_canvas, 412, 440, 4, 30, env_cfg.peeling_white_v - 20) || //[cite: 1]
                                            verify_solid_white_block(hsv_canvas, 507, 440, 4, 30, env_cfg.peeling_white_v - 20); //[cite: 1]

                    if (!ui_is_still_open) {
                        ui_absence_frames++;
                    } else {
                        ui_absence_frames = 0; 
                    }

                    if (ui_absence_frames >= 5) { 
                        successful_bursts++;
                        current_lifecycle = PipelineStatus::LIFECYCLE_INITIALIZE_PULSE; 
                        
                        operational_log = "Transaction ended. Standby delay...";
                        update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts, debug_mode_active);
                        
                        telemetry.inject_delay_distribution(env_cfg.repast_delay, env_cfg.repast_var); //[cite: 1]
                        telemetry.dispatch_hardware_stroke(0x12, env_cfg.key_hold_base, env_cfg.key_hold_var); //[cite: 1]
                        break; 
                    }

                    int highest_occupied_cluster_x = env_cfg.tension_start_x; //[cite: 1]

                    for (int x = env_cfg.tension_start_x; x <= env_cfg.tension_end_x; ++x) { //[cite: 1]
                        bool row_voted_active = false;
                        
                        for (int dy = -1; dy <= 1; ++dy) {
                            int check_y = env_cfg.tension_y + dy; //[cite: 1]
                            cv::Vec3b pixel = hsv_canvas.at<cv::Vec3b>(check_y, x); 
                            
                            if (pixel[2] >= env_cfg.tension_bright_v &&  //[cite: 1]
                                pixel[1] >= env_cfg.tension_sat_min) { //[cite: 1]
                                row_voted_active = true;
                                break;
                            }
                        }
                        
                        if (row_voted_active) {
                            highest_occupied_cluster_x = x; 
                        }
                    }

                    global_highest_tension_x = highest_occupied_cluster_x; 
                    
                    double total_roi_width = static_cast<double>(env_cfg.tension_end_x - env_cfg.tension_start_x); //[cite: 1]
                    double current_load_ratio = ((highest_occupied_cluster_x - env_cfg.tension_start_x) / total_roi_width) * 100.0; //[cite: 1]

                    if (tension_cooling_down) {
                        if (current_load_ratio <= (env_cfg.signal_floor + 6.0)) { //[cite: 1]
                            tension_cooling_down = false; 
                        } else {
                            operational_log = "[LIVE REEL] Tension: " + std::to_string(static_cast<int>(current_load_ratio)) + "% | Letting Drop (Cooling Down Pump)...";
                            update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts, debug_mode_active);
                            telemetry.inject_delay_distribution(40.0, 4.0); 
                            continue; 
                        }
                    }

                    if (current_load_ratio >= env_cfg.signal_ceiling) { //[cite: 1]
                        tension_cooling_down = true; 
                        operational_log = "[LIVE REEL] Tension: " + std::to_string(static_cast<int>(current_load_ratio)) + "% | CEILING HIT! Entering cool-down.";
                        update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts, debug_mode_active);
                        telemetry.inject_delay_distribution(100.0, 10.0); 
                    } 
                    else if (current_load_ratio <= env_cfg.signal_floor) { //[cite: 1]
                        double safety_hold = generate_humanized_jitter(env_cfg.key_hold_base, env_cfg.key_hold_var); //[cite: 1]
                        telemetry.dispatch_hardware_stroke(0x39, safety_hold, env_cfg.key_hold_var); //[cite: 1]
                        operational_log = "[LIVE REEL] Tension: " + std::to_string(static_cast<int>(current_load_ratio)) + "% | SAFE FLOOR! Pumping Deep Pulse.";
                        update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts, debug_mode_active);
                        telemetry.inject_delay_distribution(env_cfg.pulse_interval, 5.0); //[cite: 1]
                    } 
                    else {
                        double adaptive_jitter = env_cfg.pulse_interval + (current_load_ratio * 0.35); //[cite: 1]
                        double safety_hold = generate_humanized_jitter(env_cfg.key_hold_base, env_cfg.key_hold_var); //[cite: 1]
                        telemetry.dispatch_hardware_stroke(0x39, safety_hold, env_cfg.key_hold_var); //[cite: 1]
                        operational_log = "[LIVE REEL] Tension: " + std::to_string(static_cast<int>(current_load_ratio)) + "% | Smooth Adaptive Rhythm.";
                        update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts, debug_mode_active);
                        telemetry.inject_delay_distribution(adaptive_jitter, 10.0);
                    }
                }
                break;
            }
        }
    }
    return 0;
}