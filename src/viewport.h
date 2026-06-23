#pragma once
#include <windows.h>
#include <opencv2/opencv.hpp>
#include "crypto_core.h"

class ViewportBufferContext {
private:
    int frame_w;
    int frame_h;
    RECT tracking_roi;

public:
    ViewportBufferContext(int width, int height) : frame_w(width), frame_h(height) {
        double factor_x = frame_w / 1920.0;
        double factor_y = frame_h / 1080.0;

        tracking_roi.left = static_cast<long>(600 * factor_x);
        tracking_roi.top = static_cast<long>(250 * factor_y);
        tracking_roi.right = static_cast<long>(1200 * factor_x);
        tracking_roi.bottom = static_cast<long>(1050 * factor_y);
    }

    bool fetch_active_matrix(cv::Mat& target_matrix) {
        HDC hScreenDC = GetDC(NULL);
        HDC hMemoryDC = CreateCompatibleDC(hScreenDC);
        
        int region_w = tracking_roi.right - tracking_roi.left;
        int region_h = tracking_roi.bottom - tracking_roi.top;
        
        HBITMAP hBitmap = CreateCompatibleBitmap(hScreenDC, region_w, region_h);
        HBITMAP hOldBitmap = (HBITMAP)SelectObject(hMemoryDC, hBitmap);
        
        BitBlt(hMemoryDC, 0, 0, region_w, region_h, hScreenDC, tracking_roi.left, tracking_roi.top, SRCCOPY);
        
        target_matrix.create(region_h, region_w, CV_8UC4);
        
        BITMAPINFOHEADER bmiHeader = { 0 };
        bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
        bmiHeader.biWidth = region_w;
        bmiHeader.biHeight = -region_h; 
        bmiHeader.biPlanes = 1;
        bmiHeader.biBitCount = 32;
        bmiHeader.biCompression = BI_RGB;
        
        GetDIBits(hMemoryDC, hBitmap, 0, region_h, target_matrix.data, (BITMAPINFO*)&bmiHeader, DIB_RGB_COLORS);
        
        SelectObject(hMemoryDC, hOldBitmap);
        DeleteObject(hBitmap);
        DeleteDC(hMemoryDC);
        ReleaseDC(NULL, hScreenDC);
        
        return !target_matrix.empty();
    }
};