#pragma once
#include <windows.h>
#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include "crypto_core.h"

struct RuntimeProfile {
    int buffer_width = 1920;
    int buffer_height = 1080;
    int signal_floor = 40;
    int signal_ceiling = 65;
    int burst_count = 75;
    double pulse_interval = 98.0;
};

class EnvironmentProfile {
private:
    // Teks asli: "runtime.dat" -> Di-XOR dengan 'Z'
    std::string profile_vfs_path = OBS("\x28\x2F\x34\x2E\x33\x37\x3F\x74\x3E\x3B\x2E");

    std::string isolate_whitespace(const std::string& str) {
        size_t first = str.find_first_not_of(" \t\r\n");
        if (first == std::string::npos) return "";
        size_t last = str.find_last_not_of(" \t\r\n");
        return str.substr(first, (last - first + 1));
    }

public:
    RuntimeProfile initialize_environment() {
        RuntimeProfile profile;
        std::ifstream infile(profile_vfs_path);

        if (!infile.good()) {
            std::ofstream outfile(profile_vfs_path);
            outfile << "# SYSTEM SECURITY ENGINE RUNTIME MATRIX\n";
            outfile << "BUFFER_WIDTH = 1920\n";
            outfile << "BUFFER_HEIGHT = 1080\n";
            outfile << "SIGNAL_FLOOR = 40\n";
            outfile << "SIGNAL_CEILING = 65\n";
            outfile << "BURST_COUNT = 75\n";
            outfile << "PULSE_INTERVAL = 98.0\n";
            outfile.close();
            return profile;
        }

        std::string line;
        while (std::getline(infile, line)) {
            line = isolate_whitespace(line);
            if (line.empty() || line[0] == '#') continue;

            std::size_t delim_pos = line.find('=');
            if (delim_pos != std::string::npos) {
                std::string key = isolate_whitespace(line.substr(0, delim_pos));
                std::string val = isolate_whitespace(line.substr(delim_pos + 1));

                // Pencocokan Array Kunci Variabel Menggunakan Pola XOR 'Z' Baru
                if (key == OBS("\x18\x0F\x1C\x1C\x1F\x08\x05\x0D\x13\x1E\x0E\x12"))                      profile.buffer_width = std::stoi(val);   // BUFFER_WIDTH
                else if (key == OBS("\x18\x0F\x1C\x1C\x1F\x08\x05\x12\x1F\x13\x1D\x12\x0E"))             profile.buffer_height = std::stoi(val);  // BUFFER_HEIGHT
                else if (key == OBS("\x09\x13\x1D\x14\x1B\x16\x05\x1C\x16\x15\x15\x08"))                 profile.signal_floor = std::stoi(val);   // SIGNAL_FLOOR
                else if (key == OBS("\x09\x13\x1D\x14\x1B\x16\x05\x19\x1F\x13\x16\x13\x14\x1D"))         profile.signal_ceiling = std::stoi(val); // SIGNAL_CEILING
                else if (key == OBS("\x18\x0F\x08\x09\x0E\x05\x19\x15\x0F\x14\x0E"))                     profile.burst_count = std::stoi(val);    // BURST_COUNT
                else if (key == OBS("\x0A\x0F\x16\x09\x1F\x05\x13\x14\x0E\x1F\x08\x0C\x1B\x16"))         profile.pulse_interval = std::stod(val); // PULSE_INTERVAL
            }
        }
        infile.close();
        return profile;
    }
};
