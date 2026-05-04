import pandas as pd
import re
from transformers import pipeline

# 1. Veriyi Oku
file_path = r"C:\Users\User\OneDrive - gazi.edu.tr\Belgeler\Datasets\commits.parquet"
df = pd.read_parquet(file_path)

# Optimizasyon: Test ve prototip için şimdilik ilk 10.000 veya 100.000 satırı alalım
df = df.head(100000).copy()

# 2. Özel Temizlik Fonksiyonu (Sizin verinize özel)
def clean_commit_message(text):
    if not isinstance(text, str):
        return ""
    
    # SVN linklerini ve UUID'leri sil
    text = re.sub(r'git-svn-id:.*$', '', text, flags=re.MULTILINE)
    
    # ACCUMULO-123 gibi Jira proje kodlarını sil
    text = re.sub(r'[A-Z]+-\d+', '', text)
    
    # URL'leri sil
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Fazla boşlukları ve yeni satırları temizle
    text = re.sub(r'\s+', ' ', text).strip()
    return text

print("Metinler temizleniyor...")
df['temiz_metin'] = df['message'].apply(clean_commit_message)

# Çok kısa mesajları (örn: sadece "fix" yazanları) filtrele (En az 3 kelime olsun)
df = df[df['temiz_metin'].str.split().str.len() >= 3]

# 3. GoEmotions ile Otomatik Etiketleme (Pseudo-labeling)
# Cihazınızdaki RTX 4050'yi (device=0) kullanması için ayarlıyoruz
print("Duygu analizi (etiketleme) başlıyor. Bu işlem GPU üzerinde biraz sürebilir...")
classifier = pipeline("text-classification", model="SamLowe/roberta-base-go_emotions", device=0)

# Batch halinde tahminleme (GPU hızlandırması için)
def get_dominant_emotion(texts):
    # Truncation=True modelin maksimum sınırını aşan metinleri keser
    results = classifier(texts.tolist(), truncation=True, max_length=128, batch_size=32)
    return [res['label'] for res in results], [res['score'] for res in results]

# Çıktıları sütunlara yaz
labels, scores = get_dominant_emotion(df['temiz_metin'])
df['baskin_duygu'] = labels
df['duygu_skoru'] = scores

# 4. Burnout Analizi İçin Basitleştirme (GoEmotions'ın 28 sınıfını 3 ana sınıfa indirgeme)
# Bu sözlüğü kendi akademik tanımınıza göre genişletebilirsiniz
burnout_mapping = {
    'annoyance': 'negatif', 'anger': 'negatif', 'disapproval': 'negatif', 
    'disappointment': 'negatif', 'frustration': 'negatif', 'sadness': 'negatif',
    'stress': 'negatif', 'nervousness': 'negatif',
    'approval': 'pozitif', 'optimism': 'pozitif', 'joy': 'pozitif', 'relief': 'pozitif',
    'neutral': 'nötr'
}

# Eşleşmeyenleri şimdilik 'nötr' yapalım veya veriden çıkaralım
df['ana_kategori'] = df['baskin_duygu'].map(burnout_mapping).fillna('nötr')

# 5. İhtiyacımız Olan Sütunları Kaydet
final_df = df[['hash', 'author', 'author_time', 'temiz_metin', 'baskin_duygu', 'ana_kategori', 'duygu_skoru', 'added', 'removed']]
final_df.to_csv("commit_verisi.csv", index=False)

print("İşlem tamam! 'commit_verisi.csv' oluşturuldu.")