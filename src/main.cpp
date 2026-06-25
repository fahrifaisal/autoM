#include <iostream>
#include <string>
#include <chrono>
#include <thread>
#include <opencv2/opencv.hpp>
#include "telemetry.h"
#include "viewport.h"
#include "runtime_env.h"
#include "crypto_core.h"

enum class PipelineStatus {
    LIFECYCLE_STANDBY,
    LIFECYCLE_INITIALIZE_PULSE,
    LIFECYCLE_AWAIT_STREAM_SIGNAL,
    LIFECYCLE_PROCESS_TELEMETRY
};

void update_system_diagnostic_display(PipelineStatus status, std::string log_details, int processed_packets) {
    std::cout << "\033[H\033[J"; 
    std::cout << "==================================================\n";
    std::cout << "       WINDOWS SYSTEM CORE SERVICE SUBSYSTEM       \n";
    std::cout << "     Sub-Architecture: Pure Diagnostic Engine     \n";
    std::cout << "==================================================\n";
    
    std::cout << " [SERVICE STATUS]  : ";
    switch (status) {
        case PipelineStatus::LIFECYCLE_STANDBY: 
            std::cout << "❌ SUBSYSTEM STANDBY (Awaiting Interrupt)\n"; break;
        case PipelineStatus::LIFECYCLE_INITIALIZE_PULSE: 
            std::cout << "⚡ RUNTIME - CALCULATING SYNC FRAME CHANNELS\n"; break;
        case PipelineStatus::LIFECYCLE_AWAIT_STREAM_SIGNAL: 
            std::cout << "🔍 RUNTIME - LISTENING TO ASYNC MEMORY BUFFER\n"; break;
        case PipelineStatus::LIFECYCLE_PROCESS_TELEMETRY: 
            std::cout << "🔥 RUNTIME - HANDLING HYSTERESIS TELEMETRY MATRIX\n"; break;
    }

    std::cout << " [DIAGNOSTIC LOGS] : " << log_details << "\n";
    std::cout << " [PACKETS COUNTER] : " << processed_packets << " Data Bursts Transmitted\n";
    std::cout << "==================================================\n";
    std::cout << " [HARDWARE CONTROLLER INTERRUPT]:\n";
    std::cout << "   * [E] Key -> Pulse Start Automation Signal Loop\n";
    std::cout << "   * [X] Key -> Flush Queue Buffer & Standby Recovery\n";
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
    cv::Mat current_matrix, hsv_canvas;
    
    int successful_bursts = 0;
    std::string operational_log = "Service link established. Subsystem listener armed.";

    update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts);

    INPUT pulse_up = { 0 };
    pulse_up.type = INPUT_KEYBOARD;
    pulse_up.ki.wScan = 0x39;
    pulse_up.ki.dwFlags = KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP;

    #define CHECK_GLOBAL_INTERRUPTS() \
        if (telemetry.intercept_hardware_state(0x30) & 0x8000) { \
            silent_api.CallSendInput(1, &pulse_up, sizeof(INPUT)); \
            return 0; \
        } \
        if (telemetry.intercept_hardware_state(0x58) & 0x8000) { \
            silent_api.CallSendInput(1, &pulse_up, sizeof(INPUT)); \
            current_lifecycle = PipelineStatus::LIFECYCLE_STANDBY; \
            operational_log = "Subsystem emergency flush active. Returned to STANDBY."; \
            update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts); \
            telemetry.inject_delay_distribution(800, 100); \
            break; \
        }

    while (true) {
        if (telemetry.intercept_hardware_state(0x30) & 0x8000) break; 

        switch (current_lifecycle) {
            case PipelineStatus::LIFECYCLE_STANDBY: {
                if (telemetry.intercept_hardware_state(0x45) & 0x8000) { 
                    current_lifecycle = PipelineStatus::LIFECYCLE_INITIALIZE_PULSE;
                    operational_log = "Interrupt context captured. Starting sync thread tracking.";
                    update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts);
                    telemetry.inject_delay_distribution(300, 30); 
                }
                telemetry.inject_delay_distribution(30, 5); 
                break;
            }

            case PipelineStatus::LIFECYCLE_INITIALIZE_PULSE: {
                INPUT pulse_down = { 0 };
                pulse_down.type = INPUT_KEYBOARD;
                pulse_down.ki.wScan = 0x39;
                pulse_down.ki.dwFlags = KEYEVENTF_SCANCODE;
                silent_api.CallSendInput(1, &pulse_down, sizeof(INPUT));
                
                int localized_target_y = -1;
                auto pulse_timer = std::chrono::steady_clock::now();

                while (current_lifecycle == PipelineStatus::LIFECYCLE_INITIALIZE_PULSE) {
                    CHECK_GLOBAL_INTERRUPTS(); 

                    if (!camera.fetch_active_matrix(current_matrix)) continue;
                    
                    cv::cvtColor(current_matrix, hsv_canvas, cv::COLOR_BGRA2BGR);
                    cv::cvtColor(hsv_canvas, hsv_canvas, cv::COLOR_BGR2HSV);

                    int current_indicator_y = -1;

                    // Multi-Garis Sensor Vertikal Paralel (X=245, X=255, X=265)
                    for (int y = 160; y <= 461; ++y) {
                        cv::Vec3b p1 = hsv_canvas.at<cv::Vec3b>(y, 245);
                        cv::Vec3b p2 = hsv_canvas.at<cv::Vec3b>(y, 255); 
                        cv::Vec3b p3 = hsv_canvas.at<cv::Vec3b>(y, 265);
                        
                        // Saringan 1: Deteksi Lokasi Box Target (Redup/Pasif)
                        if (localized_target_y == -1) {
                            if ((p2[0] >= env_cfg.box_h_min && p2[0] <= env_cfg.box_h_max && p2[1] >= env_cfg.box_s_min && p2[1] <= env_cfg.box_s_max && p2[2] >= env_cfg.box_v_min && p2[2] <= env_cfg.box_v_max) ||
                                (p1[0] >= env_cfg.box_h_min && p1[0] <= env_cfg.box_h_max && p1[1] >= env_cfg.box_s_min && p1[1] <= env_cfg.box_s_max && p1[2] >= env_cfg.box_v_min && p1[2] <= env_cfg.box_v_max) ||
                                (p3[0] >= env_cfg.box_h_min && p3[0] <= env_cfg.box_h_max && p3[1] >= env_cfg.box_s_min && p3[1] <= env_cfg.box_s_max && p3[2] >= env_cfg.box_v_min && p3[2] <= env_cfg.box_v_max)) {
                                localized_target_y = y + 17; 
                            }
                        }

                        // Saringan 2: Deteksi Jarum Indikator Glow yang Sedang Bergerak (Sangat Terang)
                        if ((p2[0] >= env_cfg.ind_h_min && p2[0] <= env_cfg.ind_h_max && p2[1] >= env_cfg.ind_s_min && p2[1] <= env_cfg.ind_s_max && p2[2] >= env_cfg.ind_v_min && p2[2] <= env_cfg.ind_v_max) ||
                            (p1[0] >= env_cfg.ind_h_min && p1[0] <= env_cfg.ind_h_max && p1[1] >= env_cfg.ind_s_min && p1[1] <= env_cfg.ind_s_max && p1[2] >= env_cfg.ind_v_min && p1[2] <= env_cfg.ind_v_max) ||
                            (p3[0] >= env_cfg.ind_h_min && p3[0] <= env_cfg.ind_h_max && p3[1] >= env_cfg.ind_s_min && p3[1] <= env_cfg.ind_s_max && p3[2] >= env_cfg.ind_v_min && p3[2] <= env_cfg.ind_v_max)) {
                            current_indicator_y = y;
                        }
                    }

                    // LIVE TELEMETRY TUNING MATRIX
                    operational_log = "[TUNING CAST] Box Y: " + 
                                      (localized_target_y == -1 ? "SEARCHING" : std::to_string(localized_target_y)) + 
                                      " | Ind Y: " + (current_indicator_y == -1 ? "BLIND" : std::to_string(current_indicator_y));
                    update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts);

                    if (localized_target_y != -1 && current_indicator_y != -1) {
                        if (current_indicator_y >= (localized_target_y - 10)) { // Offset kompensasi pegas rem keyboard
                            silent_api.CallSendInput(1, &pulse_up, sizeof(INPUT)); 
                            current_lifecycle = PipelineStatus::LIFECYCLE_AWAIT_STREAM_SIGNAL;
                            operational_log = "Sync boundary locked! Advancing to stream signal tracking.";
                            update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts);
                            break; 
                        }
                    }

                    if (std::chrono::duration_cast<std::chrono::seconds>(std::chrono::steady_clock::now() - pulse_timer).count() > 4) {
                        silent_api.CallSendInput(1, &pulse_up, sizeof(INPUT));
                        current_lifecycle = PipelineStatus::LIFECYCLE_INITIALIZE_PULSE; 
                        operational_log = "Pulse verification failure. Initializing recovery reset...";
                        update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts);
                        telemetry.inject_delay_distribution(1500, 100);
                        telemetry.dispatch_hardware_stroke(0x12); 
                        break; 
                    }
                }
                break;
            }

            case PipelineStatus::LIFECYCLE_AWAIT_STREAM_SIGNAL: {
                operational_log = "Awaiting telemetry signal state validation from device kernel...";
                update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts);

                while (current_lifecycle == PipelineStatus::LIFECYCLE_AWAIT_STREAM_SIGNAL) {
                    CHECK_GLOBAL_INTERRUPTS(); 

                    if (!camera.fetch_active_matrix(current_matrix)) continue;
                    
                    cv::cvtColor(current_matrix, hsv_canvas, cv::COLOR_BGRA2BGR);
                    cv::cvtColor(hsv_canvas, hsv_canvas, cv::COLOR_BGR2HSV);
                    
                    cv::Vec3b pv1 = hsv_canvas.at<cv::Vec3b>(683, 250);
                    cv::Vec3b pv2 = hsv_canvas.at<cv::Vec3b>(683, 300);
                    cv::Vec3b pv3 = hsv_canvas.at<cv::Vec3b>(683, 350);

                    if (pv2[2] >= env_cfg.stream_v_min || pv1[2] >= env_cfg.stream_v_min || pv3[2] >= env_cfg.stream_v_min) { 
                        current_lifecycle = PipelineStatus::LIFECYCLE_PROCESS_TELEMETRY;
                        operational_log = "Hardware telemetry signal validated. Pumping processing matrix.";
                        update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts);
                        telemetry.inject_delay_distribution(100, 10);
                        break; 
                    }
                    std::this_thread::sleep_for(std::chrono::milliseconds(30)); 
                }
                break;
            }

            case PipelineStatus::LIFECYCLE_PROCESS_TELEMETRY: {
                while (current_lifecycle == PipelineStatus::LIFECYCLE_PROCESS_TELEMETRY) {
                    CHECK_GLOBAL_INTERRUPTS(); 

                    if (!camera.fetch_active_matrix(current_matrix)) continue;

                    cv::cvtColor(current_matrix, hsv_canvas, cv::COLOR_BGRA2BGR);
                    cv::cvtColor(hsv_canvas, hsv_canvas, cv::COLOR_BGR2HSV);

                    int highest_occupied_cluster_x = 187; 
                    
                    for (int x = 187; x <= 532; ++x) {
                        cv::Vec3b pixel = hsv_canvas.at<cv::Vec3b>(683, x); 
                        if (pixel[0] >= env_cfg.reel_h_min && pixel[0] <= env_cfg.reel_h_max &&
                            pixel[1] >= env_cfg.reel_s_min && pixel[2] >= env_cfg.reel_v_min) { 
                            highest_occupied_cluster_x = x; 
                        }
                    }

                    double current_load_ratio = ((highest_occupied_cluster_x - 187) / 345.0) * 100.0;

                    if (current_load_ratio >= 70.0) {
                        operational_log = "[LIVE REEL] Ratio: " + std::to_string(static_cast<int>(current_load_ratio)) + "% | Overload Danger Area!";
                        update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts);
                        telemetry.inject_delay_distribution(120.0, 15.0);
                    } 
                    else if (current_load_ratio <= 40.0) {
                        telemetry.dispatch_hardware_stroke(0x39); 
                        operational_log = "[LIVE REEL] Ratio: " + std::to_string(static_cast<int>(current_load_ratio)) + "% | Injection Pumping Base.";
                        update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts);
                        telemetry.inject_delay_distribution(env_cfg.pulse_interval, 8.0);
                    } 
                    else {
                        double humanized_jitter_delay = env_cfg.pulse_interval + (current_load_ratio * 0.4);
                        telemetry.dispatch_hardware_stroke(0x39);
                        operational_log = "[LIVE REEL] Ratio: " + std::to_string(static_cast<int>(current_load_ratio)) + "% | Stabilization Mode.";
                        update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts);
                        telemetry.inject_delay_distribution(humanized_jitter_delay, 12.0);
                    }

                    cv::Vec3b lifecycle_closure_pixel = hsv_canvas.at<cv::Vec3b>(683, 300);
                    if (lifecycle_closure_pixel[1] <= 20 && lifecycle_closure_pixel[2] <= 40) {
                        successful_bursts++;
                        current_lifecycle = PipelineStatus::LIFECYCLE_INITIALIZE_PULSE; 
                        operational_log = "Data lifecycle transaction verified success! Instantiating loop iteration...";
                        update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts);
                        
                        telemetry.inject_delay_distribution(2500, 200); 
                        telemetry.dispatch_hardware_stroke(0x12);   
                        break; 
                    }
                }
                break;
            }
        }
    }
    return 0;
}
