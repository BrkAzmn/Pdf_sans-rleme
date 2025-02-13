# PDF Sansürleyici

PDF dosyalarında bulunan hassas bilgileri (telefon numaraları, e-posta adresleri ve özel kelimeler) tespit edip sansürlemenizi sağlayan bir masaüstü uygulaması.

## Özellikler

- PDF dosyası yükleme ve önizleme
- Hassas bilgi kategorileri:
  - Telefon numaraları (çeşitli formatlar desteklenir)
  - E-posta adresleri
  - Özel kelimeler/kelime grupları
- Sansürleme stilleri:
  - Siyah dikdörtgen
  - Yıldızlama
- Bulunan öğeleri renkli liste halinde görüntüleme
- Seçmeli veya toplu sansürleme
- %300 zoom ile yüksek çözünürlüklü önizleme
- Sayfa sayfa gezinme
- İlerleme çubuğu

## Gereksinimler

- Python 3.8 veya üzeri
- PySide6
- PyMuPDF (fitz)
- PyPDF2

## Kurulum

1. Projeyi klonlayın:
```bash
git clone https://github.com/KULLANICIADI/pdf-sansurleme.git
cd pdf-sansurleme
```

2. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

3. Uygulamayı çalıştırın:
```bash
python pdf_sansurleme.py
```

## Kullanım

1. "PDF Dosyası Seç" butonuna tıklayarak bir PDF dosyası seçin
2. Taramak istediğiniz içerik kategorilerini işaretleyin:
   - E-posta Adresleri
   - Telefon Numaraları
3. İsterseniz özel kelimeler ekleyin
4. Sansürleme stilini seçin (Siyah Dikdörtgen veya Yıldızlama)
5. "PDF'yi Tara" butonuna tıklayın
6. Bulunan öğeleri kontrol edin
7. "Tümünü Sansürle" veya "Seçilenleri Sansürle" seçeneklerinden birini kullanın
8. Sansürlenmiş PDF dosyanız otomatik olarak kaydedilecektir

## Desteklenen Formatlar

### Telefon Numaraları
- 0532 123 45 67
- +90 532 123 45 67
- 532 123 45 67
- 0532-123-45-67
- 05321234567
- ve benzeri formatlar

### E-posta Adresleri
- Standart e-posta formatları (örn: ornek@domain.com)
- Alt çizgi, nokta ve tire içeren e-postalar
- Sayı içeren e-postalar

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın. 
