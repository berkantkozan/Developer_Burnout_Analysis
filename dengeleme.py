import pandas as pd

# Veriyi oku
df = pd.read_csv("commit_verisi.csv")

# Sınıfları ayır
df_neutral = df[df['ana_kategori'] == 'nötr']
df_negative = df[df['ana_kategori'] == 'negatif']
df_positive = df[df['ana_kategori'] == 'pozitif']

# Nötr sınıfı dramatik şekilde azalt (Undersampling)
# 387 negatif veri olduğu için, Nötr veriyi 2500 civarına çekmek ideal bir denge sağlar
df_neutral_sampled = df_neutral.sample(n=2500, random_state=42)

# Verileri tekrar birleştir ve karıştır
df_balanced = pd.concat([df_neutral_sampled, df_negative, df_positive])
df_balanced = df_balanced.sample(frac=1, random_state=42).reset_index(drop=True)

# Yeni dağılımı kontrol et
print("Yeni Veri Seti Dağılımı:")
print(df_balanced['ana_kategori'].value_counts())

# Modeli eğiteceğimiz nihai dosyayı kaydet
df_balanced.to_csv("dengeli_commit_verisi.csv", index=False)
print("\n'dengeli_commit_verisi.csv' başarıyla oluşturuldu!")