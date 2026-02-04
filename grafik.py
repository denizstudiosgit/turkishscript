# ==========================================
# TurkishScript Built-in Grafik Kütüphanesi
# Geliştirici: Deniz Asaf Sayın
# ==========================================

import ctypes
from ctypes import wintypes
import os

# --- 64-BIT GÜVENLİ TİP TANIMLAMALARI ---
WPARAM = ctypes.c_uint64
LPARAM = ctypes.c_uint64
LRESULT = ctypes.c_int64
WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, WPARAM, LPARAM)

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32
comdlg32 = ctypes.windll.comdlg32

# WinAPI Fonksiyon Prototipleri
user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, WPARAM, LPARAM]
user32.DefWindowProcW.restype = LRESULT
user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, WPARAM, LPARAM]

class WNDCLASSW(ctypes.Structure):
    _fields_ = [
        ("style", wintypes.UINT), ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", ctypes.c_int), ("cbWndExtra", ctypes.c_int),
        ("hInstance", wintypes.HINSTANCE), ("hIcon", wintypes.HANDLE),
        ("hCursor", wintypes.HANDLE), ("hbrBackground", wintypes.HANDLE),
        ("lpszMenuName", wintypes.LPCWSTR), ("lpszClassName", wintypes.LPCWSTR),
    ]

# --- ANA PENCERE ---
class Pencere:
    def __init__(self, baslik="TurkishScript Grafik", genislik=600, yukseklik=400):
        self.hInstance = kernel32.GetModuleHandleW(None)
        self.className = "TS_Grafik_Sinifi"
        self.callbacks = {}
        self.wndProc = WNDPROC(self._wnd_proc)
        
        wc = WNDCLASSW()
        wc.lpfnWndProc = self.wndProc
        wc.hInstance = self.hInstance
        wc.lpszClassName = self.className
        wc.hbrBackground = gdi32.GetStockObject(0) # Beyaz Arka Plan
        wc.hCursor = user32.LoadCursorW(0, 32512)
        user32.RegisterClassW(ctypes.byref(wc))

        self.hwnd = user32.CreateWindowExW(
            0, self.className, baslik,
            0x00CF0000 | 0x10000000, 100, 100, genislik, yukseklik, 0, 0, self.hInstance, 0
        )

    def _wnd_proc(self, hwnd, msg, wParam, lParam):
        if msg == 0x0111: # WM_COMMAND
            cmd_id = wParam & 0xFFFF
            if cmd_id in self.callbacks: self.callbacks[cmd_id]()
            return 0
        if msg == 0x0002: # WM_DESTROY
            user32.PostQuitMessage(0)
            return 0
        return user32.DefWindowProcW(hwnd, msg, wParam, lParam)

    def baslat(self):
        msg = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0):
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

# --- BİLEŞENLER ---
class Etiket: # Label
    def __init__(self, pencere, metin, x, y, w=150, h=20):
        user32.CreateWindowExW(0, "STATIC", metin, 0x40000000 | 0x10000000, 
                               x, y, w, h, pencere.hwnd, 0, pencere.hInstance, 0)

class Buton:
    _id_sayac = 1000
    def __init__(self, pencere, metin, x, y, w=120, h=30, komut=None):
        self.id = Buton._id_sayac
        Buton._id_sayac += 1
        user32.CreateWindowExW(0, "BUTTON", metin, 0x40000000 | 0x10000000, 
                               x, y, w, h, pencere.hwnd, self.id, pencere.hInstance, 0)
        if komut: pencere.callbacks[self.id] = komut

class MetinKutusu: # TextBox
    def __init__(self, pencere, x, y, w=200, h=25, coklu=False):
        stil = 0x40000000 | 0x10000000 | 0x0080 
        if coklu: stil |= 0x0004 | 0x1000 | 0x00200000 
        self.hwnd = user32.CreateWindowExW(0, "EDIT", "", stil, 
                                           x, y, w, h, pencere.hwnd, 0, pencere.hInstance, 0)
    def metin_yaz(self, metin):
        user32.SetWindowTextW(self.hwnd, str(metin))
    
    def metni_al(self):
        uzunluk = user32.GetWindowTextLengthW(self.hwnd)
        tampon = ctypes.create_unicode_buffer(uzunluk + 1)
        user32.GetWindowTextW(self.hwnd, tampon, uzunluk + 1)
        return tampon.value

class OnayKutusu: # CheckBox
    _id_sayac = 2000
    def __init__(self, pencere, metin, x, y, w=150, h=20):
        self.id = OnayKutusu._id_sayac
        OnayKutusu._id_sayac += 1
        self.hwnd = user32.CreateWindowExW(0, "BUTTON", metin, 
                                           0x40000000 | 0x10000000 | 0x0003, 
                                           x, y, w, h, pencere.hwnd, self.id, pencere.hInstance, 0)
    def secili_mi(self):
        return user32.SendMessageW(self.hwnd, 0x00F0, 0, 0) == 1

