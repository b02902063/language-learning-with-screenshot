import win32gui
import win32ui
import win32con
import ctypes
import numpy as np
from PIL import Image
import io
import base64

def grab_window_image(title):
    hwnd = win32gui.FindWindow(None, title)
    if hwnd == 0:
        raise Exception(f"找不到視窗: {title}")

    # 獲取視窗大小
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    width = right - left
    height = bottom - top

    # 建立 DC
    hwnd_dc = win32gui.GetWindowDC(hwnd)
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()
    save_bitmap = win32ui.CreateBitmap()
    save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
    save_dc.SelectObject(save_bitmap)

    # 調用 PrintWindow
    result = ctypes.windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 1)

    # 轉為 PIL Image
    bmpinfo = save_bitmap.GetInfo()
    bmp_bytes = save_bitmap.GetBitmapBits(True)
    img = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmp_bytes, 'raw', 'BGRX', 0, 1
    )

    # 釋放
    win32gui.DeleteObject(save_bitmap.GetHandle())
    save_dc.DeleteDC()
    mfc_dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwnd_dc)

    if result != 1:
        print("[警告] PrintWindow 失敗，可能該視窗不支援。")

    # 轉為 BytesIO
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_bytes = buffer.read()

    # 編碼為 base64
    img_b64 = base64.b64encode(img_bytes).decode('utf-8')

    return img_b64

# 測試
if __name__ == "__main__":
    img = grab_window_image("記事本")  # 這裡請換成你的視窗標題
    Image.fromarray(img).show()