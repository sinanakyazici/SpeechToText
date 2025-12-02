# 🎙️ GPU Destekli Konuşmacı Ayrımlı Ses Transkripsiyon

Podcast'ler, röportajlar ve toplantılar için profesyonel kalitede, GPU hızlandırmalı ses transkripsiyon uygulaması.

## ✨ Özellikler

- 🎤 **Whisper AI** ile yüksek hassasiyetli ses-metin dönüşümü
- 🗣️ **Pyannote.audio** ile otomatik konuşmacı ayrımı (2+ konuşmacı)
- 🎮 **GPU hızlandırma** (CUDA) - 20x daha hızlı
- 💾 **Akıllı cache sistemi** - tekrar işleme yok
- 📁 **MP3/WAV desteği**
- 🌍 **Çoklu dil desteği** (Türkçe, İngilizce, Almanca, Fransızca, vb.)
- 🎯 **Dinamik konuşmacı sayısı** (2, 3, 4+ otomatik tespit)
- 🔄 **Akıllı etiketleme** (en çok konuşan = SPEAKER_00)

## 🚀 Hızlı Başlangıç

### Gereksinimler

- Windows 10/11 (64-bit)
- Python 3.11.x
- NVIDIA GPU (8GB+ VRAM önerilir)
- CUDA 12.1+
- FFmpeg

### Kurulum

**1. Repository'yi İndirin**
```bash
git clone <repo-url>
cd SpeechToText
```

**2. Virtual Environment Oluşturun**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**3. PyTorch GPU Kurulumu (ÖNCELİKLİ!)**
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**4. Diğer Paketler**
```bash
pip install -r requirements.txt
```

**5. FFmpeg Kurulumu**
```bash
choco install ffmpeg
```

### Yapılandırma

`transcribe_final.py` dosyasındaki `Config` sınıfını düzenleyin:

```python
class Config:
    # Whisper model dizini
    WHISPER_MODEL_DIR = r"D:\LLM-Models\Whisper"
    
    # HuggingFace token (https://huggingface.co/settings/tokens)
    HF_TOKEN = "hf_XXXXXXXXXXXXXXX"
    
    # Model boyutu: tiny, base, small, medium, large
    WHISPER_MODEL = "base"
    
    # Dil kodu: tr, en, de, fr, vs.
    LANGUAGE = "en"
    
    # Ses dosyası
    AUDIO_FILE = r"D:\Podcasts\your-podcast.mp3"
```

### HuggingFace Token

1. https://huggingface.co/settings/tokens adresinden token alın
2. https://huggingface.co/pyannote/speaker-diarization-3.1 modeline erişim isteyin
3. Token'ı `Config.HF_TOKEN` içine yapıştırın

### Kullanım

```bash
python transcribe_final.py
```

İlk çalıştırma: ~3-5 dakika (60 dakikalık ses için)  
Sonraki çalıştırmalar: <1 saniye (cache sayesinde)

## 📊 Performans

### Test Ortamı
- GPU: NVIDIA GeForce RTX 3060 Ti (8GB)
- CPU: Modern 8-core
- Ses: 60 dakika podcast (MP3, 56MB)

### Sonuçlar
| İşlem | GPU | CPU |
|-------|-----|-----|
| Transkripsiyon | 3:07 dakika | ~60 dakika |
| Konuşmacı Ayrımı | 2-5 dakika | ~30 dakika |
| **Toplam** | **~5-8 dakika** | **~90 dakika** |

**Hızlanma:** ~20x daha hızlı! ⚡

## 📁 Çıktı Formatı

**Dosya Adı:**
```
Giriş:  podcast.mp3
Çıktı:  podcast_small.txt  ← Model adı eklenir
```

**İçerik:**
```text
0:00 [SPEAKER_00]
En çok konuşanın metni (genelde konuk/ana konuşmacı)...

0:52 [SPEAKER_01]
İkinci konuşmacının metni (genelde röportajcı)...

1:45 [SPEAKER_00]
Tekrar ana konuşmacı...

2:10 [SPEAKER_01]
İkinci konuşmacı...
```

**Özellikler:**
- **Timestamp:** Her bloğun başlangıç zamanı (0:00 formatında)
- **SPEAKER_00:** En çok konuşan (otomatik belirlenir)
- **SPEAKER_01, 02, ...:** Konuşma miktarına göre sıralı
- Ara kesmeler yakalanır
- UTF-8 encoding

## 📂 Dosya Yapısı

```
D:\Developments\python\SpeechToText\
├── .venv\                      # Virtual environment
├── transcribe_final.py         # Ana uygulama
├── system_check.py             # Sistem test scripti
├── requirements.txt            # Paket bağımlılıkları
└── README.md                   # Bu dosya

D:\LLM-Models\Whisper\          # Whisper modelleri (opsiyonel)
├── ggml-tiny.bin
├── ggml-base.bin
├── ggml-small.bin
└── ggml-large-v3.bin

D:\Podcasts\                    # Çalışma dizini
├── podcast.mp3                 # Giriş
├── podcast.txt                 # Çıktı
└── output\
    └── cache\
        └── podcast_base.json   # Cache
```

## 🔧 Sorun Giderme

### GPU Tanınmıyor

```bash
# Kontrol et
python -c "import torch; print(torch.cuda.is_available())"
```

Eğer `False` ise:
1. CUDA sürücülerini güncelleyin
2. PyTorch'u tekrar kurun (GPU versiyonu)

### FFmpeg Bulunamıyor

```bash
# Test et
ffmpeg -version
```

Eğer çalışmıyorsa:
1. PyCharm'ı kapatın
2. Bilgisayarı yeniden başlatın
3. PyCharm'ı tekrar açın

### Pyannote Modeli Yüklenmiyor

1. HuggingFace token'ınızı kontrol edin
2. Model erişim izni aldığınızdan emin olun
3. İnternet bağlantınızı kontrol edin

### Cache Sorunları

Cache'i temizlemek için:
```bash
rm -rf D:\Podcasts\output\cache\
```

## 🔑 Model Seçimi

| Model | VRAM | Hız | Hassasiyet | Öneri |
|-------|------|-----|------------|-------|
| tiny | ~1GB | ⚡⚡⚡⚡⚡ | ⭐⭐ | Hızlı test |
| base | ~1GB | ⚡⚡⚡⚡ | ⭐⭐⭐ | Hızlı |
| **small** | ~2GB | ⚡⚡⚡ | ⭐⭐⭐⭐ | **ÖNERİLEN** ✅ |
| medium | ~5GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | Profesyonel |
| large | ~10GB | ⚡ | ⭐⭐⭐⭐⭐ | En iyi (8GB'de çalışmaz) |

**Varsayılan:** `small` - Hız/kalite dengesi mükemmel!

## 📝 Versiyon Notları

### v1.0 (2025-12-02)
- ✅ İlk stabil versiyon
- ✅ GPU hızlandırma
- ✅ Cache sistemi
- ✅ Konuşmacı ayrımı
- ✅ MP3/WAV desteği

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing`)
5. Pull Request açın

## 📄 Lisans

MIT License - Detaylar için `LICENSE` dosyasına bakın

## 🙏 Teşekkürler

- [OpenAI Whisper](https://github.com/openai/whisper)
- [Pyannote.audio](https://github.com/pyannote/pyannote-audio)
- [HuggingFace](https://huggingface.co/)

## 📧 İletişim

Sorularınız için issue açabilirsiniz!

---

**⚡ GPU ile Hızlı Transkripsiyon! 🎙️**