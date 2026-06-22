#include <iostream>
#include "stealth.h"
#include "capture.h"

enum class BotState {
    CASTING_INITIALIZATION,
    WAITING_FOR_BITE,
    TAPPING_MINIGAME_LOOP
};

// Konstanta ambang batas segmentasi warna HSV (Ambang Batas Gradasi Tension)
const cv::Scalar LOWER_GREEN(35, 50, 50);
const cv::Scalar UPPER_GREEN(75, 255, 255);
const cv::Scalar LOWER_RED(0, 120, 120);
const cv::Scalar UPPER_RED(10, 255, 255);

int main() {
    std::cout << "==================================================\n";
    std::cout << "     STABILIZED NATIVE C++ FISHING ENGINE V5.0    \n";
    std::cout << "==================================================\n";

    HumanStealthController stealth;
    DXGICaptureEngine camera(1920, 1080); // Mengunci resolusi dasar layar
    
    BotState current_state = BotState::CASTING_INITIALIZATION;
    cv::Mat current_frame, hsv_canvas, mask;
    
    int successful_cycles = 0;

    while (true) {
        // Validasi status interupsi tombol darurat (Tekan 'X' untuk jeda/panic breakpoint)
        if (GetAsyncKeyState(0x58) & 0x8000) {
            std::cout << "[🚨] EMERGENCY PANIC BREAKPOINT: Resetting to Idle...\n";
            current_state = BotState::CASTING_INITIALIZATION;
            stealth.sleep_gaussian(1000, 100);
            continue;
        }

        switch (current_state) {
            case BotState::CASTING_INITIALIZATION: {
                std::cout << "[⚙️] State 1: Pressing 'E' to Trigger Rod Casting...\n";
                stealth.send_keyboard_tap(0x12); // Scan code untuk tombol 'E'
                stealth.sleep_gaussian(800, 150); // Tunggu UI "Throw Line" ter-render

                std::cout << "[🕹️] Holding Click / Space to start indicator gauge...\n";
                // Kirim perintah HOLD untuk mulai menggerakkan indikator menuju green box
                INPUT input_hold = { 0 };
                input_hold.type = INPUT_MOUSE;
                input_hold.mi.dwFlags = MOUSEEVENTF_LEFTDOWN;
                SendInput(1, &input_hold, sizeof(INPUT));

                bool gauge_scanned = true;
                auto start_gauge_timer = std::chrono::steady_clock::now();

                // Loop scanning super cepat khusus mendeteksi warna hijau kotak target
                while (gauge_scanned) {
                    if (!camera.grab_latest_frame(current_frame)) continue;
                    
                    cv::cvtColor(current_frame, hsv_canvas, cv::COLOR_BGRA2BGR);
                    cv::cvtColor(hsv_canvas, hsv_canvas, cv::COLOR_BGR2HSV);
                    cv::inRange(hsv_canvas, LOWER_GREEN, UPPER_GREEN, mask);
                    
                    int green_pixel_density = cv::countNonZero(mask);
                    
                    // Jika density piksel hijau melonjak (Indikator masuk ke wilayah kotak hijau target)
                    if (green_pixel_density > 150) {
                        // Suntikkan delay waktu reaksi psikologis manusia asli (~160ms - 220ms)
                        stealth.sleep_gaussian(185.0, 15.0);
                        
                        // RELEASE tombol klik kiri secara instan
                        input_hold.mi.dwFlags = MOUSEEVENTF_LEFTUP;
                        SendInput(1, &input_hold, sizeof(INPUT));
                        
                        std::cout << "[✅] Green box matched. Finger released safely.\n";
                        current_state = BotState::WAITING_FOR_BITE;
                        gauge_scanned = false;
                    }

                    // Proteksi jika gagal mendeteksi agar tidak hang/stuck
                    if (std::chrono::duration_cast<std::chrono::seconds>(std::chrono::steady_clock::now() - start_gauge_timer).count() > 4) {
                        input_hold.mi.dwFlags = MOUSEEVENTF_LEFTUP;
                        SendInput(1, &input_hold, sizeof(INPUT));
                        gauge_scanned = false;
                    }
                }
                break;
            }

            case BotState::WAITING_FOR_BITE: {
                std::cout << "[💤] State 2: Standing by. Scanning for 'Click Fast!' UI Overlay...\n";
                bool waiting_bite = true;
                
                while (waiting_bite) {
                    if (!camera.grab_latest_frame(current_frame)) continue;
                    
                    // Logika pendeteksian teks UI putih/merah "Click Fast!" diletakkan di sini
                    // Menggunakan teknik pemicu deteksi warna piksel horizontal untuk efisiensi
                    bool text_ui_found = false; 
                    
                    // Simulasi pemicu transisi (Aktualnya dibaca via deteksi kontur box teks)
                    stealth.sleep_gaussian(2000, 100); 
                    text_ui_found = true; 

                    if (text_ui_found) {
                        current_state = BotState::TAPPING_MINIGAME_LOOP;
                        waiting_bite = false;
                    }
                }
                break;
            }

            case BotState::TAPPING_MINIGAME_LOOP: {
                std::cout << "[🔥] State 3: Active 'Click Fast!' Minigame Secured.\n";
                bool minigame_running = true;
                int dynamic_click_count = 0;

                while (minigame_running) {
                    if (!camera.grab_latest_frame(current_frame)) continue;
                    
                    // Hitung nilai persentase Line Tension dari bar gradasi hijau->merah
                    // Kita memetakan rasio horizontal piksel merah terisi dalam ROI Tension Bar
                    int simulated_tension_percentage = 35; // Placeholder pembacaan matriks

                    if (simulated_tension_percentage < 40) {
                        // Hitung faktor kelelahan jari logaritmik manusia (Fatigue Model)
                        double fatigue_extension = dynamic_click_count * 0.45;
                        double humanized_tap_delay = 98.0 + fatigue_extension;
                        
                        stealth.send_keyboard_tap(0x39); // Ketuk tombol SPACE BAR (Scan code: 0x39)
                        stealth.sleep_gaussian(humanized_tap_delay, 12.0);
                        
                        dynamic_click_count++;
                    } 
                    else if (simulated_tension_percentage > 65) {
                        // Jari diangkat secara asimetris memberi waktu tegangan senar pancing turun
                        std::cout << "[⚠️] Line Tension high! Releasing keys temporarily...\n";
                        stealth.sleep_gaussian(380.0, 35.0);
                    }

                    // Keluar dari loop jika minigame selesai (UI menghilang dari canvas layar)
                    if (dynamic_click_count >= 75) { 
                        minigame_running = false;
                    }
                }

                successful_cycles++;
                std::cout << "[🎉] Target fish secured to bag. Total Success: " << successful_cycles << "\n";
                current_state = BotState::CASTING_INITIALIZATION; // Lakukan auto-loop kembali ke Fase 1
                
                // Jeda relaksasi tangan sebelum siklus lemparan pancing baru dimulai kembali
                stealth.sleep_gaussian(2500, 300);
                break;
            }
        }
    }
    return 0;
}
