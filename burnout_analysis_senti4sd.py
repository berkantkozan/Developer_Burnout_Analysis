import pandas as pd
import matplotlib.pyplot as plt

def burnout_analizi_yap(df):
    print("--- Developer Burnout Analiz Raporu ---\n")

    # 1. Genel Duygu Dağılımı
    duygu_dagilimi = df['senti4sd'].value_counts(normalize=True) * 100
    print("Genel Duygu Dağılımı (%):")
    print(duygu_dagilimi)
    print("-" * 30)

    # 2. Ürün Bazlı Negatif Duygu (Burnout Riski)
    # Negatif yorumların tüm yorumlara oranı burnout göstergesi olabilir
    urun_analizi = pd.crosstab(df['product'], df['senti4sd'], normalize='index') * 100
    
    # Negatif duyguya göre sıralayalım
    if 'negative' in urun_analizi.columns:
        burnout_siralamasi = urun_analizi.sort_values(by='negative', ascending=False)
        print("En Yüksek Burnout Riski Taşıyan Ürünler (Negatif Duygu Oranı):")
        print(burnout_siralamasi['negative'].head(10))
    
    # 3. Mesaj Uzunluğu ve Duygu İlişkisi (nchar)
    # Burnout olan kişiler bazen çok kısa ve sert, bazen çok uzun ve şikayet dolu yazabilir
    print("\nDuygu Durumuna Göre Ortalama Karakter Sayısı:")
    print(df.groupby('senti4sd')['nchar'].mean())

    return burnout_siralamasi

# Veriyi yükle
yol = r"C:\Users\User\OneDrive - gazi.edu.tr\Belgeler\Datasets\senti4sd.parquet"
df = pd.read_parquet(yol)

# Analizi çalıştır
risk_tablosu = burnout_analizi_yap(df)