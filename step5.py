"""
🎙️ Ses Transkripsiyon Uygulaması - ADIM 5
Cache Sistemi Eklendi (Whisper sonuçlarını kaydeder)
"""

import torch
import whisper
import json
import hashlib
from pathlib import Path
from tqdm import tqdm
from pyannote.audio import Pipeline
from datetime import datetime


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

    # Dosya adı: ses_dosyasi_MODEL.json
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
        print(f"   Model: {cache_data['model_size']}")

        # Whisper formatına dönüştür
        result = {
            "segments": cache_data["segments"],
            "text": cache_data["text"],
            "language": cache_data["language"]
        }

        return result

    except Exception as e:
        print(f"⚠️  Cache okuma hatası: {e}")
        return None


def check_device():
    """GPU/CPU kontrolü"""
    print("\n" + "=" * 70)
    print("🔧 CİHAZ KONTROLÜ")
    print("=" * 70)

    if torch.cuda.is_available():
        device = "cuda"
        gpu_name = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)

        print(f"✅ GPU: {gpu_name}")
        print(f"   VRAM: {vram:.1f} GB")
        print(f"   CUDA: {torch.version.cuda}")
    else:
        device = "cpu"
        print("⚠️  CPU modunda")

    print("=" * 70)
    return device


def load_whisper_model(model_size="base", device="cuda", model_dir=None):
    """Whisper modelini yükle"""
    print("\n" + "=" * 70)
    print("📦 WHISPER MODEL")
    print("=" * 70)

    print(f"📥 Model: {model_size}")
    print(f"🔧 Cihaz: {device.upper()}")

    if model_dir and Path(model_dir).exists():
        print(f"📁 Model dizini: {model_dir}")
        import os
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
    """Pyannote konuşmacı ayrım"""
    print("\n" + "=" * 70)
    print("🗣️  KONUŞMACI AYRIM")
    print("=" * 70)

    print(f"📥 Pyannote Diarization")
    print(f"🔧 Cihaz: {device.upper()}")
    print("⏳ Yükleniyor...")

    try:
        if hf_token:
            pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1"
            )
        else:
            pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1"
            )

        if device == "cuda":
            pipeline.to(torch.device("cuda"))

        print(f"✅ Yüklendi!")
        return pipeline

    except Exception as e:
        print(f"❌ Hata: {e}")
        return None


def transcribe_audio(model, audio_path, model_size, language="en", use_cache=True):
    """Ses dosyasını transkript et (cache ile)"""
    print("\n" + "=" * 70)
    print("🎤 TRANSKRİPSİYON")
    print("=" * 70)

    audio_path = Path(audio_path)

    if not audio_path.exists():
        print(f"❌ Dosya yok: {audio_path}")
        return None

    file_size = audio_path.stat().st_size / (1024 ** 2)
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
        print(f"⏱️  Süre: {result['segments'][-1]['end']:.1f} sn")

        # Cache'e kaydet
        if use_cache:
            save_to_cache(audio_path, model_size, result)

        return result

    except Exception as e:
        print(f"❌ Hata: {e}")
        return None


def diarize_audio(pipeline, audio_path):
    """Konuşmacı ayrımı"""
    print("\n" + "=" * 70)
    print("🗣️  KONUŞMACI TESPİTİ")
    print("=" * 70)

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
    """Birleştir"""
    print("\n" + "=" * 70)
    print("🔄 BİRLEŞTİRME")
    print("=" * 70)

    if not diarization:
        return [{
            "speaker": "SPEAKER_00",
            "text": transcription["text"].strip()
        }]

    segments = transcription["segments"]
    print(f"\n⏳ {len(segments)} segment işleniyor...")

    segments_with_speakers = []

    for segment in tqdm(segments, desc="📝"):
        start = segment["start"]
        end = segment["end"]
        text = segment["text"].strip()

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
                "text": text
            })

    # Ardışık aynı konuşmacıları birleştir
    merged = []
    current_speaker = None
    current_text = []

    for seg in segments_with_speakers:
        if seg["speaker"] != current_speaker:
            if current_speaker:
                merged.append({
                    "speaker": current_speaker,
                    "text": " ".join(current_text)
                })
            current_speaker = seg["speaker"]
            current_text = [seg["text"]]
        else:
            current_text.append(seg["text"])

    if current_speaker:
        merged.append({
            "speaker": current_speaker,
            "text": " ".join(current_text)
        })

    print(f"✅ {len(merged)} blok")
    return merged


def save_output(blocks, audio_path):
    """Kaydet"""
    print("\n" + "=" * 70)
    print("💾 KAYDETME")
    print("=" * 70)

    # MP3 ile aynı yerde
    output_path = Path(audio_path).with_suffix('.txt')

    with open(output_path, 'w', encoding='utf-8') as f:
        for block in blocks:
            f.write(f"[{block['speaker']}]\n")
            f.write(f"{block['text']}\n\n")

    print(f"\n✅ Kaydedildi:")
    print(f"   {output_path}")

    # Önizleme
    print(f"\n📄 Önizleme (ilk 3 blok):")
    print("-" * 70)
    for block in blocks[:3]:
        print(f"[{block['speaker']}]")
        preview = block['text'][:150] + "..." if len(block['text']) > 150 else block['text']
        print(preview)
        print()
    print("-" * 70)

    return output_path


def main():
    """Ana fonksiyon"""
    print("\n🎙️  TRANSKRİPSİYON - CACHE SİSTEMLİ")
    print("=" * 70)

    # HuggingFace token'ı environment variable olarak ayarla
    import os
    os.environ["HF_TOKEN"] = "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"

    # Ayarlar
    device = check_device()
    model_dir = r"D:\LLM-Models\Whisper"
    model_size = "base"  # tiny, base, small, medium, large
    hf_token = "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"
    audio_file = r"D:\Podcasts\The Pragmatic Engineer - Netflix's Engineering Culture.mp3"

    # 1. Whisper
    whisper_model = load_whisper_model(model_size, device, model_dir)
    if not whisper_model:
        return

    # 2. Pyannote
    diarization_pipeline = load_diarization_pipeline(device, hf_token)

    # 3. Transkripsiyon (cache ile!)
    transcription = transcribe_audio(
        whisper_model,
        audio_file,
        model_size,
        language="en",
        use_cache=True  # Cache kullan!
    )
    if not transcription:
        return

    # 4. Konuşmacı ayrımı
    diarization = None
    if diarization_pipeline:
        diarization = diarize_audio(diarization_pipeline, audio_file)

    # 5. Birleştir
    blocks = merge_transcription_diarization(transcription, diarization)

    # 6. Kaydet
    output = save_output(blocks, audio_file)

    print("\n" + "=" * 70)
    print("🎉 TAMAMLANDI!")
    print("=" * 70)
    print(f"📄 {output}")
    print(f"👥 {len(blocks)} blok")
    print("=" * 70)


if __name__ == "__main__":
    main()