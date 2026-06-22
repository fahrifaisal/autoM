#pragma once
#include <windows.h>
#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <algorithm>
#include "obfuscator.h" // Melibatkan proteksi enkripsi runtime

struct EngineConfig {
    int screen_width = 1920;
    int screen_height = 1080;
    int tension_low_bound = 40;
    int tension_high_bound = 65;
    int target_clicks = 75;
    double base_tap_delay = 98.0;
};

class ConfigManager {
private:
    // Teks asli: "config.txt" -> Di-XOR dengan 'K'
    std::string protected_file_name = OBS("\x28\x24\x25\x2D\x22\x2C\x65\x3F\x33\x3F");

    std::string trim_space_internal(const std::string& str) {
        size_t first = str.find_first_not_of(" \t\r\n");
        if (first == std::string::npos) return "";
        size_t last = str.find_last_not_of(" \t\r\n");
        return str.substr(first, (last - first + 1));
    }

public:
    EngineConfig load_configuration() {
        EngineConfig config;
        std::ifstream infile(protected_file_name);

        // Otomatisasi pembuatan file jika tidak ditemukan di direktori lokal
        if (!infile.good()) {
            std::ofstream outfile(protected_file_name);
            outfile << OBS("# SYSTEM CONFIGURATION MATRIX PROFILE\n");
            outfile << OBS("SCREEN_WIDTH = 1920\n");
            outfile << OBS("SCREEN_HEIGHT = 1080\n");
            outfile << OBS("TENSION_LOW_BOUND = 40\n");
            outfile << OBS("TENSION_HIGH_BOUND = 65\n");
            outfile << OBS("TARGET_CLICKS = 75\n");
            outfile << OBS("BASE_TAP_DELAY = 98.0\n");
            outfile.close();
            return config;
        }

        std::string line;
        while (std::getline(infile, line)) {
            line = trim_space_internal(line);
            if (line.empty() || line[0] == '#') continue;

            std::size_t delim_pos = line.find('=');
            if (delim_pos != std::string::npos) {
                std::string key = trim_space_internal(line.substr(0, delim_pos));
                std::string val = trim_space_internal(line.substr(delim_pos + 1));

                // Pencocokan kata kunci konfigurasi secara aman
                if (key == OBS("\x13\x03\x12\x05\x05\x0E\x1F\x17\x09\x04\x14\x08"))                  config.screen_width = std::stoi(val);       // SCREEN_WIDTH
                else if (key == OBS("\x13\x03\x12\x05\x05\x0E\x1F\x08\x05\x09\x07\x08\x14"))         config.screen_height = std::stoi(val);      // SCREEN_HEIGHT
                else if (key == OBS("\x14\x05\x0E\x13\x09\x0F\x0E\x1F\x0C\x0F\x17\x1F\x22\x0F\x15\x0E")) config.tension_low_bound = std::stoi(val); // TENSION_LOW_BOUND
                else if (key == OBS("\x14\x05\x0E\x13\x09\x0F\x0E\x1F\x08\x09\x07\x08\x1F\x22\x0F\x15\x0E")) config.tension_high_bound = std::stoi(val);// TENSION_HIGH_BOUND
                else if (key == OBS("\x14\x01\x12\x07\x05\x14\x1F\x03\x0C\x09\x03\x0B\x13"))         config.target_clicks = std::stoi(val);      // TARGET_CLICKS
                else if (key == OBS("\x22\x01\x13\x05\x1F\x14\x01\x10\x1F\x04\x05\x0C\x01\x19"))     config.base_tap_delay = std::stod(val);     // BASE_TAP_DELAY
            }
        }
        infile.close();
        return config;
    }
};
