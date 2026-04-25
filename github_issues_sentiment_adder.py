import pandas as pd
import pyarrow.parquet as pq
import re
import torch
from transformers import pipeline

# ==========================================
# 1. VERİ KEŞFİ VE OKUMA (DATA LOADING)
# ==========================================
def veri_oku(dosya_yolu, satir_sayisi=10000):
    print(f"--- [1/4] {dosya_yolu} Okunuyor ---")
    try:
        if dosya_yolu.endswith('.parquet'):
            # Parquet dosyasını pyarrow ile tarayıp bellek dostu şekilde okuyoruz
            pf = pq.ParquetFile(dosya_yolu)
            ilk_blok = pf.read_row_group(0).to_pandas()
            df = ilk_blok.head(satir_sayisi)
        else:
            print("Lütfen .parquet uzantılı bir dosya belirtin.")
            return None
        
        print(f"Başarıyla okundu! Boyut: {df.shape}")
        return df
    except Exception as e:
        print(f"Dosya okunurken hata: {e}")
        return None

# ==========================================
# 2. VERİ ÖN İŞLEME (PREPROCESSING)
# ==========================================
def metin_temizle(text):
    text = str(text)
    # URL'leri temizle
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    # Hex kodlarını (ör: 0x4B) temizle
    text = re.sub(r'0x[0-9a-fA-F]+', '', text)
    # Birden fazla boşluğu tek boşluğa indir
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def veri_temizle(df):
    print("\n--- [2/4] Veri Temizleme ve Ön İşleme ---")
    # İşe yaramayan kolonları düşür (Bellek Optimizasyonu)
    cop_kolonlar = ['last_resolved', 'version', 'milestone', 'severity']
    df_temiz = df.drop(columns=cop_kolonlar, errors='ignore').copy()

    # Eksik metin verilerini doldur
    df_temiz['description'] = df_temiz['description'].fillna('')
    df_temiz['summary'] = df_temiz['summary'].fillna('')

    # Başlık ve içeriği tek metinde birleştir
    df_temiz['tam_metin'] = df_temiz['summary'] + " " + df_temiz['description']

    # Regex temizlik fonksiyonunu uygula
    df_temiz['temiz_metin'] = df_temiz['tam_metin'].apply(metin_temizle)
    print("Metinler URL ve gereksiz karakterlerden arındırıldı.")
    return df_temiz

# ==========================================
# 3. YAPAY ZEKA İLE DUYGU ANALİZİ (INFERENCE)
# ==========================================
def duygulari_analiz_et(df_temiz, islenecek_satir=100):
    print("\n--- [3/4] Transformer Modeli Yükleniyor ---")
    # GPU Kullanılabilirliğini Kontrol Et
    device = 0 if torch.cuda.is_available() else -1
    cihaz_adi = "GPU (CUDA Aktif)" if device == 0 else "CPU"
    print(f"Kullanılan Donanım: {cihaz_adi}")

    # RoBERTa Duygu Modelini Yükle
    duygu_analizoru = pipeline(
        task="text-classification", 
        model="SamLowe/roberta-base-go_emotions", 
        device=device,
        top_k=1 # Sadece en baskın duyguyu döndür
    )

    # Hızlı test için verinin sadece bir kısmını (örneğin 100 satır) alıyoruz
    df_sample = df_temiz.head(islenecek_satir).copy()
    print(f"\nSeçilen {islenecek_satir} satır üzerinde duygu analizi başlatılıyor...")

    def tahmin_et(metin):
        try:
            # Modelin maksimum token sınırını (512) aşmamak için ilk 500 karakteri alıyoruz
            sonuc = duygu_analizoru(metin[:500])[0][0] 
            return pd.Series([sonuc['label'], sonuc['score']])
        except Exception as e:
            return pd.Series(['hata', 0.0])

    # Analizi uygula
    df_sample[['baskin_duygu', 'duygu_skoru']] = df_sample['temiz_metin'].apply(tahmin_et)
    return df_sample

# ==========================================
# 4. ANA ÇALIŞTIRMA BLOĞU (MAIN ROUTINE)
# ==========================================
if __name__ == "__main__":
    # DİKKAT: Dosya yolunuzu buraya girin (Baştaki 'r' harfini silmeyin)
    # "C:\Users\User\OneDrive - gazi.edu.tr\Belgeler\Datasets\issues.parquet"
    dosya_yolu = r'C:\Users\User\OneDrive - gazi.edu.tr\Belgeler\Datasets\issues.parquet'
    
    
    # Adım 1: Oku
    df_ham = veri_oku(dosya_yolu, satir_sayisi=10000)
    
    if df_ham is not None:
        # Adım 2: Temizle
        df_temiz = veri_temizle(df_ham)
        
        # Adım 3: Analiz Et (Test için 100 satır işleniyor)
        df_sonuc = duygulari_analiz_et(df_temiz, islenecek_satir=100)
        
        # Adım 4: Raporla
        print("\n--- [4/4] Analiz Sonuçları Özeti ---")
        print(df_sonuc['baskin_duygu'].value_counts())
        
        print("\nÖrnek Çıktılar:")
        # Terminalde düzgün görünmesi için spesifik kolonları seçiyoruz
        display_cols = ['issue_key', 'created', 'baskin_duygu', 'duygu_skoru']
        print(df_sonuc[display_cols].head(10))
        
        # İsteğe bağlı: Sonuçları CSV'ye kaydet
        kayit_yolu = r'C:\Users\User\OneDrive - gazi.edu.tr\Belgeler\Developer_Burnout_Analysis\analiz_sonuclari.csv'
        df_sonuc.to_csv(kayit_yolu, index=False)
        print(f"\nSonuçlar başarıyla kaydedildi: {kayit_yolu}")