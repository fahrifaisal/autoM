#pragma once
#include <windows.h>
#include <string>

// ==============================================================================
#define SYSTEM_CORE_KEY 'Z' // Mengubah kunci ke 'Z' untuk menghindari Null-Truncation
// ==============================================================================

inline std::string OBS(std::string data) {
    char key = SYSTEM_CORE_KEY; 
    for (size_t i = 0; i < data.size(); i++) {
        data[i] = data[i] ^ key;
    }
    return data;
}

class SilentAPI {
typedef SHORT(WINAPI* fnGetAsyncKeyState)(int);
typedef UINT(WINAPI* fnSendInput)(UINT, LPINPUT, int);

private:
    fnGetAsyncKeyState _GetAsyncKeyState = nullptr;
    fnSendInput _SendInput = nullptr;

public:
    SilentAPI() {
        // Teks asli: "user32.dll" -> Di-XOR dengan 'Z' 
        HMODULE hUser32 = GetModuleHandleA(OBS("\x2F\x29\x3F\x28\x69\x68\x74\x3E\x36\x36").c_str());
        if (!hUser32) {
            hUser32 = LoadLibraryA(OBS("\x2F\x29\x3F\x28\x69\x68\x74\x3E\x36\x36").c_str());
        }

        if (hUser32) {
            // Teks asli: "GetAsyncKeyState" -> Di-XOR dengan 'Z' (Bebas dari \x00)
            _GetAsyncKeyState = (fnGetAsyncKeyState)GetProcAddress(hUser32, OBS("\x1D\x3F\x2E\x1B\x29\x23\x34\x39\x11\x3F\x23\x09\x2E\x3B\x2E\x3F").c_str());
            
            // Teks asli: "SendInput" -> Di-XOR dengan 'Z'
            _SendInput = (fnSendInput)GetProcAddress(hUser32, OBS("\x09\x3F\x34\x3E\x13\x34\x2A\x2F\x2E").c_str());
        }
    }

    SHORT CallGetAsyncKeyState(int vKey) {
        if (_GetAsyncKeyState) return _GetAsyncKeyState(vKey);
        return 0;
    }

    UINT CallSendInput(UINT cInputs, LPINPUT pInputs, int cbSize) {
        if (_SendInput) return _SendInput(cInputs, pInputs, cbSize);
        return 0;
    }
};
