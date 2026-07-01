#pragma once
#include <windows.h>
#include <random>
#include <chrono>
#include <thread>
#include "crypto_core.h"

class TelemetryInputProcessor {
private:
    std::mt19937 random_engine;
    SilentAPI native_link; 

public:
    TelemetryInputProcessor() {
        std::random_device rd;
        random_engine = std::mt19937(rd());
    }

    void inject_delay_distribution(double target_mean, double variance) {
        std::normal_distribution<double> dist(target_mean, variance);
        double delay = dist(random_engine);
        // Memastikan pembatas bawah rasional agar tidak menghasilkan angka minus
        if (delay < target_mean - (2.5 * variance)) delay = target_mean;
        std::this_thread::sleep_for(std::chrono::milliseconds(static_cast<int>(delay)));
    }

    // ⚡ SEKTOR MODIFIKASI: Penambahan parameter hold dinamis ber-jitter acak
    void dispatch_hardware_stroke(WORD scancode, double base_hold = 65.0, double variance = 12.0) {
        INPUT input = { 0 };
        input.type = INPUT_KEYBOARD;
        input.ki.wScan = scancode;
        input.ki.dwFlags = KEYEVENTF_SCANCODE;
        
        native_link.CallSendInput(1, &input, sizeof(INPUT)); // KEY DOWN
        inject_delay_distribution(base_hold, variance);     // JITTER DURASI HOLD TOMBOL
        
        input.ki.dwFlags = KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP;
        native_link.CallSendInput(1, &input, sizeof(INPUT)); // KEY UP
    }

    SHORT intercept_hardware_state(int vKey) {
        return native_link.CallGetAsyncKeyState(vKey); 
    }
};