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

    // ==============================================================================
    // ⚡ INJEKSI MAKRO: INTERUPSI HOTKEY GLOBAL (ANTI-TRAPPING)
    // ==============================================================================
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
            pipeline_pulse_active = false; \
            streaming_context = false; \
            synchronization_pipeline = false; \
            break; \
        }

    while (true) {
        // Intersepsi utama saat berada di status STANDBY
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
                // Memicu alokasi HOLD Spacebar
                INPUT pulse_down = { 0 };
                pulse_down.type = INPUT_KEYBOARD;
                pulse_down.ki.wScan = 0x39;
                pulse_down.ki.dwFlags = KEYEVENTF_SCANCODE;
                silent_api.CallSendInput(1, &pulse_down, sizeof(INPUT));
                
                int localized_target_y = -1;
                auto pulse_timer = std::chrono::steady_clock::now();
                bool pipeline_pulse_active = true;

                while (pipeline_pulse_active) {
                    CHECK_GLOBAL_INTERRUPTS(); // Pastikan tombol X dan 0 bisa merespon di dalam loop ini

                    if (!camera.fetch_active_matrix(current_matrix)) continue;
                    
                    cv::cvtColor(current_matrix, hsv_canvas, cv::COLOR_BGRA2BGR);
                    cv::cvtColor(hsv_canvas, hsv_canvas, cv::COLOR_BGR2HSV);

                    // Optimasi Sensor: Scan 3 kolom paralel (X=245, 255, 265) agar tidak meleset dari box hijau
                    if (localized_target_y == -1) {
                        for (int y = 160; y <= 461; ++y) {
                            cv::Vec3b p1 = hsv_canvas.at<cv::Vec3b>(y, 245);
                            cv::Vec3b p2 = hsv_canvas.at<cv::Vec3b>(y, 255);
                            cv::Vec3b p3 = hsv_canvas.at<cv::Vec3b>(y, 265);
                            
                            if ((p2[0] >= 35 && p2[0] <= 75 && p2[1] >= 40 && p2[2] >= 40) ||
                                (p1[0] >= 35 && p1[0] <= 75 && p1[1] >= 40 && p1[2] >= 40) ||
                                (p3[0] >= 35 && p3[0] <= 75 && p3[1] >= 40 && p3[2] >= 40)) {
                                localized_target_y = y + 17; 
                                break;
                            }
                        }
                    }

                    // Melacak pergerakan jarum indikator putih/hijau terang
                    if (localized_target_y != -1) {
                        for (int y = 160; y <= 461; ++y) {
                            cv::Vec3b pixel = hsv_canvas.at<cv::Vec3b>(y, 255);
                            if (pixel[2] >= 220 && pixel[1] <= 40) { // Toleransi kecerahan indikator diperluas ke 220
                                if (y >= (localized_target_y - 10)) { // Kompensasi offset latensi disesuaikan ke 10px
                                    silent_api.CallSendInput(1, &pulse_up, sizeof(INPUT)); 
                                    current_lifecycle = PipelineStatus::LIFECYCLE_AWAIT_STREAM_SIGNAL;
                                    operational_log = "Pulse boundary aligned. Transitioning to stream listener.";
                                    update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts);
                                    pipeline_pulse_active = false;
                                    break;
                                }
                            }
                        }
                    }

                    // Timeout Guard (Batas maksimal kompilasi casting 4 detik)
                    if (std::chrono::duration_cast<std::chrono::seconds>(std::chrono::steady_clock::now() - pulse_timer).count() > 4) {
                        silent_api.CallSendInput(1, &pulse_up, sizeof(INPUT));
                        current_lifecycle = PipelineStatus::LIFECYCLE_INITIALIZE_PULSE; 
                        operational_log = "Pulse verification failure. Initializing recovery reset...";
                        update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts);
                        telemetry.inject_delay_distribution(1500, 100);
                        telemetry.dispatch_hardware_stroke(0x12); // Ketuk ulang tombol 'E' otomatis
                        pipeline_pulse_active = false;
                    }
                }
                break;
            }

            case PipelineStatus::LIFECYCLE_AWAIT_STREAM_SIGNAL: {
                bool streaming_context = true;
                while (streaming_context) {
                    CHECK_GLOBAL_INTERRUPTS(); // Mengamankan tombol X dan 0 di fase tunggu gigitan

                    if (!camera.fetch_active_matrix(current_matrix)) continue;
                    
                    cv::cvtColor(current_matrix, hsv_canvas, cv::COLOR_BGRA2BGR);
                    cv::cvtColor(hsv_canvas, hsv_canvas, cv::COLOR_BGR2HSV);
                    
                    // Verifikasi multi-titik horizontal untuk memastikan keaslian UI bar pancing bawah yang muncul
                    cv::Vec3b pv1 = hsv_canvas.at<cv::Vec3b>(683, 250);
                    cv::Vec3b pv2 = hsv_canvas.at<cv::Vec3b>(683, 300);
                    cv::Vec3b pv3 = hsv_canvas.at<cv::Vec3b>(683, 350);

                    if (pv2[2] >= 180 || pv1[2] >= 180 || pv3[2] >= 180) { 
                        current_lifecycle = PipelineStatus::LIFECYCLE_PROCESS_TELEMETRY;
                        operational_log = "Hardware telemetry signal validated. Pumping processing matrix.";
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
                    CHECK_GLOBAL_INTERRUPTS(); // Mengamankan tombol X dan 0 di loop pompa utama minigame

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
                        operational_log = "Buffer overload threshold hit (" + std::to_string(static_cast<int>(current_load_ratio)) + "%). Suspending telemetry injector.";
                        update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts);
                        telemetry.inject_delay_distribution(120.0, 15.0);
                    } 
                    else if (current_load_ratio <= 40.0) {
                        telemetry.dispatch_hardware_stroke(0x39); 
                        operational_log = "Buffer exhaustion floor matched (" + std::to_string(static_cast<int>(current_load_ratio)) + "%). Accelerating injection pulse.";
                        update_system_diagnostic_display(current_lifecycle, operational_log, successful_bursts);
                        telemetry.inject_delay_distribution(env_cfg.pulse_interval, 8.0);
                    } 
                    else {
                        double humanized_jitter_delay = env_cfg.pulse_interval + (current_load_ratio * 0.4);
                        telemetry.dispatch_hardware_stroke(0x39);
                        operational_log = "Subsystem load stabilizing (" + std::to_string(static_cast<int>(current_load_ratio)) + "%). Maintaining telemetry current.";
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
                        synchronization_pipeline = false;
                    }
                }
                break;
            }
        }
    }
    return 0;
}
