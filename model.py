import pandas as pd
import numpy as np
import torch
from torch import nn
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report, f1_score, recall_score
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments, DataCollatorWithPadding

# 1. Veriyi Yükle ve Etiketleri Sayısallaştır
df = pd.read_csv("dengeli_commit_verisi.csv")

# Etiket sözlüğü oluştur
label_dict = {'nötr': 0, 'negatif': 1, 'pozitif': 2}
df['label'] = df['ana_kategori'].map(label_dict)

# Sadece metin ve sayısal etiketleri al
texts = df['temiz_metin'].astype(str).tolist()
labels = df['label'].tolist()

# Train (%80), Val (%10), Test (%10) Ayrımı
train_texts, temp_texts, train_labels, temp_labels = train_test_split(
    texts, labels, test_size=0.2, random_state=42, stratify=labels
)
val_texts, test_texts, val_labels, test_labels = train_test_split(
    temp_texts, temp_labels, test_size=0.5, random_state=42, stratify=temp_labels
)

# 2. Sınıf Ağırlıklarını Hesaplama (ÇOK KRİTİK: Dengesiz veriler için)
class_weights = compute_class_weight('balanced', classes=np.unique(train_labels), y=train_labels)
device = 'cuda' if torch.cuda.is_available() else 'cpu'
class_weights_tensor = torch.tensor(class_weights, dtype=torch.float).to(device)
print(f"Sınıf Ağırlıkları (Nötr, Negatif, Pozitif): {class_weights}")

# 3. Tokenizasyon (max_length 128 - Bellek dostu)
model_name = "roberta-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)

def tokenize_function(text_list):
    return tokenizer(text_list, truncation=True, max_length=128)

train_encodings = tokenize_function(train_texts)
val_encodings = tokenize_function(val_texts)
test_encodings = tokenize_function(test_texts)

# 4. PyTorch Dataset Sınıfı
class CommitDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item

    def __len__(self):
        return len(self.labels)

train_dataset = CommitDataset(train_encodings, train_labels)
val_dataset = CommitDataset(val_encodings, val_labels)
test_dataset = CommitDataset(test_encodings, test_labels)

# 5. Özel Trainer (Kayıp Fonksiyonunu Ağırlıklandırmak İçin)
class WeightedTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        # Ağırlıklı Cross Entropy
        loss_fct = nn.CrossEntropyLoss(weight=class_weights_tensor)
        loss = loss_fct(logits.view(-1, self.model.config.num_labels), labels.view(-1))
        return (loss, outputs) if return_outputs else loss

# 6. Metrik Hesaplama
def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    f1 = f1_score(labels, preds, average='macro')
    # Sadece Negatif sınıfın (1) Recall'ını takip etmek istiyorsanız:
    neg_recall = recall_score(labels, preds, labels=[1], average='macro') 
    return {'macro_f1': f1, 'negatif_sinif_recall': neg_recall}

# 7. Model ve Argümanlar (RTX 4050 Optimize)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3)

training_args = TrainingArguments(
    output_dir='./roberta_burnout_model',
    num_train_epochs=3,
    per_device_train_batch_size=16,     # max_length 128 olduğu için 16'ya çıkardık
    gradient_accumulation_steps=2,      # 16x2 = 32 efektif batch
    per_device_eval_batch_size=32,
    warmup_steps=500,
    weight_decay=0.01,
    logging_steps=100,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="macro_f1",
    fp16=True,                          # 16-bit hızlandırma ve VRAM tasarrufu
    report_to="none"
)

data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

trainer = WeightedTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
    data_collator=data_collator
)

# 8. Eğitimi Başlat
print("Model Eğitimi Başlıyor...")
trainer.train()

# 9. Test Setinde Nihai Değerlendirme
print("Test Setinde Değerlendirme Yapılıyor...")
test_results = trainer.predict(test_dataset)
preds = test_results.predictions.argmax(-1)
print(classification_report(test_labels, preds, target_names=['Nötr', 'Negatif', 'Pozitif']))

# 10. Modeli Kaydet
trainer.save_model("./best_burnout_roberta")
tokenizer.save_pretrained("./best_burnout_roberta")
print("En iyi model başarıyla kaydedildi!")