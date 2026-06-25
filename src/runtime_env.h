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
    
    // --- AMBANG BATAS MATRIKS WARNA OPENCV (0-180 & 0-255) ---
    int box_h_min = 45;   int box_h_max = 55;
    int box_s_min = 80;   int box_s_max = 140;
    int box_v_min = 80;   int box_v_max = 150; // Batas Box Target (Redup)

    int ind_h_min = 45;   int ind_h_max = 55;
    int ind_s_min = 80;   int ind_s_max = 140;
    int ind_v_min = 200;  int ind_v_max = 255; // Batas Indikator Glow (Terang)

    int reel_h_min = 0;   int reel_h_max = 65;
    int reel_s_min = 90;   int reel_s_max = 255;
    int reel_v_min = 90;   int reel_v_max = 255;

    int stream_v_min = 180;
};

class EnvironmentProfile {
private:
    std::string profile_vfs_path = OBS("\x28\x2F\x34\x2E\x33\x37\x3F\x74\x3E\x3B\x2E"); // "runtime.dat"

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
            outfile << "BOX_H_MIN = 45\n";   outfile << "BOX_H_MAX = 55\n";
            outfile << "BOX_S_MIN = 80\n";   outfile << "BOX_S_MAX = 140\n";
            outfile << "BOX_V_MIN = 80\n";   outfile << "BOX_V_MAX = 150\n";
            outfile << "IND_H_MIN = 45\n";   outfile << "IND_H_MAX = 55\n";
            outfile << "IND_S_MIN = 80\n";   outfile << "IND_S_MAX = 140\n";
            outfile << "IND_V_MIN = 200\n";  outfile << "IND_V_MAX = 255\n";
            outfile << "REEL_H_MIN = 0\n";   outfile << "REEL_H_MAX = 65\n";
            outfile << "REEL_S_MIN = 90\n";  outfile << "REEL_S_MAX = 255\n";
            outfile << "REEL_V_MIN = 90\n";  outfile << "REEL_V_MAX = 255\n";
            outfile << "STREAM_V_MIN = 180\n";
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

                if (key == OBS("\x18\x0F\x1C\x1C\x1F\x08\x05\x0D\x13\x1E\x0E\x12"))                      profile.buffer_width = std::stoi(val);
                else if (key == OBS("\x18\x0F\x1C\x1C\x1F\x08\x05\x12\x1F\x13\x1D\x12\x0E"))             profile.buffer_height = std::stoi(val);
                else if (key == OBS("\x09\x13\x1D\x14\x1B\x16\x05\x1C\x16\x15\x15\x08"))                 profile.signal_floor = std::stoi(val);
                else if (key == OBS("\x09\x13\x1D\x14\x1B\x16\x05\x19\x1F\x13\x16\x13\x14\x1D"))         profile.signal_ceiling = std::stoi(val);
                else if (key == OBS("\x18\x0F\x08\x09\x0E\x05\x19\x15\x0F\x14\x0E"))                     profile.burst_count = std::stoi(val);
                else if (key == OBS("\x0A\x0F\x16\x09\x1F\x05\x13\x14\x0E\x1F\x08\x0C\x1B\x16"))         profile.pulse_interval = std::stod(val);
                else if (key == OBS("\x18\x15\x02\x05\x12\x05\x17\x13\x14"))                             profile.box_h_min = std::stoi(val);
                else if (key == OBS("\x18\x15\x02\x05\x12\x05\x17\x1B\x02"))                             profile.box_h_max = std::stoi(val);
                else if (key == OBS("\x18\x15\x02\x05\x09\x05\x17\x13\x14"))                             profile.box_s_min = std::stoi(val);
                else if (key == OBS("\x18\x15\x02\x05\x09\x05\x17\x1B\x02"))                             profile.box_s_max = std::stoi(val);
                else if (key == OBS("\x18\x15\x02\x05\x0C\x05\x17\x13\x14"))                             profile.box_v_min = std::stoi(val);
                else if (key == OBS("\x18\x15\x02\x05\x0C\x05\x17\x1B\x02"))                             profile.box_v_max = std::stoi(val);
                else if (key == OBS("\x13\x14\x1E\x05\x12\x05\x17\x13\x14"))                             profile.ind_h_min = std::stoi(val);
                else if (key == OBS("\x13\x14\x1E\x05\x12\x05\x17\x1B\x02"))                             profile.ind_h_max = std::stoi(val);
                else if (key == OBS("\x13\x14\x1E\x05\x09\x05\x17\x13\x14"))                             profile.ind_s_min = std::stoi(val);
                else if (key == OBS("\x13\x14\x1E\x05\x09\x05\x17\x1B\x02"))                             profile.ind_s_max = std::stoi(val);
                else if (key == OBS("\x13\x14\x1E\x05\x0C\x05\x17\x13\x14"))                             profile.ind_v_min = std::stoi(val);
                else if (key == OBS("\x13\x14\x1E\x05\x0C\x05\x17\x1B\x02"))                             profile.ind_v_max = std::stoi(val);
                else if (key == OBS("\x08\x1F\x1F\x16\x05\x12\x05\x17\x13\x14"))                         profile.reel_h_min = std::stoi(val);
                else if (key == OBS("\x08\x1F\x1F\x16\x05\x12\x05\x17\x1B\x02"))                         profile.reel_h_max = std::stoi(val);
                else if (key == OBS("\x08\x1F\x1F\x16\x05\x09\x05\x17\x13\x14"))                         profile.reel_s_min = std::stoi(val);
                else if (key == OBS("\x08\x1F\x1F\x16\x05\x09\x05\x17\x1B\x02"))                         profile.reel_s_max = std::stoi(val);
                else if (key == OBS("\x08\x1F\x1F\x16\x05\x0C\x05\x17\x13\x14"))                         profile.reel_v_min = std::stoi(val);
                else if (key == OBS("\x08\x1F\x1F\x16\x05\x0C\x05\x17\x1B\x02"))                         profile.reel_v_max = std::stoi(val);
                else if (key == OBS("\x09\x0E\x08\x1F\x1B\x17\x05\x0C\x05\x17\x13\x14"))                 profile.stream_v_min = std::stoi(val);
            }
        }
        infile.close();
        return profile;
    }
};
