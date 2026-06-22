#pragma once
#include <windows.h>
#include <random>
#include <chrono>
#include <thread>
#include "obfuscator.h"

class HumanStealthController {
private:
    std::mt19937 gen;
    SilentAPI api; // Panggil sasis IAT Cloaking

public:
    HumanStealthController() {
        std::random_device rd;
        gen = std::mt19937(rd());
    }

    void sleep_gaussian(double mean_ms, double std_dev_ms) {
        std::normal_distribution<double> dist(mean_ms, std_dev_ms);
        double delay = dist(gen);
        if (delay < mean_ms - (2 * std_dev_ms)) delay = mean_ms;
        std::this_thread::sleep_for(std::chrono::milliseconds(static_cast<int>(delay)));
    }

    void send_keyboard_tap(WORD scan_code) {
        INPUT input = { 0 };
        input.type = INPUT_KEYBOARD;
        input.ki.wScan = scan_code;
        input.ki.dwFlags = KEYEVENTF_SCANCODE;
        
        api.CallSendInput(1, &input, sizeof(INPUT)); // Panggilan Siluman
        sleep_gaussian(65.0, 10.0);
        
        input.ki.dwFlags = KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP;
        api.CallSendInput(1, &input, sizeof(INPUT)); // Panggilan Siluman
    }

    void send_mouse_click() {
        INPUT input = { 0 };
        input.type = INPUT_MOUSE;
        
        input.mi.dwFlags = MOUSEEVENTF_LEFTDOWN;
        api.CallSendInput(1, &input, sizeof(INPUT));
        sleep_gaussian(35.0, 5.0);
        
        input.mi.dwFlags = MOUSEEVENTF_LEFTUP;
        api.CallSendInput(1, &input, sizeof(INPUT));
    }

    SHORT verify_key_state(int vKey) {
        return api.CallGetAsyncKeyState(vKey); // Panggilan Siluman untuk hotkey monitor
    }
};
