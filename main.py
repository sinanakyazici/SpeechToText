"""
🎙️ GPU Destekli Konuşmacı Ayrımlı Ses Transkripsiyon Uygulaması
Versiyon: 1.0
Python: 3.11.x
GPU: CUDA 12.1

Özellikler:
- Whisper ile ses-metin dönüşümü (tiny/base/small/medium/large)
- Pyannote ile otomatik konuşmacı ayrımı (2+ konuşmacı)
- GPU hızlandırma (CUDA)
- Akıllı cache sistemi
- MP3/WAV desteği
- Dinamik konuşmacı sayısı (2, 3, 4+ desteklenir)
- Akıllı konuşmacı etiketleme (en çok konuşan = SPEAKER_00)
"""

import os
import json
import hashlib
import warnings
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
import torch
import whisper
from tqdm import tqdm
from pyannote.audio import Pipeline

# .env dosyasını yükle
load_dotenv()

# ============================================
# YAPILANDIRMA
# ============================================

class Config:
    """Uygulama ayarları"""

    # Model dizinleri
    WHISPER_MODEL_DIR = r"D:\LLM-Models\Whisper"

    # HuggingFace token (.env dosyasından okunur)
    HF_TOKEN = os.getenv("HF_TOKEN")

    # Model seçenekleri
    WHISPER_MODEL = "small"  # tiny, base, small, medium, large
    LANGUAGE = "en"  # tr, en, de, fr, vs. (None = otomatik tespit)

    # Cache ayarları
    USE_CACHE = True

    # Ses dosyası
    AUDIO_FILE = r"D:\Podcasts\The Pragmatic Engineer - Netflix's Engineering Culture.mp3"


# ============================================
# YARDIMCI FONKSİYONLAR
# ============================================

def get_file_hash(file_path):
    """Dosya hash'i hesapla (değişiklik kontrolü için)"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_cache_path(audio_path, model_size):
    """Cache dosya yolunu oluştur"""
    audio_path = Path(audio_path)
    cache_dir = audio_path.parent / "output" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    cache_filename = f"{audio_path.stem}_{model_size}.json"
    return cache_dir / cache_filename


def save_to_cache(audio_path, model_size, transcription_result):
    """Whisper sonucunu cache'e kaydet"""
    cache_path = get_cache_path(audio_path, model_size)

    cache_data = {
        "audio_file": str(audio_path),
        "audio_hash": get_file_hash(audio_path),
        "model_size": model_size,
        "timestamp": datetime.now().isoformat(),
        "segments": transcription_result["segments"],
        "text": transcription_result["text"],
        "language": transcription_result["language"]
    }

    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)

    print(f"💾 Cache kaydedildi: {cache_path.name}")
    return cache_path


def load_from_cache(audio_path, model_size):
    """Cache'den Whisper sonucunu yükle"""
    cache_path = get_cache_path(audio_path, model_size)

    if not cache_path.exists():
        return None

    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)

        # Dosya değişmiş mi kontrol et
        current_hash = get_file_hash(audio_path)
        if cache_data["audio_hash"] != current_hash:
            print("⚠️  Ses dosyası değişmiş, cache geçersiz")
            return None

        # Model aynı mı kontrol et
        if cache_data["model_size"] != model_size:
            print(f"⚠️  Farklı model (cache: {cache_data['model_size']}, istenilen: {model_size})")
            return None

        print(f"✅ Cache bulundu: {cache_path.name}")
        print(f"   Tarih: {cache_data['timestamp']}")

        result = {
            "segments": cache_data["segments"],
            "text": cache_data["text"],
            "language": cache_data["language"]
        }

        return result

    except Exception as e:
        print(f"⚠️  Cache okuma hatası: {e}")
        return None


# ============================================
# ANA FONKSİYONLAR
# ============================================

def check_device():
    """GPU/CPU kontrolü"""
    print("\n" + "="*70)
    print("🔧 CİHAZ KONTROLÜ")
    print("="*70)

    if torch.cuda.is_available():
        device = "cuda"
        gpu_name = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)

        print(f"✅ GPU: {gpu_name}")
        print(f"   VRAM: {vram:.1f} GB")
        print(f"   CUDA: {torch.version.cuda}")
    else:
        device = "cpu"
        print("⚠️  CPU modunda (yavaş)")

    print("="*70)
    return device


