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
    int signal_floor = 35;       
    int signal_ceiling = 68;     
    double pulse_interval = 85.0; 
    int past_brake_offset = 20; 

    double repast_delay = 2000.0;   
    double repast_var = 350.0;      
    double key_hold_base = 65.0;    
    double key_hold_var = 12.0;     
    
    int pasting_bright_v = 75;  
    int peeling_white_v = 180;   
    int tension_bright_v = 80;   
    int tension_sat_min = 75;    
    int tension_y = 558;         
    int tension_start_x = 290;   
    int tension_end_x = 540;     
    double template_threshold = 0.89; // ⚡ SUNTIKAN BARU: Batas akurasi template matching
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
            outfile << "# SYSTEM LUMINANCE SECURITY RUNTIME MATRIX\n";
            outfile << "BUFFER_WIDTH = 1920\n";
            outfile << "BUFFER_HEIGHT = 1080\n";
            outfile << "SIGNAL_FLOOR = 35\n";
            outfile << "SIGNAL_CEILING = 68\n";
            outfile << "PULSE_INTERVAL = 85.0\n";
            outfile << "PAST_BRAKE_OFFSET = 20\n";
            outfile << "REPAST_DELAY = 2000.0\n";
            outfile << "REPAST_VAR = 350.0\n";
            outfile << "KEY_HOLD_BASE = 65.0\n";
            outfile << "KEY_HOLD_VAR = 12.0\n";
            outfile << "PASTING_BRIGHT_V = 75\n";
            outfile << "PEELING_WHITE_V = 180\n";
            outfile << "TENSION_BRIGHT_V = 80\n";
            outfile << "TENSION_SAT_MIN = 75\n";
            outfile << "TENSION_Y = 558\n"; 
            outfile << "TENSION_START_X = 290\n"; 
            outfile << "TENSION_END_X = 540\n"; 
            outfile << "TEMPLATE_THRESHOLD = 0.89\n"; // Tulis otomatis baris baru
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
                else if (key == OBS("\x0A\x0F\x16\x09\x1F\x05\x13\x14\x0E\x1F\x08\x0C\x1B\x16"))         profile.pulse_interval = std::stod(val);
                else if (key == OBS("\x19\x1B\x09\x0E\x05\x18\x08\x1B\x11\x1F\x05\x15\x1C\x1C\x09\x1F\x0E")) profile.past_brake_offset = std::stoi(val);
                else if (key == OBS("\x08\x1F\x19\x1B\x09\x0E\x05\x1E\x1F\x16\x1B\x03"))                 profile.repast_delay = std::stod(val);   
                else if (key == OBS("\x08\x1F\x19\x1B\x09\x0E\x05\x0C\x1B\x08"))                         profile.repast_var = std::stod(val);     
                else if (key == OBS("\x11\x1F\x03\x05\x12\x15\x16\x1E\x05\x18\x1B\x09\x1F"))             profile.key_hold_base = std::stod(val);  
                else if (key == OBS("\x11\x1F\x03\x05\x12\x15\x16\x1E\x05\x0C\x1B\x08"))                 profile.key_hold_var = std::stod(val);   
                else if (key == OBS("\x18\x06\x16\x13\x02\x05\x0C\x05\x17\x1B\x02"))                     profile.pasting_bright_v = std::stoi(val);
                else if (key == OBS("\x17\x02\x02\x07\x02\x05\x12\x0F\x02\x1F\x05\x1D"))                 profile.peeling_white_v = std::stoi(val);
                else if (key == OBS("\x1F\x0E\x05\x16\x02\x04\x05\x09\x19\x12\x0E\x0E\x13\x05\x1D"))     profile.tension_bright_v = std::stoi(val);
                else if (key == OBS("\x1F\x0E\x05\x16\x02\x04\x05\x09\x04\x13\x03\x12\x10\x1F\x13\x1C")) profile.tension_sat_min = std::stoi(val);
                else if (key == OBS("\x1F\x0E\x05\x16\x02\x04\x05\x09\x04\x03\x1F\x1E\x0B"))             profile.tension_y = std::stoi(val); 
                else if (key == "TENSION_START_X") profile.tension_start_x = std::stoi(val);
                else if (key == "TENSION_END_X")   profile.tension_end_x = std::stoi(val);
                else if (key == "TEMPLATE_THRESHOLD") profile.template_threshold = std::stod(val); // Parsing Threshold
            }
        }
        infile.close();
        return profile;
    }
};