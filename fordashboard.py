import pandas as pd

# 1. Modelin ürettiği CSV dosyasını okutun
dosya_yolu = r"C:\Users\User\OneDrive - gazi.edu.tr\Belgeler\Developer_Burnout_Analysis\dashboard_zaman_serisi_verisi.csv"
df = pd.read_csv(dosya_yolu)

# 2. React dosyanız için gerekli olan formatta ekrana yazdırın
print("const GERCEK_ZAMAN_SERISI = [")

for index, row in df.iterrows():
    # author_time sütunu genellikle "2013-01-20 00:00:00+00:00" formatındadır, sadece tarih kısmını alalım
    tarih = str(row['author_time']).split(' ')[0] 
    risk_orani = round(row['burnout_riski_yuzdesi'], 2)
    commit_sayisi = int(row['toplam_commit'])
    
    print(f"  {{ date: '{tarih}', burnoutRisk: {risk_orani}, commitCount: {commit_sayisi} }},")

print("];")
# import pandas as pd
# import torch
# from transformers import pipeline

# print("Model yükleniyor...")
# # Kendi eğittiğimiz en iyi modeli yüklüyoruz
# model_path = "./best_burnout_roberta"
# device = 0 if torch.cuda.is_available() else -1

# # Pipeline oluştur (Eğitimdeki sınıflarla)
# classifier = pipeline("text-classification", model=model_path, tokenizer=model_path, device=device)

# # Tüm temiz veriyi yükle
# df = pd.read_csv("commit_verisi.csv")

# print(f"{len(df)} satır analiz ediliyor. RTX 4050 ile yaklaşık 5-8 dakika sürebilir...")

# # Toplu Tahminleme
# metinler = df['temiz_metin'].astype(str).tolist()
# results = classifier(metinler, truncation=True, max_length=128, batch_size=32)

# # Eğitim scriptindeki label_dict: {'nötr': 0, 'negatif': 1, 'pozitif': 2}
# # Pipeline çıktısında bunlar LABEL_0, LABEL_1, LABEL_2 olarak gelir
# id2label = {'LABEL_0': 'nötr', 'LABEL_1': 'negatif', 'LABEL_2': 'pozitif'}

# df['model_tahmini'] = [id2label.get(res['label'], res['label']) for res in results]
# df['tahmin_skoru'] = [res['score'] for res in results]

# # --- ZAMAN SERİSİ AGGREGATION (DASHBOARD İÇİN) ---
# print("Zaman serisi grafiği için veriler haftalık olarak gruplanıyor...")

# # Tarih sütununu datetime formatına çevir ve index yap
# df['author_time'] = pd.to_datetime(df['author_time'], utc=True)
# df.set_index('author_time', inplace=True)

# # Haftalık (W) bazda grupla ve o haftaki negatif/nötr/pozitif mesajların yüzdesini bul
# haftalik_trend = df.groupby(pd.Grouper(freq='W'))['model_tahmini'].value_counts(normalize=True).unstack().fillna(0) * 100

# # Bize asıl lazım olan "Negatif" (Burnout) trendi
# dashboard_df = haftalik_trend[['negatif']].copy()
# dashboard_df.rename(columns={'negatif': 'burnout_riski_yuzdesi'}, inplace=True)

# # İsteğe bağlı: O hafta toplam kaç commit atılmış (İş yükünü görmek için)
# dashboard_df['toplam_commit'] = df.groupby(pd.Grouper(freq='W')).size()

# # Sonucu kaydet
# dashboard_df.to_csv("dashboard_zaman_serisi_verisi.csv")
# print("İşlem Tamam! 'dashboard_zaman_serisi_verisi.csv' arayüz için hazır.")