def load_whisper_model(model_size="base", device="cuda", model_dir=None):
    """Whisper modelini yükle"""
    print("\n" + "="*70)
    print("📦 WHISPER MODEL")
    print("="*70)

    print(f"📥 Model: {model_size}")
    print(f"🔧 Cihaz: {device.upper()}")

    if model_dir and Path(model_dir).exists():
        print(f"📁 Model dizini: {model_dir}")
        os.environ["WHISPER_CACHE"] = str(model_dir)

    print("⏳ Yükleniyor...")

    try:
        model = whisper.load_model(model_size, device=device, download_root=model_dir)
        print(f"✅ Yüklendi!")
        return model
    except Exception as e:
        print(f"❌ Hata: {e}")
        return None


def load_diarization_pipeline(device="cuda", hf_token=None):
    """Pyannote konuşmacı ayrım modelini yükle"""
    print("\n" + "="*70)
    print("🗣️  KONUŞMACI AYRIM")
    print("="*70)

    print(f"📥 Pyannote Diarization")
    print(f"🔧 Cihaz: {device.upper()}")
    print("⏳ Yükleniyor...")

    # HuggingFace token'ı environment variable olarak ayarla
    if hf_token:
        os.environ["HF_TOKEN"] = hf_token

    try:
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1"
        )

        if device == "cuda":
            pipeline.to(torch.device("cuda"))

        print(f"✅ Yüklendi!")
        return pipeline

    except Exception as e:
        print(f"❌ Hata: {e}")
        print("\nℹ️  HuggingFace Token Gerekebilir:")
        print("   1. https://huggingface.co/settings/tokens")
        print("   2. https://huggingface.co/pyannote/speaker-diarization-3.1")
        return None


def transcribe_audio(model, audio_path, model_size, language="en", use_cache=True):
    """Ses dosyasını transkript et (cache ile)"""
    print("\n" + "="*70)
    print("🎤 TRANSKRİPSİYON")
    print("="*70)

    audio_path = Path(audio_path)

    if not audio_path.exists():
        print(f"❌ Dosya yok: {audio_path}")
        return None

    file_size = audio_path.stat().st_size / (1024**2)
    print(f"\n📁 {audio_path.name}")
    print(f"📊 {file_size:.1f} MB")
    print(f"🌍 Dil: {language.upper()}")

    # Cache kontrol
    if use_cache:
        print("\n🔍 Cache kontrol ediliyor...")
        cached = load_from_cache(audio_path, model_size)
        if cached:
            print("⚡ Cache'den yüklendi!")
            return cached
        else:
            print("❌ Cache yok, transkripsiyon yapılacak...")

    # Transkripsiyon
    print(f"\n⏳ Transkripsiyon başlıyor...")

    try:
        result = model.transcribe(
            str(audio_path),
            language=language,
            verbose=True,
            fp16=torch.cuda.is_available()
        )

        print(f"\n✅ Tamamlandı!")
        print(f"📝 Segment: {len(result['segments'])}")

        # Cache'e kaydet
        if use_cache:
            save_to_cache(audio_path, model_size, result)

        return result

    except Exception as e:
        print(f"❌ Hata: {e}")
        return None


def diarize_audio(pipeline, audio_path):
    """Konuşmacı ayrımı yap"""
    print("\n" + "="*70)
    print("🗣️  KONUŞMACI TESPİTİ")
    print("="*70)

    print(f"\n⏳ İşleniyor...")

    try:
        diarization = pipeline(str(audio_path))

        speakers = set()
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            speakers.add(speaker)

        print(f"✅ Tamamlandı!")
        print(f"👥 {len(speakers)} konuşmacı")

        return diarization

    except Exception as e:
        print(f"❌ Hata: {e}")
        return None


