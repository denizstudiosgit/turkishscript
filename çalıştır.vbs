Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

' Kullanýcýdan dosya adýný al
derlenecek = InputBox("Derlenecek .trs dosyasýnýn adýný yazýn:", "TurkishCode v5 Derleyici", "oyun.trs")

' Ýptal basýlýrsa veya boþ býrakýlýrsa çýk
If derlenecek = "" Then
    WScript.Quit
End If

' Dosya var mý kontrol et
If Not fso.FileExists(derlenecek) Then
    MsgBox "Hata: " & derlenecek & " dosyasý bulunamadý!", 16, "Dosya Yok"
    WScript.Quit
End If

' Komutu hazýrla (Sanal ortamdaki python'ý kullanarak tsm.py'yi tetikler)
' Not: /k parametresi pencereyi açýk tutar, hata varsa görmeni saðlar.
komut = "cmd /k tsm.exe " & derlenecek

' Komutu çalýþtýr
shell.Run komut, 1, True

MsgBox "Ýþlem tamamlandý!", 64, "Baþarýlý"