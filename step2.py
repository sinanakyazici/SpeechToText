"""
🎙️ Ses Transkripsiyon Uygulaması - ADIM 2
Whisper model yükleme eklendi
"""

import torch
import whisper
from pathlib import Path


def check_device():
    """GPU/CPU kontrolü ve bilgilendirme"""
    print("\n" + "=" * 70)
    print("🔧 CİHAZ KONTROLÜ")
    print("=" * 70)

    if torch.cuda.is_available():
        device = "cuda"
        gpu_name = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)

        print(f"✅ GPU Tespit Edildi!")
        print(f"   İsim: {gpu_name}")
        print(f"   VRAM: {vram:.1f} GB")
        print(f"   CUDA: {torch.version.cuda}")
    else:
        device = "cpu"
        print("⚠️  GPU bulunamadı")
        print("   CPU modunda çalışacak (yavaş olabilir)")

    print("=" * 70)
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
    print("\n" + "=" * 70)
    print("📦 WHISPER MODEL YÜKLEME")
    print("=" * 70)

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


def main():
    """Ana fonksiyon"""
    print("\n🎙️  SES TRANSKRİPSİYON UYGULAMASI")
    print("=" * 70)

    # Cihaz kontrolü
    device = check_device()

    # Özel model dizini
    custom_model_dir = r"D:\LLM-Models\Whisper"

    # Whisper model yükleme
    # 'base' modeli kullanıyoruz (sizde mevcut)
    model = load_whisper_model(
        model_size="base",
        device=device,
        model_dir=custom_model_dir
    )

    if model:
        print("\n✅ ADIM 2 TAMAMLANDI!")
        print("   Whisper modeli hazır!")
        print(f"   Model türü: {type(model).__name__}")
    else:
        print("\n❌ ADIM 2 BAŞARISIZ!")
        print("   Model yüklenemedi")


if __name__ == "__main__":
    main()