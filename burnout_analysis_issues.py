import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def burnout_analizi_yap(csv_yolu):
    print(f"--- [Raporlama] {csv_yolu} İşleniyor ---")
    
    # 1. Veriyi Yükle
    df = pd.read_csv(csv_yolu)
    
    # 2. GoEmotions Duygularını Burnout Kategorilerine Grupla
    # GoEmotions çok detaylıdır (28 duygu). Bunları burnout analizi için sadeleştiriyoruz.
    burnout_mapping = {
        # Negatif (Burnout Belirtileri)
        'anger': 'Negatif (Risk)', 'annoyance': 'Negatif (Risk)', 'disappointment': 'Negatif (Risk)',
        'disgust': 'Negatif (Risk)', 'fear': 'Negatif (Risk)', 'grief': 'Negatif (Risk)',
        'nervousness': 'Negatif (Risk)', 'remorse': 'Negatif (Risk)', 'sadness': 'Negatif (Risk)',
        
        # Pozitif (Motivasyon Belirtileri)
        'admiration': 'Pozitif', 'amusement': 'Pozitif', 'approval': 'Pozitif',
        'caring': 'Pozitif', 'desire': 'Pozitif', 'excitement': 'Pozitif',
        'gratitude': 'Pozitif', 'joy': 'Pozitif', 'love': 'Pozitif',
        'optimism': 'Pozitif', 'pride': 'Pozitif', 'relief': 'Pozitif',
        
        # Nötr/Diğer
        'neutral': 'Nötr', 'realization': 'Nötr', 'surprise': 'Nötr',
        'curiosity': 'Nötr', 'confusion': 'Nötr'
    }
    
    df['burnout_kategori'] = df['baskin_duygu'].map(burnout_mapping).fillna('Diğer')

    # 3. İstatistiksel Özet
    print("\n--- Burnout Kategorilerine Göre Dağılım ---")
    ozet = df['burnout_kategori'].value_counts(normalize=True) * 100
    print(ozet)

    # 4. En Çok Görülen 5 Spesifik Duygu
    print("\n--- En Çok Tetiklenen 5 Duygu ---")
    print(df['baskin_duygu'].value_counts().head(5))

    # 5. Görselleştirme (Grafik)
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    
    # Duygu Dağılım Grafiği
    ax = sns.countplot(data=df, x='burnout_kategori', palette={'Negatif (Risk)': 'red', 'Pozitif': 'green', 'Nötr': 'gray', 'Diğer': 'blue'})
    plt.title('Developer Burnout Risk Analizi (Duygu Bazlı)')
    plt.xlabel('Kategori')
    plt.ylabel('Mesaj Sayısı')
    
    # Grafik üzerine yüzdeleri ekle
    total = len(df)
    for p in ax.patches:
        percentage = f'{100 * p.get_height() / total:.1f}%'
        ax.annotate(percentage, (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='center', xytext=(0, 10), textcoords='offset points')

    plt.tight_layout()
    plt.show()

    # 6. Riskli Mesajları Listele (Örnek)
    print("\n--- Burnout Riski Yüksek (Negatif) Örnek Mesajlar ---")
    riskli_mesajlar = df[df['burnout_kategori'] == 'Negatif (Risk)'].sort_values(by='duygu_skoru', ascending=False)
    print(riskli_mesajlar[['issue_key', 'baskin_duygu', 'duygu_skoru']].head(5))

if __name__ == "__main__":
    csv_yolu = r'C:\Users\User\OneDrive - gazi.edu.tr\Belgeler\Developer_Burnout_Analysis\analiz_sonuclari.csv'
    burnout_analizi_yap(csv_yolu)