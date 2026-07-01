#pragma once
#include <windows.h>
#include <opencv2/opencv.hpp>
#include "crypto_core.h"

class ViewportBufferContext {
private:
    int frame_w;
    int frame_h;
    RECT tracking_roi;
    HDC hScreenDC;
    HDC hMemoryDC;
    HBITMAP hBitmap;
    HBITMAP hOldBitmap;
    int region_w;
    int region_h;
    BITMAPINFO bmi;

public:
    ViewportBufferContext(int width, int height) : frame_w(width), frame_h(height) {
        double factor_x = frame_w / 1920.0;
        double factor_y = frame_h / 1080.0;

        tracking_roi.left = static_cast<long>(500 * factor_x);
        tracking_roi.top = static_cast<long>(380 * factor_y);
        tracking_roi.right = static_cast<long>(1400 * factor_x);
        tracking_roi.bottom = static_cast<long>(1080 * factor_y); // ⚡ MUTAKHIR: Diturunkan ke 1080 penuh agar HUD bawah terlihat

        region_w = tracking_roi.right - tracking_roi.left;
        region_h = tracking_roi.bottom - tracking_roi.top;

        hScreenDC = GetDC(NULL);
        hMemoryDC = CreateCompatibleDC(hScreenDC);
        hBitmap = CreateCompatibleBitmap(hScreenDC, region_w, region_h);
        hOldBitmap = (HBITMAP)SelectObject(hMemoryDC, hBitmap);

        ZeroMemory(&bmi, sizeof(BITMAPINFO));
        bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
        bmi.bmiHeader.biWidth = region_w;
        bmi.bmiHeader.biHeight = -region_h; 
        bmi.bmiHeader.biPlanes = 1;
        bmi.bmiHeader.biBitCount = 32;
        bmi.bmiHeader.biCompression = BI_RGB;
    }

    ~ViewportBufferContext() {
        SelectObject(hMemoryDC, hOldBitmap);
        DeleteObject(hBitmap);
        DeleteDC(hMemoryDC);
        ReleaseDC(NULL, hScreenDC);
    }

    bool fetch_active_matrix(cv::Mat& target_matrix) {
        BitBlt(hMemoryDC, 0, 0, region_w, region_h, hScreenDC, tracking_roi.left, tracking_roi.top, SRCCOPY);
        target_matrix.create(region_h, region_w, CV_8UC4);
        GetDIBits(hMemoryDC, hBitmap, 0, region_h, target_matrix.data, &bmi, DIB_RGB_COLORS);
        return !target_matrix.empty();
    }
};