# --- MENÜ SİSTEMİ ---
class MenuCubugu:
    def __init__(self, pencere):
        self.pencere = pencere
        self.hMenu = user32.CreateMenu()
        user32.SetMenu(pencere.hwnd, self.hMenu)

    def ana_baslik_ekle(self, etiket):
        hAltMenu = user32.CreatePopupMenu()
        user32.AppendMenuW(self.hMenu, 0x0010, hAltMenu, etiket)
        return hAltMenu

    def komut_ekle(self, menu, etiket, komut):
        cmd_id = Buton._id_sayac
        Buton._id_sayac += 1
        user32.AppendMenuW(menu, 0x0000, cmd_id, etiket)
        self.pencere.callbacks[cmd_id] = komut

# --- DİALOGLAR ---
class MesajKutusu:
    @staticmethod
    def goster(baslik, metin):
        user32.MessageBoxW(0, str(metin), str(baslik), 0x00000040)

class DosyaSecici:
    @staticmethod
    def dosya_ac():
        class OFN(ctypes.Structure):
            _fields_ = [("lStructSize", wintypes.DWORD), ("hwndOwner", wintypes.HWND), ("hInstance", wintypes.HINSTANCE),
                        ("lpstrFilter", wintypes.LPCWSTR), ("lpstrCustomFilter", wintypes.LPWSTR),
                        ("nMaxCustFilter", wintypes.DWORD), ("nFilterIndex", wintypes.DWORD),
                        ("lpstrFile", wintypes.LPWSTR), ("nMaxFile", wintypes.DWORD),
                        ("lpstrFileTitle", wintypes.LPWSTR), ("nMaxFileTitle", wintypes.DWORD),
                        ("lpstrInitialDir", wintypes.LPCWSTR), ("lpstrTitle", wintypes.LPCWSTR),
                        ("Flags", wintypes.DWORD), ("nFileOffset", wintypes.WORD),
                        ("nFileExtension", wintypes.WORD), ("lpstrDefExt", wintypes.LPCWSTR),
                        ("lCustData", wintypes.LPARAM), ("lpfnHook", ctypes.c_void_p),
                        ("lpTemplateName", wintypes.LPCWSTR), ("pvReserved", ctypes.c_void_p),
                        ("dwReserved", wintypes.DWORD), ("FlagsEx", wintypes.DWORD)]
        buffer = ctypes.create_unicode_buffer(260)
        ofn = OFN()
        ofn.lStructSize = ctypes.sizeof(OFN)
        ofn.lpstrFile = ctypes.cast(buffer, wintypes.LPWSTR)
        ofn.nMaxFile = 260
        ofn.lpstrFilter = "Tüm Dosyalar (*.*)\0*.*\0"
        ofn.Flags = 0x00000800 | 0x00000004
        if comdlg32.GetOpenFileNameW(ctypes.byref(ofn)): return buffer.value
        return None

class RenkSecici:
    @staticmethod
    def renk_al():
        class CHOOSECOLORW(ctypes.Structure):
            _fields_ = [("lStructSize", wintypes.DWORD), ("hwndOwner", wintypes.HWND), ("hInstance", wintypes.HINSTANCE),
                        ("rgbResult", wintypes.DWORD), ("lpCustColors", ctypes.POINTER(wintypes.DWORD)),
                        ("Flags", wintypes.DWORD), ("lCustData", wintypes.LPARAM), ("lpfnHook", ctypes.c_void_p),
                        ("lpTemplateName", wintypes.LPCWSTR)]
        cust_colors = (wintypes.DWORD * 16)()
        cc = CHOOSECOLORW()
        cc.lStructSize = ctypes.sizeof(CHOOSECOLORW)
        cc.lpCustColors = ctypes.cast(cust_colors, ctypes.POINTER(wintypes.DWORD))
        cc.Flags = 0x03
        if comdlg32.ChooseColorW(ctypes.byref(cc)):
            c = cc.rgbResult
            return (c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF)
        return None

class GirisKutusu: # InputBox
    @staticmethod
    def sor(baslik, soru):
        vbs = "temp.vbs"
        with open(vbs, "w", encoding="latin-1") as f:
            f.write(f'WScript.Echo InputBox("{soru}", "{baslik}")')
        with os.popen(f"cscript //nologo {vbs}") as f: res = f.read().strip()
        if os.path.exists(vbs): os.remove(vbs)
        return res