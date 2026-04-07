# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
import os
import sys

class TurkishCodeIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("TurkishCode Pro IDE - tsm.exe Builder")
        self.root.geometry("1000x700")
        self.root.configure(bg="#1e1e1e")

        # Sabit dosya adı
        self.proje_dosyasi = "kayitli_proje.trs"

        # Üst Panel (Toolbar)
        self.toolbar = tk.Frame(self.root, bg="#2d2d2d", pady=5)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # Çalıştır Butonu
        self.btn_run = tk.Button(self.toolbar, text="▶ DERLE VE ÇALIŞTIR", 
                                 bg="#2ea043", fg="white", 
                                 font=("Segoe UI", 10, "bold"), 
                                 command=self.run_tsm)
        self.btn_run.pack(side=tk.LEFT, padx=10)

        # Bilgi Etiketi
        self.lbl_info = tk.Label(self.toolbar, text=f"Dosya: {self.proje_dosyasi}", 
                                 bg="#2d2d2d", fg="#8b949e", font=("Segoe UI", 9))
        self.lbl_info.pack(side=tk.LEFT, padx=10)

        # Kod Editörü (Üst Kısım)
        self.txt_editor = scrolledtext.ScrolledText(self.root, bg="#1e1e1e", fg="#d4d4d4", 
                                                   insertbackground="white", 
                                                   font=("Consolas", 13), undo=True)
        self.txt_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Konsol/Log Alanı (Alt Kısım)
        self.txt_console = scrolledtext.ScrolledText(self.root, height=12, bg="#000000", 
                                                    fg="#00ff00", font=("Consolas", 10))
        self.txt_console.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)
        self.log(">>> IDE Hazır. tsm.exe bekleniyor...")

        # Başlangıçta örnek kod ekle
        if not os.path.exists(self.proje_dosyasi):
            ornek_kod = 'BAŞLA\n    YAZ "Merhaba Dünya!"\n    SAYI x = 5\n    TEKRAR x KEZ\n        YAZ "Döngü çalışıyor..."\n    BİTİR\nBİTTİ'
            self.txt_editor.insert(tk.END, ornek_kod)
        else:
            with open(self.proje_dosyasi, "r", encoding="utf-8") as f:
                self.txt_editor.insert(tk.END, f.read())

    def log(self, msg):
        self.txt_console.config(state=tk.NORMAL)
        self.txt_console.insert(tk.END, msg + "\n")
        self.txt_console.see(tk.END)
        self.txt_console.config(state=tk.DISABLED)

    def run_tsm(self):
        # 1. Adım: Editördeki içeriği kayitli_proje.trs olarak kaydet
        content = self.txt_editor.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Uyarı", "Boş kodu derleyemezsin!")
            return

        try:
            with open(self.proje_dosyasi, "w", encoding="utf-8") as f:
                f.write(content)
            self.log(f"📝 {self.proje_dosyasi} güncellendi.")
        except Exception as e:
            self.log(f"❌ Dosya yazma hatası: {e}")
            return

        # 2. Adım: tsm.exe dosyasının varlığını kontrol et
        if not os.path.exists("tsm.exe"):
            self.log("⚠️ Hata: tsm.exe bulunamadı! Lütfen derleyiciyi bu klasöre koy.")
            messagebox.showerror("Eksik Dosya", "tsm.exe ana dizinde bulunamadı.")
            return

        # 3. Adım: tsm.exe <dosya>.trs komutunu çalıştır
        self.log(f"🚀 Komut çalışıyor: tsm.exe {self.proje_dosyasi}")
        
        try:
            # shell=True ile tsm.exe'yi tetikliyoruz
            process = subprocess.Popen(["tsm.exe", self.proje_dosyasi], 
                                       stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE, 
                                       text=True, 
                                       encoding="utf-8")
            
            stdout, stderr = process.communicate()

            if stdout:
                self.log(f"[TSM ÇIKTISI]:\n{stdout}")
            if stderr:
                self.log(f"[TSM HATASI]:\n{stderr}")
            
            self.log("✅ İşlem tamamlandı.\n" + "-"*30)
            
        except Exception as e:
            self.log(f"❌ Çalıştırma Hatası: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    # Pencereyi ekranın ortasında açma
    app = TurkishCodeIDE(root)
    root.mainloop()