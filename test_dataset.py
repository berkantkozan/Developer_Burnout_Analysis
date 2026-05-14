import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

# 1. Ayarlar ve Donanım Kontrolü
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Kullanılan Cihaz: {device}")

# Daha önce eğittiğin modelin yolu (checkpoint klasörü)
MODEL_PATH = "./best_burnout_roberta" 
DATA_PATH = "commit_verisi.csv"
OUTPUT_PATH = "dashboard_ready_data.csv"

# 2. Model ve Tokenizer Yükleme
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, use_fast=False)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH).to(device)
model.eval() # Modeli değerlendirme moduna alıyoruz (dropout vb. kapanır)

# 3. Veri Seti Sınıfı (Bellek Verimliliği İçin)
class BurnoutDataset(Dataset):
    def __init__(self, texts):
        self.texts = texts

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        return str(self.texts[idx])

# 4. Veriyi Yükle
df = pd.read_csv(DATA_PATH)
# 100.000 satır sınırlaması (isteğe bağlı)
df = df.head(100000) 

texts = df['temiz_metin'].tolist() # 'text' sütun adını kendi verine göre güncelle
dataset = BurnoutDataset(texts)
# RTX 4050 için 32 batch size idealdir
dataloader = DataLoader(dataset, batch_size=32, shuffle=False)

# 5. Inference (Çıkarım) Döngüsü
all_scores = []

print("Analiz başlatılıyor...")
with torch.no_grad(): # Gradient hesaplamayı kapatıyoruz (Hız ve RAM kazancı)
    for batch in tqdm(dataloader):
        # Tokenize işlemi
        inputs = tokenizer(batch, padding=True, truncation=True, max_length=128, return_tensors="pt").to(device)
        
        # Tahmin
        outputs = model(**inputs)
        
        # Softmax ile olasılık değerlerini alıyoruz (Örn: 0: Normal, 1: Stresli)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # Stresli (1. index) olasılığını alıp listeye ekliyoruz
        stress_scores = probs[:, 1].cpu().numpy()
        all_scores.extend(stress_scores)

# 6. Sonuçları CSV Formatına Dönüştürme
df['burnout_score'] = all_scores

# Dashboard için gerekli sütunları seç ve kaydet
# Tarih, metin ve hesaplanan skor
dashboard_df = df[['author_time', 'temiz_metin', 'burnout_score']]
dashboard_df.to_csv(OUTPUT_PATH, index=False)

print(f"İşlem tamamlandı! {OUTPUT_PATH} dosyası oluşturuldu.")