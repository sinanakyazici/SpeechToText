"""
🔍 GPU ve Sistem Kontrolü
Bu script PyTorch kurulumunu ve GPU desteğini kontrol eder
"""


def check_pytorch_gpu():
    """PyTorch ve GPU kontrolü"""
    print("=" * 70)
    print("🔍 PyTorch ve GPU Kontrolü")
    print("=" * 70)
    print()

    try:
        import torch
        print(f"✅ PyTorch Versiyonu: {torch.__version__}")
        print()

        # CUDA kontrolü
        cuda_available = torch.cuda.is_available()
        print(f"🎮 CUDA Kullanılabilir: {'✅ EVET' if cuda_available else '❌ HAYIR'}")

        if cuda_available:
            print(f"📌 CUDA Versiyonu: {torch.version.cuda}")
            print(f"📊 GPU Sayısı: {torch.cuda.device_count()}")
            print()

            # Her GPU için detay
            for i in range(torch.cuda.device_count()):
                print(f"🎮 GPU {i}:")
                print(f"   İsim: {torch.cuda.get_device_name(i)}")

                # VRAM bilgisi
                props = torch.cuda.get_device_properties(i)
                total_memory_gb = props.total_memory / (1024 ** 3)
                print(f"   VRAM: {total_memory_gb:.2f} GB")

                # Bellek kullanımı
                allocated = torch.cuda.memory_allocated(i) / (1024 ** 3)
                reserved = torch.cuda.memory_reserved(i) / (1024 ** 3)
                print(f"   Kullanılan: {allocated:.2f} GB")
                print(f"   Ayrılmış: {reserved:.2f} GB")
                print()

            # Test hesaplama
            print("🧪 GPU Testi yapılıyor...")
            try:
                x = torch.randn(1000, 1000).cuda()
                y = torch.randn(1000, 1000).cuda()
                z = torch.matmul(x, y)
                print("✅ GPU hesaplama testi başarılı!")
                print()
            except Exception as e:
                print(f"❌ GPU testi başarısız: {e}")
                print()
        else:
            print("⚠️  CPU modunda çalışacak (yavaş olabilir)")
            print()

        print("=" * 70)
        if cuda_available:
            print("🎉 Sistem hazır! GPU ile transkripsiyon yapabilirsiniz.")
        else:
            print("⚠️  GPU tespit edilemedi. CPU ile çalışacak.")
        print("=" * 70)

        return cuda_available

    except ImportError:
        print("❌ PyTorch yüklü değil!")
        print("📦 Kurulum için: pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121")
        return False
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False


if __name__ == "__main__":
    check_pytorch_gpu()