def merge_transcription_diarization(transcription, diarization):
    """Transkripsiyon + Konuşmacı bilgilerini birleştir"""
    print("\n" + "="*70)
    print("🔄 BİRLEŞTİRME")
    print("="*70)

    if not diarization:
        return [{
            "speaker": "SPEAKER_00",
            "text": transcription["text"].strip(),
            "start": 0,
            "end": 0
        }]

    segments = transcription["segments"]
    print(f"\n⏳ {len(segments)} segment işleniyor...")

    # Her segment için konuşmacı bul (basit overlap yöntemi)
    segments_with_speakers = []

    for segment in tqdm(segments, desc="📝"):
        start = segment["start"]
        end = segment["end"]
        text = segment["text"].strip()

        # En çok örtüşen konuşmacıyı bul
        best_speaker = None
        max_overlap = 0

        for turn, _, speaker in diarization.itertracks(yield_label=True):
            overlap_start = max(start, turn.start)
            overlap_end = min(end, turn.end)
            overlap = max(0, overlap_end - overlap_start)

            if overlap > max_overlap:
                max_overlap = overlap
                best_speaker = speaker

        if best_speaker:
            segments_with_speakers.append({
                "speaker": best_speaker,
                "text": text,
                "start": start,
                "end": end
            })

    # Ardışık aynı konuşmacıları birleştir
    merged = []
    current_speaker = None
    current_text = []
    current_start = None
    current_end = None

    for seg in segments_with_speakers:
        if seg["speaker"] != current_speaker:
            if current_speaker and current_text:
                merged.append({
                    "speaker": current_speaker,
                    "text": " ".join(current_text),
                    "start": current_start,
                    "end": current_end
                })
            current_speaker = seg["speaker"]
            current_text = [seg["text"]]
            current_start = seg["start"]
            current_end = seg["end"]
        else:
            current_text.append(seg["text"])
            current_end = seg["end"]  # Son segment'in bitiş zamanı

    # Son bloğu ekle
    if current_speaker and current_text:
        merged.append({
            "speaker": current_speaker,
            "text": " ".join(current_text),
            "start": current_start,
            "end": current_end
        })

    print(f"✅ {len(merged)} blok")
    return merged


def identify_main_speaker(blocks):
    """
    Ana konuşmacıyı belirle (en çok konuşan)
    Konuşmacı sayısı dinamik - 2, 3, 4+ konuşmacı desteklenir
    """
    print("\n" + "="*70)
    print("🎯 KONUŞMACI TESPİTİ")
    print("="*70)

    if len(blocks) == 0:
        return blocks

    # Her konuşmacının toplam karakter sayısı
    speaker_stats = {}

    for block in blocks:
        speaker = block['speaker']
        text_len = len(block['text'])

        if speaker not in speaker_stats:
            speaker_stats[speaker] = {
                'total_chars': 0,
                'block_count': 0
            }

        speaker_stats[speaker]['total_chars'] += text_len
        speaker_stats[speaker]['block_count'] += 1

    # İstatistikleri göster
    print(f"\n📊 Konuşmacı İstatistikleri:")
    for speaker, stats in sorted(speaker_stats.items()):
        chars = stats['total_chars']
        blocks_count = stats['block_count']
        avg_per_block = chars / blocks_count if blocks_count > 0 else 0
        percentage = (chars / sum(s['total_chars'] for s in speaker_stats.values())) * 100
        print(f"   {speaker}:")
        print(f"      Toplam: {chars:,} karakter ({percentage:.1f}%)")
        print(f"      Blok sayısı: {blocks_count}")
        print(f"      Ortalama: {avg_per_block:.0f} karakter/blok")

    # En çok konuşanı bul
    main_speaker = max(speaker_stats, key=lambda x: speaker_stats[x]['total_chars'])

    print(f"\n🎤 Ana konuşmacı: {main_speaker}")
    print(f"   (En çok konuşan)")

    # Ana konuşmacı SPEAKER_00 olmalı
    if main_speaker != 'SPEAKER_00':
        print(f"\n🔄 Etiketler düzeltiliyor...")
        print(f"   {main_speaker} → SPEAKER_00 (Ana konuşmacı)")

        # Tüm konuşmacıları yeniden etiketle
        # SPEAKER_00 olmayan en çok konuşan → SPEAKER_00
        # Diğerleri sırayla SPEAKER_01, SPEAKER_02, ...

        speaker_mapping = {}
        speaker_mapping[main_speaker] = 'SPEAKER_00'

        # Diğer konuşmacıları sırala (konuşma miktarına göre)
        other_speakers = sorted(
            [s for s in speaker_stats.keys() if s != main_speaker],
            key=lambda x: speaker_stats[x]['total_chars'],
            reverse=True
        )

        for i, speaker in enumerate(other_speakers, start=1):
            new_label = f'SPEAKER_{i:02d}'
            speaker_mapping[speaker] = new_label
            print(f"   {speaker} → {new_label}")

        # Blokları güncelle
        for block in blocks:
            if block['speaker'] in speaker_mapping:
                block['speaker'] = speaker_mapping[block['speaker']]

        print(f"✅ Etiketler düzeltildi!")
    else:
        print(f"✅ Etiketler zaten doğru!")

    print("="*70)
    return blocks


