#pragma once
#include <windows.h>
#include <opencv2/opencv.hpp>
#include "obfuscator.h"

class DXGICaptureEngine {
private:
    int screen_w;
    int screen_h;
    RECT bounding_roi;

public:
    DXGICaptureEngine(int width, int height) : screen_w(width), height(height) {
        // Kalkulasi wilayah isolasi kotak pancing (ROI) berbasis rasio resolusi monitor target
        double scale_multiplier_x = screen_w / 1920.0;
        double scale_multiplier_y = screen_h / 1080.0;

        bounding_roi.left = static_cast<long>(600 * scale_multiplier_x);
        bounding_roi.top = static_cast<long>(250 * scale_multiplier_y);
        bounding_roi.right = static_cast<long>(1200 * scale_multiplier_x);
        bounding_roi.bottom = static_cast<long>(1050 * scale_multiplier_y);
    }

    bool grab_latest_frame(cv::Mat& output_matrix) {
        // Interfasi penangkapan tingkat rendah Windows GDI Engine
        HDC hScreenDC = GetDC(NULL);
        HDC hMemoryDC = CreateCompatibleDC(hScreenDC);
        
        int region_width = bounding_roi.right - bounding_roi.left;
        int region_height = bounding_roi.bottom - bounding_roi.top;
        
        HBITMAP hBitmap = CreateCompatibleBitmap(hScreenDC, region_width, region_height);
        HBITMAP hOldBitmap = (HBITMAP)SelectObject(hMemoryDC, hBitmap);
        
        // Transfer bit fisik matriks gambar langsung dari kartu grafis aktif
        BitBlt(hMemoryDC, 0, 0, region_width, region_height, hScreenDC, bounding_roi.left, bounding_roi.top, SRCCOPY);
        
        // Alokasikan dimensi internal matriks OpenCV sebagai penampung data 4-Channel (BGRA)
        output_matrix.create(region_height, region_width, CV_8UC4);
        
        BITMAPINFOHEADER bmiHeader = { 0 };
        bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
        bmiHeader.biWidth = region_width;
        bmiHeader.biHeight = -region_height; // Format negatif memaksa pembacaan top-down koordinat piksel
        bmiHeader.biPlanes = 1;
        bmiHeader.biBitCount = 32;
        bmiHeader.biCompression = BI_RGB;
        
        // Salin susunan bit biner memori GDI ke pointer array data mentah OpenCV
        GetDIBits(hMemoryDC, hBitmap, 0, region_height, output_matrix.data, (BITMAPINFO*)&bmiHeader, DIB_RGB_COLORS);
        
        // ==============================================================================
        // CRITICAL CLEANUP: DE-ALOKASI DAN PEMBERSIHAN RESOURCE MEMORI DEVICE CONTEXT
        // ==============================================================================
        SelectObject(hMemoryDC, hOldBitmap);
        DeleteObject(hBitmap);
        DeleteDC(hMemoryDC);
        ReleaseDC(NULL, hScreenDC);
        
        return !output_matrix.empty();
    }
};
