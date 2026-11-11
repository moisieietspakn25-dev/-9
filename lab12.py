
import numpy as np
import wave
import matplotlib.pyplot as plt

# Частота дискретизації за замовчуванням
SR = 44100


# =====================================================
# Запис WAV
# =====================================================

def save_wav(filename, x, sr=SR):
    x = np.clip(x, -1.0, 1.0)
    audio = (x * 32767).astype(np.int16)

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(audio.tobytes())


# =====================================================
# Читання WAV
# =====================================================

def load_wav(filename):
    with wave.open(filename, "rb") as wf:
        sr = wf.getframerate()
        frames = wf.readframes(wf.getnframes())

    audio = np.frombuffer(frames, dtype=np.int16)
    return audio.astype(np.float64) / 32767.0, sr


# =====================================================
# Завдання 1. Генерація чистого тону
# =====================================================

def tone(freq, dur=2.0, amp=0.5, sr=SR):
    t = np.arange(int(dur * sr)) / sr
    return amp * np.sin(2 * np.pi * freq * t)


# =====================================================
# Завдання 2. Генерація свіпу
# =====================================================

def sweep(f0, f1, dur=4.0, amp=0.5, sr=SR):
    t = np.arange(int(dur * sr)) / sr

    # Правильне обчислення фази
    ph = 2 * np.pi * (
        f0 * t +
        (f1 - f0) / (2 * dur) * t**2
    )

    return amp * np.sin(ph)


# =====================================================
# Завдання 3. Квантування
# =====================================================

def quantize(x, bits):
    levels = 2 ** bits
    max_level = levels / 2 - 1

    q = np.round(x * max_level) / max_level

    return np.clip(q, -1.0, 1.0)


# =====================================================
# Завдання 4. Дизер
# =====================================================

def dither(x, bits, seed=42):
    rng = np.random.default_rng(seed)

    step = 2 / (2 ** bits)

    noise = rng.uniform(
        -step / 2,
        step / 2,
        len(x)
    )

    return quantize(x + noise, bits)


# =====================================================
# Відношення сигнал/шум
# =====================================================

def snr_db(original, processed):
    noise = original - processed

    signal_power = np.mean(original ** 2)
    noise_power = np.mean(noise ** 2)

    if noise_power == 0:
        return float("inf")

    return 10 * np.log10(signal_power / noise_power)


# =====================================================
# Пошук пікової частоти
# =====================================================

def peak_freq(x, sr=SR):
    spectrum = np.abs(np.fft.rfft(x))
    frequencies = np.fft.rfftfreq(len(x), 1 / sr)

    # Ігноруємо нульову частоту
    index = np.argmax(spectrum[1:]) + 1

    return round(frequencies[index])


# =====================================================
# Побудова спектра
# =====================================================

def plot_spectrum(signals, filename):
    plt.figure(figsize=(10, 5))

    for x, label in signals:
        spectrum = np.abs(np.fft.rfft(x))
        frequencies = np.fft.rfftfreq(len(x), 1 / SR)

        spectrum_db = 20 * np.log10(
            spectrum / (np.max(spectrum) + 1e-12) + 1e-12
        )

        plt.plot(frequencies, spectrum_db, label=label)

    plt.xlabel("Частота, Гц")
    plt.ylabel("Амплітуда, дБ")
    plt.title("Порівняння спектрів")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


# =====================================================
# Побудова спектрограми
# =====================================================

def plot_spectrogram(x, filename, sr=SR):
    plt.figure(figsize=(10, 5))

    plt.specgram(
        x,
        NFFT=512,
        Fs=sr,
        noverlap=384
    )

    plt.xlabel("Час, секунди")
    plt.ylabel("Частота, Гц")
    plt.title("Спектрограма свіпу")
    plt.colorbar(label="Інтенсивність, дБ")

    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


# =====================================================
# ДОДАТКОВІ ТЕСТИ
# =====================================================

if __name__ == "__main__":

    print("ЛАБОРАТОРНА РОБОТА №12")
    print("Генерація та обробка цифрового звуку")
    print("=" * 50)

    # Завдання 1: чисті тони

    print("\nЗАВДАННЯ 1. Чисті тони")

    for f in (220, 440, 880):
        x = tone(f, 2.0)
        save_wav(f"tone_{f}.wav", x)

        print(f"Створено tone_{f}.wav")

    # Завдання 2: свіп

    print("\nЗАВДАННЯ 2. Свіп")

    sr = 8000

    s = sweep(0, sr, 6.0, sr=sr)

    save_wav("sweep.wav", s, sr=sr)
    plot_spectrogram(s, "sweep.png", sr=sr)

    print("Створено sweep.wav")
    print("Створено sweep.png")

    # Перевірка аліасингу

    print("\nПеревірка аліасингу:")

    for f in (3000, 5000, 7000):
        x = tone(f, 1.0, sr=sr)

        save_wav(f"alias_{f}.wav", x, sr=sr)

        print(f, "→", peak_freq(x, sr))

    # Завдання 3: квантування

    print("\nЗАВДАННЯ 3. Квантування")

    t = tone(440, 2.0, amp=0.9)

    for b in (16, 8, 4):
        q = quantize(t, b)

        save_wav(f"quant_{b}bit.wav", q)

        print(
            b,
            "біт: SNR =",
            round(snr_db(t, q), 2),
            "дБ"
        )

    # Завдання 4: дизер

    print("\nЗАВДАННЯ 4. Дизер")

    q = tone(440, 3.0, amp=0.25)

    without_dither = quantize(q, 4)
    with_dither = dither(q, 4)

    save_wav("dither_off.wav", without_dither)
    save_wav("dither_on.wav", with_dither)

    plot_spectrum(
        [
            (without_dither, "без дизеру"),
            (with_dither, "з дизером")
        ],
        "dither.png"
    )

    print(
        "SNR без:",
        round(snr_db(q, without_dither), 2),
        "дБ"
    )

    print(
        "SNR з:",
        round(snr_db(q, with_dither), 2),
        "дБ"
    )

    print("\nУсі завдання виконано!")
