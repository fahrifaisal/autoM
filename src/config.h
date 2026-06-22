#pragma once
#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <algorithm>

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
    std::string file_name = "config.txt";

    // Fungsi utilitas untuk membersihkan spasi teks mentah
    std::string trim_whitespace(const std::string& str) {
        size_t first = str.find_first_not_of(" \t\r\n");
        if (first == std::string::npos) return "";
        size_t last = str.find_last_not_of(" \t\r\n");
        return str.substr(first, (last - first + 1));
    }

public:
    EngineConfig load_configuration() {
        EngineConfig config;
        std::ifstream infile(file_name);

        // Jika file tidak ditemukan, generate file default otomatis
        if (!infile.good()) {
            std::ofstream outfile(file_name);
            outfile << "# ==================================================\n";
            outfile << "#          SYSTEM CONFIGURATION PROFILE CONFIG      \n";
            outfile << "# ==================================================\n\n";
            outfile << "SCREEN_WIDTH = 1920\n";
            outfile << "SCREEN_HEIGHT = 1080\n";
            outfile << "TENSION_LOW_BOUND = 40\n";
            outfile << "TENSION_HIGH_BOUND = 65\n";
            outfile << "TARGET_CLICKS = 75\n";
            outfile << "BASE_TAP_DELAY = 98.0\n";
            outfile.close();
            return config;
        }

        std::string line;
        while (std::getline(infile, line)) {
            line = trim_whitespace(line);
            if (line.empty() || line[0] == '#') continue; // Skip baris komentar atau kosong

            std::setlocale(LC_ALL, "C");
            std::size_t delim_pos = line.find('=');
            if (delim_pos != std::string::npos) {
                std::string key = trim_whitespace(line.substr(0, delim_pos));
                std::string val = trim_whitespace(line.substr(delim_pos + 1));

                if (key == "SCREEN_WIDTH") config.screen_width = std::stoi(val);
                else if (key == "SCREEN_HEIGHT") config.screen_height = std::stoi(val);
                else if (key == "TENSION_LOW_BOUND") config.tension_low_bound = std::stoi(val);
                else if (key == "TENSION_HIGH_BOUND") config.tension_high_bound = std::stoi(val);
                else if (key == "TARGET_CLICKS") config.target_clicks = std::stoi(val);
                else if (key == "BASE_TAP_DELAY") config.base_tap_delay = std::stod(val);
            }
        }
        infile.close();
        return config;
    }
};
