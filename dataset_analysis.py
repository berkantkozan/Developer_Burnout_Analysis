import pandas as pd
import os

def veri_ozetini_cikar(dosya_yolu):
    # 1. Dosya varlık kontrolü
    if not os.path.exists(dosya_yolu):
        print(f"Hata: '{dosya_yolu}' dosyası bulunamadı!")
        return

    print(f"--- {dosya_yolu} Analiz Ediliyor ---\n")

    try:
        # 2. Veriyi oku
        df = pd.read_parquet(dosya_yolu)
        
        # 3. Temel Bilgiler
        print("1. [SÜTUN İSİMLERİ]")
        print(df.columns.tolist())
        print("\n" + "-"*30)

        print("2. [VERİ TİPLERİ VE BOŞ DEĞERLER]")
        info_df = pd.DataFrame({
            'Veri Tipi': df.dtypes,
            'Eksik Değer (NaN)': df.isnull().sum(),
            'Doluluk Oranı (%)': (1 - df.isnull().sum() / len(df)) * 100
        })
        print(info_df)
        print("\n" + "-"*30)

        print("3. [İLK 5 SATIR]")
        print(df.head())

        # 4. 'description' sütunu kontrolü (Özel kontrol)
        if 'description' not in df.columns:
            print("\n!!! KRİTİK UYARI: 'description' sütunu bulunamadı!")
            # Benzer isimde sütun var mı diye bak (Büyük/küçük harf duyarlılığı için)
            benzerler = [c for c in df.columns if 'desc' in c.lower()]
            if benzerler:
                print(f"Bunu mu demek istediniz?: {benzerler}")

    except Exception as e:
        print(f"Dosya okunurken bir hata oluştu: {e}")

if __name__ == "__main__":
    # Kendi dosya yolunuzu buraya yazın
    yol = r"C:\Users\User\OneDrive - gazi.edu.tr\Belgeler\Datasets\senti4sd.parquet"
    veri_ozetini_cikar(yol)