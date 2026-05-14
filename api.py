from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import pandas as pd
import sys
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("api_key")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Groq API Key'in başında ve sonunda boşluk kalmadığından emin ol
client = Groq(api_key=api_key)

class WeeklyAnalysisRequest(BaseModel):
    messages: list[str]

@app.post("/analyze-weekly-burnout")
async def analyze_weekly(request: WeeklyAnalysisRequest):
    # 'flush=True' sayesinde printler terminalde anında görünür
    print(f"\n>>> YENI ISTEK: {len(request.messages)} mesaj geldi.", flush=True)
    
    if not request.messages:
        print(">>> HATA: Mesaj listesi bos!", flush=True)
        return {"analysis": "Analiz edilecek mesaj bulunamadı."}

    # İlk 10-15 mesajı alalım (bağlam sınırını aşmamak için)
    context = "\n- ".join(request.messages[:15])
    
    try:
        print(">>> Groq API'ye baglaniliyor...", flush=True)
        
        completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile", # Şu anki en güçlü ve önerilen model
    # Alternatif olarak daha hızlı bir model istersen: "llama-3.1-8b-instant"
    messages=[
    {
        "role": "system", 
        "content": """Sen 20 yıllık deneyimli bir CTO'sun. 
        Sana gelen kriz mesajlarını analiz ederken:
        1. Cevapları türkçe ver.
        2. Gereksiz giriş cümleleri kurma (Örn: 'Analizime göre...' deme).
        3. Teknik terimleri doğru kullan (Réféns değil, Referans).
        4. Çözüm önerileri somut ve uygulanabilir olsun
        5. Cevapların kısa, keskin ve aksiyon odaklı olsun."""
    },
    {
        "role": "user", 
        "content": f"""
Bir proje yöneticisi olarak aşağıdaki stresli geliştirici mesajlarını analiz et. 

MESAJLAR:
{context}

ANALİZ KURALLARI:
- Yazım hatalarını düzelt (reféns -> referans).
- Duygusal durumu (stres düzeyi) değerlendir.
- Teknik sorunu tam olarak tanımla.
-teknik çözüm önerileri sun.

RAPOR FORMATI (BU FORMATI KULLAN):
# 📊 Haftalık Teknik Risk Analizi /n

### 🔍 Tespit Edilen Problem /n
(Buraya sorunu yaz)
/n
### ⚠️ Ekip Morali ve Burnout Riski /n
(Buraya mesajların tonuna göre ekibin durumunu yaz)
/n
### 💡 Yönetici Aksiyon Planı /n
1. ... /n
2. ... /n
"""
    }
]
)
        
        result = completion.choices[0].message.content
        print(">>> ANALIZ BASARILI!", flush=True)
        return {"analysis": result}

    except Exception as e:
        # Hatayı hem terminale bas hem de React'e gönder
        error_msg = str(e)
        print(f">>> KRITIK HATA: {error_msg}", flush=True)
        # Detaylı hatayı React'e dönüyoruz ki sorunu göresin
        return {"analysis": f"Backend Hatası: {error_msg}"}

@app.get("/get-dashboard-data")
async def get_dashboard_data():
    try:
        # 1. Veriyi yükle (Dosya yolunu kendine göre güncelle)
        df = pd.read_csv("dashboard_ready_data.csv")
        print(f">>> Veriler yuklendi: {len(df)} satir", flush=True)
        #Tarih ve Skorsal İşlemler
        df['author_time'] = pd.to_datetime(df['author_time'], errors='coerce')
        df = df.dropna(subset=['author_time'])
        print(f">>> Tarih sütunu datetime formatina cevrildi: {df['author_time'].dtype}", flush=True)
        
        # 1. Önce sadece kritik mesajları içeren geçici bir sütun oluşturalım
        # Skoru 0.7'den büyük olanların metnini al, diğerlerini boş bırak (None)
        df['critical_content'] = None
        df.loc[df['burnout_score'] > 0.7, 'critical_content'] = df['temiz_metin']

        # 2. Gruplama ve Aggregation (Çok daha hızlı çalışır)
        zaman_serisi = df.groupby(pd.Grouper(key='author_time', freq='W')).agg({
            'burnout_score': 'mean',
            'temiz_metin': 'count',  # Satır sayısını (commitCount) buradan alalım
            'critical_content': lambda x: [str(t) for t in x.dropna().head(5).tolist()] # Sadece dolu olanları al
        }).reset_index()
        
        # 4. Formatlama
        zaman_serisi.columns = ['author_time', 'burnoutRisk', 'commitCount', 'criticalMessages']
        zaman_serisi['author_time'] = zaman_serisi['author_time'].dt.strftime('%Y-%m-%d')
        zaman_serisi['burnoutRisk'] = (zaman_serisi['burnoutRisk'] * 100).round(1)
        zaman_serisi = zaman_serisi.fillna(0)
        return {
            "zaman_serisi": zaman_serisi.to_dict(orient='records'),
            "summary": {
                "total_processed": len(df),
                "avg_risk": round(zaman_serisi['burnoutRisk'].mean(), 1)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))