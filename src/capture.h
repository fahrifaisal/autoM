#pragma once
#include <windows.h>
#include <opencv2/opencv.hpp>

class DXGICaptureEngine {
private:
    int width;
    int height;
    RECT roi;

public:
    DXGICaptureEngine(int screen_w, int screen_h) : width(screen_w), height(screen_h) {
        // Tentukan batas wilayah ROI pancing secara dinamis berbasis skala resolusi
        roi.left = static_cast<long>(600 * (width / 1920.0));
        roi.top = static_cast<long>(250 * (height / 1080.0));
        roi.right = static_cast<long>(1200 * (width / 1920.0));
        roi.bottom = static_cast<long>(1050 * (height / 1080.0));
    }

    // Fungsi utilitas grabber untuk mengekstrak bitmap layar menjadi Matriks OpenCV cv::Mat
    bool grab_latest_frame(cv::Mat& output_matrix) {
        // Implementasi Win32 BitBlt / DXGI desktop duplication fall-back interface
        HDC hScreenDC = GetDC(NULL);
        HDC hMemoryDC = CreateCompatibleDC(hScreenDC);
        
        int roi_w = roi.right - roi.left;
        int roi_h = roi.bottom - roi.top;
        
        HBITMAP hBitmap = CreateCompatibleBitmap(hScreenDC, roi_w, roi_h);
        HBITMAP hOldBitmap = (HBITMAP)SelectObject(hMemoryDC, hBitmap);
        
        // Transfer biner piksel langsung dari hardware konteks device layar
        BitBlt(hMemoryDC, 0, 0, roi_w, roi_h, hScreenDC, roi.left, roi.top, SRCCOPY);
        
        // Konversi Bitmap GDI menjadi Matriks CV_8UC4 (BGRA)
        output_matrix.create(roi_h, roi_w, CV_8UC4);
        BITMAPINFOHEADER bi = { 0 };
        bi.biSize = sizeof(BITMAPINFOHEADER);
        bi.biWidth = roi_w;
        bi.biHeight = -roi_h;  // Membalik baris agar matriks terbaca top-down secara natural
        bi.biPlanes = 1;
        bi.biBitCount = 32;
        bi.biCompression = BI_RGB;
        
        GetDIBits(hMemoryDC, hBitmap, 0, roi_h, output_matrix.data, (BITMAPINFO*)&bi, DIB_RGB_COLORS);
        
        // Pembersihan resource memori GDI agar terhindar dari Memory Leak
        SelectObject(hMemoryDC, hOldBitmap);
        DeleteObject(hBitmap);
        DeleteDC(hMemoryDC);
        ReleaseDC(NULL, hScreenDC);
        
        return !output_matrix.empty();
    }
};
