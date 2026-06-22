#pragma once
#include <windows.h>
#include <string>

// ==============================================================================
// INTERNAL ENCRYPTION ENGINE: LIGHTWEIGHT RUNTIME XOR
// ==============================================================================
inline std::string OBS(std::string data) {
    // Kunci enkripsi XOR (Bisa Anda ganti dengan karakter bebas apa saja)
    char key = 'K'; 
    for (size_t i = 0; i < data.size(); i++) {
        data[i] = data[i] ^ key;
    }
    return data;
}

// ==============================================================================
// SILENT WIN32 API LINKER (IAT CLOAKING ENGINE)
// ==============================================================================
class SilentAPI {
typedef SHORT(WINAPI* fnGetAsyncKeyState)(int);
typedef UINT(WINAPI* fnSendInput)(UINT, LPINPUT, int);

private:
    fnGetAsyncKeyState _GetAsyncKeyState = nullptr;
    fnSendInput _SendInput = nullptr;

public:
    SilentAPI() {
        // Memuat modul secara dinamis menggunakan string yang dienkripsi XOR
        // Teks asli: "user32.dll" -> Enkripsi XOR 'K' -> "\x1D\x3B\x3D\x3A\x3B\x2A\x66\x2C\x24\x24"
        HMODULE hUser32 = GetModuleHandleA(OBS("\x1D\x3B\x3D\x3A\x3B\x2A\x66\x2C\x24\x24").c_str());
        if (!hUser32) {
            hUser32 = LoadLibraryA(OBS("\x1D\x3B\x3D\x3A\x3B\x2A\x66\x2C\x24\x24").c_str());
        }

        if (hUser32) {
            // Mengambil pointer fungsi langsung dari memori tanpa mendaftarkannya ke IAT
            // Teks asli: "GetAsyncKeyState"
            _GetAsyncKeyState = (fnGetAsyncKeyState)GetProcAddress(hUser32, OBS("\x2D\x2D\x3C\x0F\x2D\x31\x13\x3D\x31\x33\x3B\x3B\x1F\x33\x3B\x3D").c_str());
            // Teks asli: "SendInput"
            _SendInput = (fnSendInput)GetProcAddress(hUser32, OBS("\x3D\x3D\x26\x2C\x01\x26\x38\x3D\x3C").c_str());
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
