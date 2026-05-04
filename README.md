# Developer Burnout & Sentiment Analysis System

Bu proje, yazılım geliştiricilerin commit mesajları ve sosyal medya aktiviteleri üzerinden tükenmişlik (burnout) seviyelerini ve duygu durumlarını analiz etmeyi amaçlayan kapsamlı bir veri madenciliği ve makine öğrenmesi aracıdır.

## 🚀 Özellikler

*   **Duygu Analizi (Sentiment Analysis):** Senti4SD ve özelleştirilmiş NLP modelleri kullanılarak geliştirici metinlerinin analizi.
*   **Model Çeşitliliği:** BERT ve RoBERTa mimarileri üzerine inşa edilmiş, tükenmişlik tespiti için eğitilmiş sınıflandırıcılar.
*   **Veri Dengeleme:** Dengesiz veri setleri üzerinde SMOTE algoritması ile k-parametresi 500 olacak şekilde optimize edilmiş eğitim süreci.
*   **Interaktif Dashboard:** Analiz sonuçlarını zaman serisi bazlı görselleştiren React.js tabanlı kullanıcı arayüzü.

## 🛠️ Teknik Yığın

*   **Backend/Analysis:** Python, Transformers (Hugging Face), Scikit-learn, Pandas.
*   **Frontend:** React.js, Chart.js / Recharts.
*   **Modeller:** BERT-base-uncased, RoBERTa-base.

## 📂 Proje Yapısı
```text
├── burnout-dashboard/          # React tabanlı arayüz kodları
├── burnout_analysis_commits.py # Commit mesajları analiz scripti
├── burnout_analysis_senti4sd.py# Senti4SD entegrasyonu
├── dengeleme.py               # SMOTE ve veri dengeleme işlemleri
├── model.py                   # Model eğitim ve tahmin mantığı
├── dataset_analysis.py        # Veri seti istatistiksel analizleri
└── package.json               # Frontend bağımlılıkları