def save_output(blocks, audio_path, model_name):
    """Sonuçları kaydet (model adı ve timestamp ile)"""
    print("\n" + "="*70)
    print("💾 KAYDETME")
    print("="*70)

    # Dosya adı: ses_dosyasi_MODEL.txt
    audio_path = Path(audio_path)
    output_filename = f"{audio_path.stem}_{model_name}.txt"
    output_path = audio_path.parent / output_filename

    def format_timestamp(seconds):
        """Saniyeyi 0:00 formatına çevir"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"

    with open(output_path, 'w', encoding='utf-8') as f:
        for block in blocks:
            # Timestamp ve konuşmacı
            timestamp = format_timestamp(block.get('start', 0))
            f.write(f"{timestamp} [{block['speaker']}]\n")
            f.write(f"{block['text']}\n\n")

    print(f"\n✅ Kaydedildi:")
    print(f"   {output_path}")

    # Önizleme
    preview_count = min(3, len(blocks))
    print(f"\n📄 Önizleme (ilk {preview_count} blok):")
    print("-" * 70)
    for block in blocks[:preview_count]:
        timestamp = format_timestamp(block.get('start', 0))
        print(f"{timestamp} [{block['speaker']}]")
        preview = block['text'][:150] + "..." if len(block['text']) > 150 else block['text']
        print(preview)
        print()
    print("-" * 70)

    return output_path


# ============================================
# ANA PROGRAM
# ============================================

def main():
    """Ana fonksiyon"""
    print("\n" + "🎙️" * 35)
    print("  GPU Destekli Konuşmacı Ayrımlı Transkripsiyon")
    print("🎙️" * 35)

    # Yapılandırma
    config = Config()

    # Cihaz kontrolü
    device = check_device()

    # 1. Whisper yükle
    whisper_model = load_whisper_model(
        config.WHISPER_MODEL,
        device,
        config.WHISPER_MODEL_DIR
    )
    if not whisper_model:
        print("\n❌ Whisper yüklenemedi!")
        return

    # 2. Pyannote yükle
    diarization_pipeline = load_diarization_pipeline(device, config.HF_TOKEN)
    if not diarization_pipeline:
        print("\n⚠️  Konuşmacı ayrımı OLMADAN devam ediliyor...")

    # 3. Transkripsiyon (cache ile)
    transcription = transcribe_audio(
        whisper_model,
        config.AUDIO_FILE,
        config.WHISPER_MODEL,
        language=config.LANGUAGE,
        use_cache=config.USE_CACHE
    )
    if not transcription:
        print("\n❌ Transkripsiyon başarısız!")
        return

    # 4. Konuşmacı ayrımı
    diarization = None
    if diarization_pipeline:
        diarization = diarize_audio(diarization_pipeline, config.AUDIO_FILE)

    # 5. Birleştir
    blocks = merge_transcription_diarization(transcription, diarization)

    # 6. Akıllı konuşmacı tanıma (en çok konuşan = ana konuşmacı)
    if diarization:
        blocks = identify_main_speaker(blocks)

    # 7. Kaydet (model adı ile)
    output = save_output(blocks, config.AUDIO_FILE, config.WHISPER_MODEL)

    # Özet
    print("\n" + "="*70)
    print("🎉 TAMAMLANDI!")
    print("="*70)
    print(f"📄 Çıktı: {output}")
    print(f"🎤 Model: {config.WHISPER_MODEL}")
    print(f"👥 Konuşmacı blok sayısı: {len(blocks)}")
    print("="*70)


if __name__ == "__main__":
    main()