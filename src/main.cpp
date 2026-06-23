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
    std::cout << OBS("==================================================\n");
    std::cout << OBS("       WINDOWS SYSTEM CORE SERVICE SUBSYSTEM       \n");
    std::cout << OBS("     Sub-Architecture: Pure Diagnostic Engine     \n");
    std::cout << OBS("==================================================\n");
    
    std::cout << OBS(" [SERVICE STATUS]  : ");
    switch (status) {
        case PipelineStatus::LIFECYCLE_STANDBY: 
            std::cout << OBS("❌ SUBSYSTEM STANDBY (Awaiting Interrupt)\n"); break;
        case PipelineStatus::LIFECYCLE_INITIALIZE_PULSE: 
            std::cout << OBS("⚡ RUNTIME - CALCULATING SYNC FRAME CHANNELS\n"); break;
        case PipelineStatus::LIFECYCLE_AWAIT_STREAM_SIGNAL: 
            std::cout << OBS("🔍 RUNTIME - LISTENING TO ASYNC MEMORY BUFFER\n"); break;
        case PipelineStatus::LIFECYCLE_PROCESS_TELEMETRY: 
            std::cout << OBS("🔥 RUNTIME - HANDLING HYSTERESIS TELEMETRY MATRIX\n"); break;
    }

    std::cout << OBS(" [DIAGNOSTIC LOGS] : ") << log_details << "\n";
    std::cout << OBS(" [PACKETS COUNTER] : ") << processed_packets << OBS(" Data Bursts Transmitted\n");
    std::cout << OBS("==================================================\n");
    std::cout << OBS(" [HARDWARE CONTROLLER INTERRUPT]:\n");
    std::cout << OBS("   * [E] Key -> Pulse Start Automation Signal Loop\n");
    std::cout << OBS("   * [X] Key -> Flush Queue Buffer & Standby Recovery\n");
    std::cout << OBS("   * [0] Key -> Terminate Thread Allocator & Safe Exit\n");
    std::cout << OBS("==================================================\n");
}

