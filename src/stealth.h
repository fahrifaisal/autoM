#pragma once
#include <windows.h>
#include <random>
#include <chrono>
#include <thread>

class HumanStealthController {
private:
    std::mt19937 gen;

public:
    HumanStealthController() {
        std::random_device rd;
        gen = std::mt19937(rd());
    }

    // Generator delay berbasis Kurva Lonceng (Gaussian Distribution)
    void sleep_gaussian(double mean_ms, double std_dev_ms) {
        std::normal_distribution<double> dist(mean_ms, std_dev_ms);
        double delay = dist(gen);
        
        // Pencegahan nilai ekstrem atau minus
        if (delay < mean_ms - (2 * std_dev_ms)) delay = mean_ms;
        
        std::this_thread::sleep_for(std::chrono::milliseconds(static_cast<int>(delay)));
    }

    // Simulasi pengetukan tombol keyboard murni 1-PC (Metode sementara sebelum Arduino)
    void send_keyboard_tap(WORD scan_code) {
        INPUT input = { 0 };
        input.type = INPUT_KEYBOARD;
        input.ki.wScan = scan_code;
        input.ki.dwFlags = KEYEVENTF_SCANCODE;
        
        // KEY_DOWN
        SendInput(1, &input, sizeof(INPUT));
        
        // Jeda fisik pegas mekanis switch keyboard manusia (45ms - 85ms)
        sleep_gaussian(65.0, 10.0);
        
        // KEY_UP
        input.ki.dwFlags = KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP;
        SendInput(1, &input, sizeof(INPUT));
    }

    // Simulasi klik mouse murni 1-PC
    void send_mouse_click() {
        INPUT input = { 0 };
        input.type = INPUT_MOUSE;
        
        // MOUSE_DOWN
        input.mi.dwFlags = MOUSEEVENTF_LEFTDOWN;
        SendInput(1, &input, sizeof(INPUT));
        
        // Jeda waktu penekanan jari manusia saat klik (25ms - 45ms)
        sleep_gaussian(35.0, 5.0);
        
        // MOUSE_UP
        input.mi.dwFlags = MOUSEEVENTF_LEFTUP;
        SendInput(1, &input, sizeof(INPUT));
    }
};
