# -*- coding: utf-8 -*-
import re
import sys
import os
import subprocess
import urllib.request
import time
import ctypes

class TurkishCodeTranspiler:
    def __init__(self):
        self.exe_ayari = {"konsol": True, "baslik": "TurkishCode Uygulamasi"}
        
        # Derlenmiş Regex Kuralları (Hız ve Kararlılık)
        self.rules = [
            (re.compile(r'\bDOĞRU\b'), 'True'),
            (re.compile(r'\bYANLIŞ\b'), 'False'),
            (re.compile(r'\bVE\b'), 'and'),
            (re.compile(r'\bVEYA\b'), 'or'),
            (re.compile(r'\bDEĞİL\b'), 'not'),
            (re.compile(r'\bSAYI\s+(\w+)\s*='), r'\1 ='),
            (re.compile(r'\bMETİN\s+(\w+)\s*='), r'\1 ='),
            (re.compile(r'\bYAZ\s+(.+)'), r'print(\1)'),
            (re.compile(r'\bBEKLE\s+(.+)'), r'time.sleep(\1)'),
            (re.compile(r'\bDURDUR\b'), 'input("Devam etmek icin ENTER basin...")'),
            
            # Veri Okuma Komutları
            (re.compile(r'\bOKU_SAYI\b'), 'int(input())'),
            (re.compile(r'\bOKU\b'), 'input()'),
            (re.compile(r'\bYAZILACAK_YER\b'), 'input()'), 
            
            # Dosya Sistemi
            (re.compile(r'DOSYA_YAZ\s*\((.*?)\s*,\s*(.*?)\s*,\s*(.*?)\)'), 
             r'with open(\1, "w", encoding="utf-8") as f: f.write(str(\2))\nif \3: os.system("attrib +h " + \1)'),
            (re.compile(r'DOSYA_OKU\s*\((.*?)\s*,\s*(.*?)\s*\)'), 
             r'(open(\1, "r", encoding="utf-8").read(int(\2)) if str(\2).isdigit() else open(\1, "r", encoding="utf-8").read())'),
            
            # Akış Kontrolü ve Bloklar
            (re.compile(r'\bEĞER\s+(.+)'), r'if \1:'),
            (re.compile(r'\bDEĞİLSE\b'), 'else:'),
            (re.compile(r'\bTEKRAR\s+(.+)\s+KEZ\b'), r'for _ in range(\1):'),
            
            # Fonksiyon ve Sınıf Yapıları
            (re.compile(r'\bFONKSİYON\s+(\w+)\((.*)\)'), r'def \1(\2):'),
            (re.compile(r'\bDÖNDÜR\b'), 'return'),
            (re.compile(r'\bSINIF\s+(\w+)'), r'class \1:'),
            (re.compile(r'\bEVENT\s+(\w+)'), r'def event_\1():'),
            (re.compile(r'\bTETİKLE\s+(\w+)'), r'event_\1()'),
            (re.compile(r'\bDLL_Ekle\((.+)\)'), r'ctypes.CDLL(\1)')
        ]

    def transpile(self, source_code):
        py_lines = ["# -*- coding: utf-8 -*-", "import time, ctypes, sys, os, math", ""]
        girinti = 0
        ana_program_var = False

        for line in source_code.splitlines():
            raw = line.strip()
            if not raw or raw.startswith("PAKET"): continue

            # EXE Ayarları (Başlık ve Konsol)
            exe_match = re.search(r'EXE_AYARI\((.*),(.*)\)', raw)
            if exe_match:
                self.exe_ayari["konsol"] = (exe_match.group(1).strip().upper() == "DOĞRU")
                self.exe_ayari["baslik"] = exe_match.group(2).strip().strip('"\'')
                py_lines.append(f"if os.name == 'nt': os.system('title {self.exe_ayari['baslik']}')")
                continue

            # Girinti Yönetimi
            if raw == "DEĞİLSE":
                girinti = max(0, girinti - 1)
                py_lines.append("    " * girinti + "else:")
                girinti += 1
                continue
            
            if raw in ["BİTTİ", "BİTİR"]:
                girinti = max(0, girinti - 1)
                continue

            if raw == "BAŞLA":
                py_lines.append("def ana_program():")
                girinti, ana_program_var = 1, True
                continue

            # Python Dönüşümü
            processed = raw
            for pattern, repl in self.rules:
                processed = pattern.sub(repl, processed)
            
            py_lines.append("    " * girinti + processed)

            # Otomatik Girinti Artırma (Blok Sonu Kontrolü)
            if processed.endswith(":") and "else:" not in processed:
                girinti += 1

        # Program Giriş Noktası
        if ana_program_var:
            py_lines.extend(["", "if __name__ == '__main__':", "    try:", "        ana_program()", 
                             "    except Exception as e:", "        print(f'\\n[TRS HATASI]: {e}')", "        input('Kapatmak icin ENTER...')"])
        
        return "\n".join(py_lines), self.exe_ayari

def calistir():
    # Komut satırı argümanı kontrolü
    input_file = next((a for a in sys.argv if a.endswith(".trs")), None)
    if not input_file: 
        print("Kullanim: tsm.exe dosya.trs")
        return

    # Mevcut çalışma klasörünü al (EXE için kritik)
    current_dir = os.getcwd()

    if not os.path.exists(input_file):
        print(f"Hata: {input_file} dosyasi bulunamadi.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        source = f.read()

    transpiler = TurkishCodeTranspiler()
    py_code, ayar = transpiler.transpile(source)

    output_path = os.path.join(current_dir, "cikti.py")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(py_code)
    
    print("✔️ Ceviri basarili: cikti.py")
    
    # compile.bat tetikleme
    bat_path = os.path.join(current_dir, "compile.bat")
    if os.path.exists(bat_path):
        print("🚀 Derleme baslatiliyor...")
        env = os.environ.copy()
        env["EXE_KONSOL"] = "VAR" if ayar["konsol"] else "YOK"
        # shell=True Windows ortamında BAT dosyaları için zorunludur
        subprocess.run([bat_path], shell=True, env=env)
    else:
        print("⚠️ Uyari: compile.bat bulunamadigi icin EXE uretilemedi.")

if __name__ == "__main__":
    calistir()
