"""
🎙️ Ses Transkripsiyon Uygulaması - ADIM 3
Basit ses transkripsiyon eklendi
"""

import torch
import whisper
from pathlib import Path


def check_device():
    """GPU/CPU kontrolü ve bilgilendirme"""
    print("\n" + "="*70)
    print("🔧 CİHAZ KONTROLÜ")
    print("="*70)

    if torch.cuda.is_available():
        device = "cuda"
        gpu_name = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)

        print(f"✅ GPU Tespit Edildi!")
        print(f"   İsim: {gpu_name}")
        print(f"   VRAM: {vram:.1f} GB")
        print(f"   CUDA: {torch.version.cuda}")
    else:
        device = "cpu"
        print("⚠️  GPU bulunamadı")
        print("   CPU modunda çalışacak (yavaş olabilir)")

    print("="*70)
    return device


def load_whisper_model(model_size="base", device="cuda", model_dir=None):
    """
    Whisper modelini yükle

    Args:
        model_size: tiny, base, small, medium, large
        device: cuda veya cpu
        model_dir: Özel model dizini (opsiyonel)

    Returns:
        Yüklenen model
    """
    print("\n" + "="*70)
    print("📦 WHISPER MODEL YÜKLEME")
    print("="*70)

    # Model boyutları ve VRAM gereksinimleri
    model_info = {
        "tiny": "~1 GB VRAM - En hızlı, temel hassasiyet",
        "base": "~1 GB VRAM - Hızlı, iyi hassasiyet (önerilen)",
        "small": "~2 GB VRAM - Orta hız, iyi hassasiyet",
        "medium": "~5 GB VRAM - Yavaş, yüksek hassasiyet",
        "large": "~10 GB VRAM - En yavaş, en hassas"
    }

    print(f"\n📥 Model: {model_size}")
    print(f"ℹ️  {model_info.get(model_size, 'Bilinmeyen model')}")
    print(f"🔧 Cihaz: {device.upper()}")

    # Özel model dizini varsa kontrol et
    if model_dir:
        model_path = Path(model_dir)
        if model_path.exists():
            print(f"📁 Model dizini: {model_dir}")
            # Whisper'a özel download root belirt
            import os
            os.environ["WHISPER_CACHE"] = str(model_path)
        else:
            print(f"⚠️  Model dizini bulunamadı: {model_dir}")
            print("   Varsayılan dizin kullanılacak")

    print("\n⏳ Model yükleniyor...")

    try:
        model = whisper.load_model(model_size, device=device, download_root=model_dir)
        print(f"✅ Whisper '{model_size}' modeli başarıyla yüklendi!")
        return model
    except Exception as e:
        print(f"❌ Model yüklenirken hata: {e}")
        return None


def transcribe_audio(model, audio_path, language="tr"):
    """
    Ses dosyasını transkript et

    Args:
        model: Yüklenmiş Whisper modeli
        audio_path: Ses dosyası yolu
        language: Dil kodu (tr, en, de, fr, vs.)

    Returns:
        Transkripsiyon sonucu (dict)
    """
    print("\n" + "="*70)
    print("🎤 SES TRANSKRİPSİYON")
    print("="*70)

    # Dosya kontrolü
    audio_path = Path(audio_path)

    print(f"\n🔍 Dosya yolu kontrolü:")
    print(f"   Tam yol: {audio_path.absolute()}")
    print(f"   Var mı: {audio_path.exists()}")

    if not audio_path.exists():
        print(f"❌ Dosya bulunamadı: {audio_path}")
        return None

    # Dosya bilgisi
    file_size = audio_path.stat().st_size / (1024**2)  # MB
    print(f"\n📁 Dosya: {audio_path.name}")
    print(f"📊 Boyut: {file_size:.1f} MB")
    print(f"🌍 Dil: {language.upper()}")
    print(f"\n⏳ Transkripsiyon başlıyor...")
    print("   (Bu işlem birkaç dakika sürebilir)")

    try:
        # Transkripsiyon
        result = model.transcribe(
            str(audio_path),
            language=language,
            verbose=False,  # İlerleme mesajlarını gösterme
            fp16=torch.cuda.is_available()  # GPU varsa FP16 kullan
        )

        print(f"✅ Transkripsiyon tamamlandı!")
        print(f"📝 Segment sayısı: {len(result['segments'])}")
        print(f"⏱️  Toplam süre: {result['segments'][-1]['end']:.1f} saniye")

        return result

    except Exception as e:
        print(f"❌ Transkripsiyon hatası: {e}")
        import traceback
        print("\n📋 Detaylı hata:")
        traceback.print_exc()
        return None


def save_text_output(result, output_path):
    """
    Transkripsiyon sonucunu basit metin olarak kaydet

    Args:
        result: Whisper transkripsiyon sonucu
        output_path: Çıktı dosyası yolu
    """
    print("\n" + "="*70)
    print("💾 SONUÇ KAYDETME")
    print("="*70)

    output_path = Path(output_path)

    # Tam metni al
    full_text = result['text'].strip()

    # TXT dosyası olarak kaydet
    txt_path = output_path.with_suffix('.txt')
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(full_text)

    print(f"\n✅ Metin kaydedildi: {txt_path}")
    print(f"📝 Karakter sayısı: {len(full_text)}")

    # İlk 200 karakteri göster
    print(f"\n📄 Önizleme:")
    print("-" * 70)
    preview = full_text[:200] + "..." if len(full_text) > 200 else full_text
    print(preview)
    print("-" * 70)

    return txt_path


def main():
    """Ana fonksiyon"""
    print("\n🎙️  SES TRANSKRİPSİYON UYGULAMASI")
    print("="*70)

    # Cihaz kontrolü
    device = check_device()

    # Özel model dizini
    custom_model_dir = r"D:\LLM-Models\Whisper"

    # Whisper model yükleme
    model = load_whisper_model(
        model_size="base",
        device=device,
        model_dir=custom_model_dir
    )

    if not model:
        print("\n❌ Model yüklenemedi, program sonlanıyor...")
        return

    # Test için ses dosyası yolu
    test_audio = r"D:\Podcasts\The Pragmatic Engineer - Netflix's Engineering Culture.mp3"

    # Dosya var mı kontrol et
    if not Path(test_audio).exists():
        print(f"\n⚠️  Test dosyası bulunamadı: {test_audio}")
        print("   Lütfen dosya yolunu kontrol edin")
        return

    # Transkripsiyon yap
    result = transcribe_audio(
        model=model,
        audio_path=test_audio,
        language="en"  # Netflix podcast İngilizce
    )

    if not result:
        print("\n❌ Transkripsiyon başarısız!")
        return

    # Sonucu kaydet - MP3 ile aynı dizinde, aynı isimle
    output_path = Path(test_audio).with_suffix('')  # .mp3'ü kaldır
    saved_path = save_text_output(result, output_path)

    print("\n" + "="*70)
    print("🎉 ADIM 3 TAMAMLANDI!")
    print("="*70)
    print(f"✅ Ses dosyası transkript edildi")
    print(f"📄 Çıktı: {saved_path}")
    print("="*70)


if __name__ == "__main__":
    main()