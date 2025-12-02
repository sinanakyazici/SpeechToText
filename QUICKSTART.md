# 🚀 Hızlı Başlangıç Kılavuzu

## ⚡ 3 Adımda Kullanım

### 1. Ayarları Düzenle

`transcribe_final.py` dosyasını açın, `Config` sınıfını düzenleyin:

```python
class Config:
    # HuggingFace token
    HF_TOKEN = "hf_XXXXXXXXXXXXXXX"  # Token'ınızı buraya
    
    # Model seçimi
    WHISPER_MODEL = "small"  # tiny, base, small, medium, large
    
    # Dil (None = otomatik)
    LANGUAGE = "en"  # tr, en, de, fr, vs.
    
    # Ses dosyası
    AUDIO_FILE = r"D:\Podcasts\your-audio.mp3"
```

### 2. Çalıştır

```bash
python transcribe_final.py
```

### 3. Sonucu Al

```
D:\Podcasts\your-audio_small.txt
```

---

## 📊 Model Seçimi

| Model | VRAM | Hız | Hassasiyet | Öneri |
|-------|------|-----|------------|-------|
| tiny | ~1GB | ⚡⚡⚡⚡⚡ | ⭐⭐ | Test |
| base | ~1GB | ⚡⚡⚡⚡ | ⭐⭐⭐ | Hızlı |
| **small** | ~2GB | ⚡⚡⚡ | ⭐⭐⭐⭐ | **ÖNERİLEN** |
| medium | ~5GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | Kaliteli |
| large | ~10GB | ⚡ | ⭐⭐⭐⭐⭐ | En iyi |

**RTX 3060 Ti (8GB) için:** `small` veya `medium`

---

## 🌍 Dil Desteği

```python
LANGUAGE = "tr"  # Türkçe
LANGUAGE = "en"  # İngilizce
LANGUAGE = "de"  # Almanca
LANGUAGE = "fr"  # Fransızca
LANGUAGE = None  # Otomatik tespit
```

---

## 💾 Cache Sistemi

**İlk çalıştırma:**
```
⏳ Transkripsiyon: ~5-6 dakika
⏳ Konuşmacı ayrımı: ~2-5 dakika
⏱️  Toplam: ~7-11 dakika
```

**Sonraki çalıştırmalar:**
```
⚡ Cache'den yükleme: <1 saniye!
⏳ Konuşmacı ayrımı: ~2-5 dakika
⏱️  Toplam: ~2-5 dakika
```

**Cache temizleme:**
```bash
# Windows
rmdir /s D:\Podcasts\output\cache

# Veya Python ile
import shutil
shutil.rmtree("D:/Podcasts/output/cache")
```

---

## 📁 Çıktı Formatı

**Dosya adı:**
```
Orijinal:  podcast.mp3
Çıktı:     podcast_small.txt
```

**İçerik:**
```text
0:00 [SPEAKER_00]
En çok konuşanın metni buraya...

0:52 [SPEAKER_01]
İkinci konuşmacının metni...

1:45 [SPEAKER_02]
Üçüncü konuşmacı (varsa)...
```

**Özellikler:**
- **Timestamp:** Konuşmanın başladığı zaman (dakika:saniye)
- **SPEAKER_00** = En çok konuşan (genelde konuk)
- **SPEAKER_01, 02, ...** = Konuşma miktarına göre sıralı
- Ara kesmeler yakalanır
- UTF-8 encoding

---

## ⚙️ İleri Seviye Ayarlar

### Model Dizini

Whisper modellerini özel dizinde tutun:

```python
WHISPER_MODEL_DIR = r"D:\LLM-Models\Whisper"
```

İlk kullanımda modeller buraya indirilir.

### Cache Devre Dışı

```python
USE_CACHE = False
```

Her seferinde yeniden transkript eder.

### Otomatik Dil Tespiti

```python
LANGUAGE = None
```

Whisper dili otomatik algılar (biraz daha yavaş).

---

## 🐛 Sorun Giderme

### GPU Tanınmıyor

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

`False` ise:
1. NVIDIA sürücülerini güncelleyin
2. PyTorch'u yeniden kurun:
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121 --upgrade
```

### Pyannote Yüklenmiyor

1. HuggingFace token'ı kontrol edin
2. Model erişimi olduğundan emin olun:
   - https://huggingface.co/pyannote/speaker-diarization-3.1

### VRAM Yetersiz

Model boyutunu küçültün:
```python
WHISPER_MODEL = "small"  # medium → small
```

### Yavaş Çalışıyor

1. GPU kullanıldığından emin olun
2. Cache açık olduğundan emin olun
3. Daha küçük model kullanın

---

## 📊 Performans İpuçları

**En Hızlı:**
```python
WHISPER_MODEL = "tiny"
USE_CACHE = True
```

**En Kaliteli:**
```python
WHISPER_MODEL = "medium"  # large 8GB'de çalışmaz
LANGUAGE = "en"  # Otomatik tespit kapalı
```

**Dengeli (Önerilen):**
```python
WHISPER_MODEL = "small"
LANGUAGE = "en"
USE_CACHE = True
```

---

## 🎯 Örnek Kullanım Senaryoları

### Podcast Transkripti
```python
AUDIO_FILE = r"D:\Podcasts\podcast-episode-123.mp3"
WHISPER_MODEL = "small"
LANGUAGE = "en"
```

### Röportaj (Türkçe)
```python
AUDIO_FILE = r"D:\Interviews\mülakat.mp3"
WHISPER_MODEL = "small"
LANGUAGE = "tr"
```

### Toplantı Kaydı
```python
AUDIO_FILE = r"D:\Meetings\2025-12-02-team-meeting.mp3"
WHISPER_MODEL = "base"  # Hızlı
LANGUAGE = "tr"
```

### Akademik Konuşma (Yüksek Kalite)
```python
AUDIO_FILE = r"D:\Lectures\quantum-physics-101.mp3"
WHISPER_MODEL = "medium"
LANGUAGE = "en"
```

---

## 📞 Destek

Sorun mu var? İşte kaynaklar:

1. **README.md** - Detaylı dokümantasyon
2. **CHANGELOG.md** - Son değişiklikler
3. **system_check.py** - Sistem testi

---

**Kolay gelsin! 🎙️**