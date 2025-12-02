"""
🎙️ Ses Transkripsiyon Uygulaması - ADIM 1
Temel yapı ve cihaz kontrolü
"""

import torch
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


def main():
    """Ana fonksiyon"""
    print("\n🎙️  SES TRANSKRİPSİYON UYGULAMASI")
    print("="*70)

    # Cihaz kontrolü
    device = check_device()
    print(f"\n✅ Seçilen cihaz: {device.upper()}")

    print("\n✅ ADIM 1 TAMAMLANDI!")
    print("   Cihaz kontrolü başarılı")


if __name__ == "__main__":
    main()