int main() {
    SetConsoleTitleA(OBS("System Windows Service Core Interface").c_str());

    EnvironmentProfile environment;
    RuntimeProfile env_cfg = environment.initialize_environment();

    TelemetryInputProcessor telemetry;
    ViewportBufferContext camera(env_cfg.buffer_width, env_cfg.buffer_height);
    SilentAPI silent_api;
    
    PipelineStatus current_lifecycle = PipelineStatus::LIFECYCLE_STANDBY;
    cv::Mat current_matrix, hsv_canvas;
    
    int successful_bursts = 0;
    std::string operational_log = OBS("Service link established. Subsystem listener armed.");

    update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts);

    INPUT pulse_down = { 0 }, pulse_up = { 0 };
    pulse_down.type = INPUT_KEYBOARD;
    pulse_down.ki.wScan = 0x39; // Spacebar scan code
    pulse_down.ki.dwFlags = KEYEVENTF_SCANCODE;

    pulse_up.type = INPUT_KEYBOARD;
    pulse_up.ki.wScan = 0x39;
    pulse_up.ki.dwFlags = KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP;

    while (true) {
        if (telemetry.intercept_hardware_state(0x30) & 0x8000) break; // '0' Key Exit

        if (telemetry.intercept_hardware_state(0x58) & 0x8000) { // 'X' Emergency Override
            if (current_lifecycle != PipelineStatus::LIFECYCLE_STANDBY) {
                silent_api.CallSendInput(1, &pulse_up, sizeof(INPUT)); 
                current_lifecycle = PipelineStatus::LIFECYCLE_STANDBY;
                operational_log = OBS("Subsystem interrupt active. Queue cleared successfully.");
                update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts);
                telemetry.inject_delay_distribution(800, 100);
                continue;
            }
        }

        switch (current_lifecycle) {
            case PipelineStatus::LIFECYCLE_STANDBY: {
                if (telemetry.intercept_hardware_state(0x45) & 0x8000) { // 'E' Key Start
                    current_lifecycle = PipelineStatus::LIFECYCLE_INITIALIZE_PULSE;
                    operational_log = OBS("Interrupt context captured. Starting sync thread tracking.");
                    update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts);
                    telemetry.inject_delay_distribution(300, 30); 
                }
                telemetry.inject_delay_distribution(30, 5); 
                break;
            }

            case PipelineStatus::LIFECYCLE_INITIALIZE_PULSE: {
                silent_api.CallSendInput(1, &pulse_down, sizeof(INPUT));
                
                int localized_target_y = -1;
                auto pulse_timer = std::chrono::steady_clock::now();
                bool pipeline_pulse_active = true;

                while (pipeline_pulse_active) {
                    if (!camera.fetch_active_matrix(current_matrix)) continue;
                    
                    cv::cvtColor(current_matrix, hsv_canvas, cv::COLOR_BGRA2BGR);
                    cv::cvtColor(hsv_canvas, hsv_canvas, cv::COLOR_BGR2HSV);

                    if (localized_target_y == -1) {
                        for (int y = 160; y <= 461; ++y) {
                            cv::Vec3b pixel = hsv_canvas.at<cv::Vec3b>(y, 255); 
                            if (pixel[0] >= 35 && pixel[0] <= 75 && pixel[1] >= 50 && pixel[2] >= 50) {
                                localized_target_y = y + 17; 
                                break;
                            }
                        }
                    }

                    if (localized_target_y != -1) {
                        for (int y = 160; y <= 461; ++y) {
                            cv::Vec3b pixel = hsv_canvas.at<cv::Vec3b>(y, 255);
                            if (pixel[2] >= 240 && pixel[1] <= 30) { 
                                if (y >= (localized_target_y - 8)) {
                                    silent_api.CallSendInput(1, &pulse_up, sizeof(INPUT)); 
                                    current_lifecycle = PipelineStatus::LIFECYCLE_AWAIT_STREAM_SIGNAL;
                                    operational_log = OBS("Pulse boundary aligned. Transitioning to stream listener.");
                                    update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts);
                                    pipeline_pulse_active = false;
                                    break;
                                }
                            }
                        }
                    }

                    if (std::chrono::duration_cast<std::chrono::seconds>(std::chrono::steady_clock::now() - pulse_timer).count() > 4) {
                        silent_api.CallSendInput(1, &pulse_up, sizeof(INPUT));
                        current_lifecycle = PipelineStatus::LIFECYCLE_INITIALIZE_PULSE; 
                        operational_log = OBS("Pulse collision verification failure. Initializing automated recovery reset...");
                        update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts);
                        telemetry.inject_delay_distribution(1500, 100);
                        telemetry.dispatch_hardware_stroke(0x12); // Send Scancode 'E' to retry
                        pipeline_pulse_active = false;
                    }
                }
                break;
            }

            case PipelineStatus::LIFECYCLE_AWAIT_STREAM_SIGNAL: {
                operational_log = OBS("Awaiting telemetry signal state validation from device kernel...");
                update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts);
                
                bool streaming_context = true;
                while (streaming_context) {
                    if (telemetry.intercept_hardware_state(0x58) & 0x8000) { streaming_context = false; break; }

                    if (!camera.fetch_active_matrix(current_matrix)) continue;
                    
                    cv::cvtColor(current_matrix, hsv_canvas, cv::COLOR_BGRA2BGR);
                    cv::cvtColor(hsv_canvas, hsv_canvas, cv::COLOR_BGR2HSV);
                    
                    cv::Vec3b telemetry_validator_pixel = hsv_canvas.at<cv::Vec3b>(683, 300); 
                    if (telemetry_validator_pixel[2] >= 200) { 
                        current_lifecycle = PipelineStatus::LIFECYCLE_PROCESS_TELEMETRY;
                        operational_log = OBS("Hardware telemetry signal validated. Pumping processing matrix.");
                        update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts);
                        streaming_context = false;
                        telemetry.inject_delay_distribution(100, 10);
                    }
                    std::this_thread::sleep_for(std::chrono::milliseconds(30)); 
                }
                break;
            }

            case PipelineStatus::LIFECYCLE_PROCESS_TELEMETRY: {
                bool synchronization_pipeline = true;

                while (synchronization_pipeline) {
                    if (telemetry.intercept_hardware_state(0x58) & 0x8000) { synchronization_pipeline = false; break; }

                    if (!camera.fetch_active_matrix(current_matrix)) continue;

                    cv::cvtColor(current_matrix, hsv_canvas, cv::COLOR_BGRA2BGR);
                    cv::cvtColor(hsv_canvas, hsv_canvas, cv::COLOR_BGR2HSV);

                    int highest_occupied_cluster_x = 187; 
                    
                    for (int x = 187; x <= 532; ++x) {
                        cv::Vec3b pixel = hsv_canvas.at<cv::Vec3b>(683, x); 
                        if (pixel[1] >= 50 && pixel[2] >= 50) { 
                            highest_occupied_cluster_x = x; 
                        }
                    }

                    double current_load_ratio = ((highest_occupied_cluster_x - 187) / 345.0) * 100.0;

                    if (current_load_ratio >= 70.0) {
                        operational_log = OBS("Buffer overload threshold hit (") + std::to_string(static_cast<int>(current_load_ratio)) + OBS("%). Suspending telemetry injector.");
                        update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts);
                        telemetry.inject_delay_distribution(120.0, 15.0);
                    } 
                    else if (current_load_ratio <= 40.0) {
                        telemetry.dispatch_hardware_stroke(0x39); 
                        operational_log = OBS("Buffer exhaustion floor matched (") + std::to_string(static_cast<int>(current_load_ratio)) + OBS("%). Accelerating injection pulse.");
                        update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts);
                        telemetry.inject_delay_distribution(env_cfg.pulse_interval, 8.0);
                    } 
                    else {
                        double humanized_jitter_delay = env_cfg.pulse_interval + (current_load_ratio * 0.4);
                        telemetry.dispatch_hardware_stroke(0x39);
                        operational_log = OBS("Subsystem load stabilizing (") + std::to_string(static_cast<int>(current_load_ratio)) + OBS("%). Maintaining telemetry current.");
                        update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts); // ✅ Nama variabel selaras
                        telemetry.inject_delay_distribution(humanized_jitter_delay, 12.0);
                    }

                    cv::Vec3b lifecycle_closure_pixel = hsv_canvas.at<cv::Vec3b>(683, 300);
                    if (lifecycle_closure_pixel[1] <= 20 && lifecycle_closure_pixel[2] <= 40) {
                        successful_bursts++;
                        current_lifecycle = PipelineStatus::LIFECYCLE_INITIALIZE_PULSE; 
                        operational_log = OBS("Data lifecycle transaction verified success! Instantiating loop iteration...");
                        update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts);
                        
                        telemetry.inject_delay_distribution(2500, 200); 
                        telemetry.dispatch_hardware_stroke(0x12);   // Autoloop stroke 'E' scan code
                        synchronization_pipeline = false;
                    }
                }
                break;
            }
        }
    }
    return 0;
}
