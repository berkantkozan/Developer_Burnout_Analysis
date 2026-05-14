import pandas as pd
import json

# 1. Dosyaları Yükle
# 'roberta_analiz_sonuclari.csv' -> Model çıktıların
# 'dengeli_commit_verisi.csv'   -> Tarih (date/author_time) bilgisini içeren orijinal dosyan
df_results = pd.read_csv("roberta_analiz_sonuclari.csv")
df_original = pd.read_csv("dengeli_commit_verisi.csv")

# 2. Tarih Bilgisini Ekle (Text üzerinden eşleştirme)
# Orijinal dosyadaki tarih kolonunun adının 'date' olduğunu varsayıyorum.
# Değilse 'author_time' vb. ile değiştirin.
df = pd.merge(df_results, df_original[['temiz_metin', 'author_time']], left_on='text', right_on='temiz_metin')

# 3. Tarih İşlemleri ve Gruplandırma
df['author_time'] = pd.to_datetime(df['author_time'])
df['week'] = df['author_time'].dt.to_period('W').apply(lambda r: r.start_time)

zaman_serisi = []

# 4. Haftalık İstatistikleri Hesapla 
for week, group in df.groupby('week'):
    total_commits = len(group)
    
    # Sadece True Negative olanları (Model doğru bildiği stresli mesajlar) al
    true_negatives = group[
        (group['predicted_label'] == 'negatif') & 
        (group['true_label'] == 'negatif')
    ]
    
    neg_count = len(true_negatives)
    
    # Formül: (Negatif İleti / Toplam İleti) * 100 
    risk_percentage = (neg_count / total_commits) * 100 if total_commits > 0 else 0
    
    zaman_serisi.append({
        "date": week.strftime('%Y-%m-%d'),
        "burnoutRisk": round(risk_percentage, 2),
        "commitCount": total_commits,
        "criticalMessages": true_negatives['text'].tolist() # Tüm mesajları dizi olarak tutar
    })

# 5. data.js Olarak Kaydet
# Not: sentimentData gibi diğer sabitleri elle ekleyebilir veya bu scripti genişletebilirsin.
js_output = f"export const ZAMAN_SERISI = {json.dumps(zaman_serisi, indent=2, ensure_ascii=False)};"

with open("data.js", "w", encoding="utf-8") as f:
    f.write(js_output)

print(f"data.js oluşturuldu! {len(zaman_serisi)} haftalık veri işlendi.")