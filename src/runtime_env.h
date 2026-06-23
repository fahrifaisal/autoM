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
    // Teks asli: "runtime.dat" -> Di-XOR dengan 'K'
    std::string profile_vfs_path = OBS("\x39\x3E\x25\x3F\x22\x26\x2E\x6D\x2F\x30\x3F");

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
            outfile << OBS("# SYSTEM SECURITY ENGINE RUNTIME MATRIX\n");
            outfile << OBS("BUFFER_WIDTH = 1920\n");
            outfile << OBS("BUFFER_HEIGHT = 1080\n");
            outfile << OBS("SIGNAL_FLOOR = 40\n");
            outfile << OBS("SIGNAL_CEILING = 65\n");
            outfile << OBS("BURST_COUNT = 75\n");
            outfile << OBS("PULSE_INTERVAL = 98.0\n");
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

                // Mencocokkan konfigurasi menggunakan penyamaran nama variabel hardware baru
                if (key == OBS("\x09\x1E\x05\x05\x06\x19\x14\x1C\x02\x0F\x1F\x03"))                     profile.buffer_width = std::stoi(val);   // BUFFER_WIDTH
                else if (key == OBS("\x09\x1E\x05\x05\x06\x19\x14\x03\x06\x02\x0C\x03\x1F"))            profile.buffer_height = std::stoi(val);  // BUFFER_HEIGHT
                else if (key == OBS("\x14\x02\x0C\x05\x1A\x07\x14\x05\x07\x04\x04\x19"))                profile.signal_floor = std::stoi(val);   // SIGNAL_FLOOR
                else if (key == OBS("\x14\x02\x0C\x05\x1A\x07\x14\x08\x06\x02\x07\x02\x05\x0C"))        profile.signal_ceiling = std::stoi(val); // SIGNAL_CEILING
                else if (key == OBS("\x09\x1E\x19\x18\x1F\x14\x08\x04\x1E\x05\x1F"))                    profile.burst_count = std::stoi(val);    // BURST_COUNT
                else if (key == OBS("\x1B\x1E\x07\x18\x06\x14\x02\x05\x1F\x06\x19\x1D\x1A\x07"))        profile.pulse_interval = std::stod(val); // PULSE_INTERVAL
            }
        }
        infile.close();
        return profile;
    }
};