import sys
import os
import re
from datetime import datetime
import json
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QPushButton, QLabel, QFileDialog,
                            QCheckBox, QLineEdit, QListWidget, QMessageBox,
                            QProgressBar, QComboBox, QTextEdit, QScrollArea,
                            QListWidgetItem)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCharFormat, QColor, QPixmap, QImage
import PyPDF2
import fitz  # PyMuPDF

class PDFOnizlemeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Scroll Area ve içindeki QLabel
        self.scroll_area = QScrollArea()
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setWidgetResizable(True)
        
        # Sayfa kontrolleri
        self.controls_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Önceki Sayfa")
        self.next_btn = QPushButton("Sonraki Sayfa")
        self.page_label = QLabel("Sayfa: 0/0")
        
        self.prev_btn.clicked.connect(self.prev_page)
        self.next_btn.clicked.connect(self.next_page)
        
        self.controls_layout.addWidget(self.prev_btn)
        self.controls_layout.addWidget(self.page_label)
        self.controls_layout.addWidget(self.next_btn)
        
        self.layout.addWidget(self.scroll_area)
        self.layout.addLayout(self.controls_layout)
        
        # PDF değişkenleri
        self.pdf_doc = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom = 3.0  # Sabit zoom faktörü
    
    def load_pdf(self, pdf_path):
        try:
            if self.pdf_doc:
                self.pdf_doc.close()
            
            self.pdf_doc = fitz.open(pdf_path)
            self.current_page = 0
            self.total_pages = len(self.pdf_doc)
            self.page_label.setText(f"Sayfa: 1/{self.total_pages}")
            self.show_page(0)
            return True
        except Exception as e:
            if self.pdf_doc:
                self.pdf_doc.close()
                self.pdf_doc = None
            QMessageBox.critical(None, "Hata", f"PDF yüklenirken hata oluştu: {str(e)}")
            return False
    
    def show_page(self, page_num):
        if not self.pdf_doc or page_num >= len(self.pdf_doc):
            return
        
        try:
            page = self.pdf_doc[page_num]
            # Sayfayı yüksek çözünürlükte render et
            mat = fitz.Matrix(self.zoom, self.zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # PyQt için QImage oluştur
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
            
            # QPixmap'e dönüştür
            pixmap = QPixmap.fromImage(img)
            
            # Görüntüyü pencere genişliğine göre ayarla, yüksekliği orantılı olarak değişsin
            viewport_size = self.scroll_area.viewport().size()
            scaled_pixmap = pixmap.scaledToWidth(viewport_size.width(), Qt.TransformationMode.SmoothTransformation)
            
            # Label'ı pixmap boyutuna ayarla
            self.image_label.setPixmap(scaled_pixmap)
            
            self.current_page = page_num
            self.page_label.setText(f"Sayfa: {page_num + 1}/{self.total_pages}")
            
        except Exception as e:
            QMessageBox.critical(None, "Hata", f"Sayfa görüntülenirken hata oluştu: {str(e)}")
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.pdf_doc:
            self.show_page(self.current_page)
    
    def next_page(self):
        if self.pdf_doc and self.current_page < len(self.pdf_doc) - 1:
            self.show_page(self.current_page + 1)
    
    def prev_page(self):
        if self.pdf_doc and self.current_page > 0:
            self.show_page(self.current_page - 1)
    
    def closeEvent(self, event):
        if self.pdf_doc:
            self.pdf_doc.close()
            self.pdf_doc = None
        super().closeEvent(event)

class PDFSansurleyici(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Sansürleyici")
        self.setGeometry(100, 100, 1200, 800)
        
        # Ana widget ve layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Sol panel
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        
        # PDF Yükleme Bölümü
        self.dosya_sec_btn = QPushButton("PDF Dosyası Seç")
        self.dosya_sec_btn.clicked.connect(self.pdf_sec)
        self.left_layout.addWidget(self.dosya_sec_btn)
        
        # Seçili dosya etiketi
        self.secili_dosya_label = QLabel("Seçili Dosya: ")
        self.left_layout.addWidget(self.secili_dosya_label)
        
        # Kategori Seçimleri
        self.kategoriler_grup = QWidget()
        self.kategoriler_layout = QVBoxLayout(self.kategoriler_grup)
        
        self.email_cb = QCheckBox("E-posta Adresleri")
        self.tel_cb = QCheckBox("Telefon Numaraları")
        
        self.kategoriler_layout.addWidget(self.email_cb)
        self.kategoriler_layout.addWidget(self.tel_cb)
        
        # Sansürlenecek Kelimeler Bölümü
        self.ozel_kelime_widget = QWidget()
        self.ozel_kelime_layout = QHBoxLayout(self.ozel_kelime_widget)
        
        self.ozel_kelime_input = QLineEdit()
        self.ozel_kelime_input.setPlaceholderText("Sansürlenecek kelime ekleyin...")
        self.ozel_kelime_ekle_btn = QPushButton("Ekle")
        self.ozel_kelime_sil_btn = QPushButton("Sil")
        self.ozel_kelime_ekle_btn.clicked.connect(self.ozel_kelime_ekle)
        self.ozel_kelime_sil_btn.clicked.connect(self.ozel_kelime_sil)
        
        self.ozel_kelime_layout.addWidget(self.ozel_kelime_input)
        self.ozel_kelime_layout.addWidget(self.ozel_kelime_ekle_btn)
        self.ozel_kelime_layout.addWidget(self.ozel_kelime_sil_btn)
        
        self.ozel_kelimeler_liste = QListWidget()
        
        self.kategoriler_layout.addWidget(QLabel("Sansürlenecek Kelimeler:"))
        self.kategoriler_layout.addWidget(self.ozel_kelime_widget)
        self.kategoriler_layout.addWidget(self.ozel_kelimeler_liste)
        
        self.left_layout.addWidget(self.kategoriler_grup)
        
        # Sansürleme Stilleri
        self.stil_grup = QWidget()
        self.stil_layout = QVBoxLayout(self.stil_grup)
        self.stil_layout.addWidget(QLabel("Sansürleme Stili:"))
        self.stil_combo = QComboBox()
        self.stil_combo.addItems(["Siyah Dikdörtgen", "Yıldızlama"])
        self.stil_layout.addWidget(self.stil_combo)
        self.left_layout.addWidget(self.stil_grup)
        
        # Tarama ve Sansürleme Butonları
        self.tara_btn = QPushButton("PDF'yi Tara")
        self.tara_btn.clicked.connect(self.pdf_tara)
        self.left_layout.addWidget(self.tara_btn)
        
        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.left_layout.addWidget(self.progress_bar)
        
        # Sağ panel
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        
        # PDF Önizleme
        self.pdf_preview = PDFOnizlemeWidget()
        self.right_layout.addWidget(self.pdf_preview)
        
        # Bulunan öğeler bölümü
        self.bulunan_ogeler_liste = QListWidget()
        self.bulunan_ogeler_liste.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.right_layout.addWidget(QLabel("Bulunan Öğeler:"))
        self.right_layout.addWidget(self.bulunan_ogeler_liste)
        
        # Sansürleme Butonları
        self.buton_grup = QWidget()
        self.buton_layout = QHBoxLayout(self.buton_grup)
        
        self.tumunu_sansurle_btn = QPushButton("Tümünü Sansürle")
        self.secilenleri_sansurle_btn = QPushButton("Seçilenleri Sansürle")
        self.tumunu_sansurle_btn.clicked.connect(self.tumunu_sansurle)
        self.secilenleri_sansurle_btn.clicked.connect(self.secilenleri_sansurle)
        
        self.buton_layout.addWidget(self.tumunu_sansurle_btn)
        self.buton_layout.addWidget(self.secilenleri_sansurle_btn)
        
        self.right_layout.addWidget(self.buton_grup)
        
        # Panelleri ana layout'a ekle
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.left_panel, 1)
        main_layout.addWidget(self.right_panel, 2)
        
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.layout.addWidget(main_widget)
        
        # Değişkenler
        self.pdf_dosya_yolu = None
        self.bulunan_ogeler = []

    def pdf_sec(self):
        try:
            dosya_yolu, _ = QFileDialog.getOpenFileName(
                self,
                "PDF Dosyası Seç",
                "",
                "PDF Dosyaları (*.pdf)"
            )
            
            if dosya_yolu:
                if not os.path.exists(dosya_yolu):
                    QMessageBox.critical(self, "Hata", "Seçilen dosya bulunamadı!")
                    return
                
                if not dosya_yolu.lower().endswith('.pdf'):
                    QMessageBox.critical(self, "Hata", "Lütfen geçerli bir PDF dosyası seçin!")
                    return
                
                try:
                    doc = fitz.open(dosya_yolu)
                    sayfa_sayisi = len(doc)
                    doc.close()
                    
                    self.pdf_dosya_yolu = dosya_yolu
                    self.secili_dosya_label.setText(f"Seçili Dosya: {os.path.basename(dosya_yolu)} ({sayfa_sayisi} sayfa)")
                    
                    if self.pdf_preview.load_pdf(dosya_yolu):
                        self.progress_bar.setValue(0)
                        self.bulunan_ogeler = []
                        self.bulunan_ogeler_liste.clear()
                        
                        QMessageBox.information(self, "Başarılı", f"PDF dosyası başarıyla yüklendi.\nToplam {sayfa_sayisi} sayfa.")
                    
                except Exception as e:
                    QMessageBox.critical(self, "Hata", f"PDF dosyası açılırken hata oluştu: {str(e)}")
                    return
                    
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya seçimi sırasında bir hata oluştu: {str(e)}")
            return

    def ozel_kelime_ekle(self):
        kelime = self.ozel_kelime_input.text().strip()
        if kelime:
            # Aynı kelime daha önce eklenmişse ekleme
            mevcut_kelimeler = [self.ozel_kelimeler_liste.item(i).text() 
                              for i in range(self.ozel_kelimeler_liste.count())]
            if kelime not in mevcut_kelimeler:
                item = QListWidgetItem(kelime)
                self.ozel_kelimeler_liste.addItem(item)
            self.ozel_kelime_input.clear()

    def ozel_kelime_sil(self):
        # Seçili öğeleri sil
        secili_itemler = self.ozel_kelimeler_liste.selectedItems()
        for item in secili_itemler:
            self.ozel_kelimeler_liste.takeItem(self.ozel_kelimeler_liste.row(item))

    def pdf_tara(self):
        if not self.pdf_dosya_yolu:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir PDF dosyası seçin!")
            return
        
        if not any([self.email_cb.isChecked(), self.tel_cb.isChecked(), 
                   self.ozel_kelimeler_liste.count() > 0]):
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir arama kategorisi seçin!")
            return
        
        self.bulunan_ogeler = []
        self.bulunan_ogeler_liste.clear()
        self.progress_bar.setValue(0)
        
        # Tekrar eden telefon numaralarını önlemek için set
        bulunan_telefonlar = set()
        
        try:
            doc = fitz.open(self.pdf_dosya_yolu)
            toplam_sayfa = len(doc)
            
            for sayfa_no in range(toplam_sayfa):
                sayfa = doc[sayfa_no]
                metin = sayfa.get_text()
                
                if self.email_cb.isChecked():
                    # Geliştirilmiş e-posta regex
                    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                    emailler = re.finditer(email_pattern, metin)
                    for match in emailler:
                        email = match.group()
                        self.bulunan_ogeler.append(("E-posta", email, sayfa_no))
                
                if self.tel_cb.isChecked():
                    # Geliştirilmiş telefon regex desenleri
                    telefon_patterns = [
                        r'\b(?:0|90|\+90)?[- .]?[1-9][0-9]{2}[- .]?[0-9]{3}[- .]?[0-9]{2}[- .]?[0-9]{2}\b',  # Genel format
                        r'\b(?:0|90|\+90)?[- .]?5[0-9]{2}[- .]?[0-9]{3}[- .]?[0-9]{2}[- .]?[0-9]{2}\b',  # Cep telefonu
                        r'\b[1-9][0-9]{2}[- .]?[0-9]{3}[- .]?[0-9]{2}[- .]?[0-9]{2}\b',  # Alan kodsuz
                        r'\b\+90[ ]?[1-9][0-9]{2}[ ]?[0-9]{3}[ ]?[0-9]{2}[ ]?[0-9]{2}\b',  # Uluslararası format
                        r'\b0[ ]?[1-9][0-9]{2}[ ]?[0-9]{3}[ ]?[0-9]{2}[ ]?[0-9]{2}\b'  # Başında 0 ile
                    ]
                    
                    for pattern in telefon_patterns:
                        telefonlar = re.finditer(pattern, metin)
                        for match in telefonlar:
                            telefon = match.group()
                            # Telefon numarasını temizle (boşluk ve karakterleri kaldır)
                            temiz_telefon = re.sub(r'\D', '', telefon)
                            # Başındaki 0, 90 veya +90'ı kaldır
                            if temiz_telefon.startswith('90'):
                                temiz_telefon = temiz_telefon[2:]
                            if temiz_telefon.startswith('0'):
                                temiz_telefon = temiz_telefon[1:]
                                
                            # Eğer bu telefon numarası daha önce bulunmadıysa ekle
                            if temiz_telefon not in bulunan_telefonlar:
                                bulunan_telefonlar.add(temiz_telefon)
                                # Formatlanmış telefon numarası oluştur
                                formatli_telefon = f"{temiz_telefon[:3]} {temiz_telefon[3:6]} {temiz_telefon[6:8]} {temiz_telefon[8:]}"
                                # Hem orijinal hem de formatlanmış numarayı sakla
                                self.bulunan_ogeler.append(("Telefon", formatli_telefon, sayfa_no, telefon))
                
                # Sansürlenecek kelimeleri ara
                for i in range(self.ozel_kelimeler_liste.count()):
                    kelime = self.ozel_kelimeler_liste.item(i).text()
                    pattern = re.compile(re.escape(kelime), re.IGNORECASE)
                    matches = pattern.finditer(metin)
                    for match in matches:
                        self.bulunan_ogeler.append(("Sansürlenecek Kelime", match.group(), sayfa_no))
                
                self.progress_bar.setValue(int((sayfa_no + 1) / toplam_sayfa * 100))
            
            doc.close()
            
            if self.bulunan_ogeler:
                # Bulunan öğeleri sayfaya göre sırala
                self.bulunan_ogeler.sort(key=lambda x: (x[2], x[0], x[1]))
                
                # Listeyi güncelle ve öğeleri kategorilere göre renklendir
                for item in self.bulunan_ogeler:
                    tip = item[0]
                    deger = item[1]
                    sayfa = item[2]
                    
                    list_item = QListWidgetItem(f"{tip}: {deger} (Sayfa {sayfa+1})")
                    if tip == "E-posta":
                        list_item.setForeground(QColor(0, 128, 0))  # Yeşil
                    elif tip == "Telefon":
                        list_item.setForeground(QColor(0, 0, 255))  # Mavi
                    elif tip == "Sansürlenecek Kelime":
                        list_item.setForeground(QColor(128, 0, 128))  # Mor
                    self.bulunan_ogeler_liste.addItem(list_item)
                
                QMessageBox.information(self, "Bilgi", f"Toplam {len(self.bulunan_ogeler)} öğe bulundu.")
            else:
                QMessageBox.information(self, "Bilgi", "Seçilen kriterlere uygun öğe bulunamadı.")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"PDF tarama sırasında bir hata oluştu: {str(e)}")

    def tumunu_sansurle(self):
        if not self.bulunan_ogeler:
            QMessageBox.warning(self, "Uyarı", "Sansürlenecek öğe bulunamadı!")
            return
        
        self.sansurle(self.bulunan_ogeler)

    def secilenleri_sansurle(self):
        secili_itemler = self.bulunan_ogeler_liste.selectedItems()
        if not secili_itemler:
            QMessageBox.warning(self, "Uyarı", "Lütfen sansürlenecek öğeleri seçin!")
            return
        
        secili_ogeler = []
        for item in secili_itemler:
            index = self.bulunan_ogeler_liste.row(item)
            secili_ogeler.append(self.bulunan_ogeler[index])
        
        self.sansurle(secili_ogeler)

    def sansurle(self, sansurlenecek_ogeler):
        if not self.pdf_dosya_yolu or not sansurlenecek_ogeler:
            QMessageBox.warning(self, "Uyarı", "Sansürlenecek PDF veya öğe bulunamadı!")
            return
        
        try:
            dosya_adi = os.path.splitext(self.pdf_dosya_yolu)[0]
            yeni_dosya = f"{dosya_adi}_sansurlu.pdf"
            
            doc = fitz.open(self.pdf_dosya_yolu)
            
            for sayfa_no in range(len(doc)):
                sayfa = doc[sayfa_no]
                sayfa_ogeleri = [oge for oge in sansurlenecek_ogeler if oge[2] == sayfa_no]
                
                if sayfa_ogeleri:
                    for item in sayfa_ogeleri:
                        tip = item[0]
                        deger = item[1]
                        
                        # Telefon numarası için orijinal metni kullan
                        aranacak_deger = item[3] if tip == "Telefon" and len(item) > 3 else deger
                        
                        areas = sayfa.search_for(aranacak_deger)
                        for rect in areas:
                            if self.stil_combo.currentText() == "Siyah Dikdörtgen":
                                # Siyah dikdörtgen çiz
                                sayfa.draw_rect(rect, color=(0, 0, 0), fill=(0, 0, 0))
                            else:  # Yıldızlama
                                # Beyaz arka plan
                                sayfa.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                                # Yıldızları ekle
                                yildiz = "*" * len(aranacak_deger)
                                sayfa.insert_text(rect.tl, yildiz, color=(0, 0, 0))
            
            doc.save(yeni_dosya)
            doc.close()
            
            QMessageBox.information(self, "Başarılı", f"PDF başarıyla sansürlendi ve kaydedildi:\n{yeni_dosya}")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Sansürleme işlemi sırasında bir hata oluştu: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pencere = PDFSansurleyici()
    pencere.show()
    sys.exit(app.exec())