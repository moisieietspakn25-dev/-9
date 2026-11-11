"""
Лабораторна робота №13. Спектральний аналіз
Спеціальність 122 Комп'ютерні науки, група КН-3/1

Перед запуском:
    py -m pip install numpy scipy matplotlib

Запуск:
    py lab13.py

Скрипт створює:
- source.wav
- spectrum.png, spectrogram.png
- window_comparison.txt
- spectrogram_128.png, spectrogram_4096.png
- eq_before.png, eq_after.png
- preset_bass.wav, preset_voice.wav, preset_phone.wav
- band_energy.txt
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import spectrogram

SR = 44100


def normalize_audio(x):
    """Нормалізація сигналу до діапазону приблизно [-1; 1]."""
    peak = np.max(np.abs(x))
    if peak == 0:
        return x
    return 0.95 * x / peak


def save_wav(filename, x, sr=SR):
    """Збереження сигналу у 16-бітний WAV."""
    audio = normalize_audio(np.asarray(x, dtype=float))
    wavfile.write(filename, sr, (audio * 32767).astype(np.int16))


def music(dur=3.0, sr=SR):
    """Генерація акорду з основними тонами 220, 277.18 і 329.63 Гц."""
    t = np.arange(int(dur * sr)) / sr
    x = np.zeros_like(t)
    for f0 in (220.0, 277.18, 329.63):
        for k, a in enumerate([1, 0.5, 0.3, 0.18, 0.1, 0.06], start=1):
            x += a * np.sin(2 * np.pi * f0 * k * t + k)
    x *= np.minimum(1, t * 8) * np.exp(-0.35 * t)
    return normalize_audio(x)


def task1_spectrum_and_spectrogram(x):
    """Завдання 1: спектр одного фрагмента та спектрограма сигналу."""
    n = 8192
    fragment = x[:n]
    windowed = fragment * np.hanning(n)

    sp = np.abs(np.fft.rfft(windowed))
    db = 20 * np.log10(sp / (sp.max() + 1e-15) + 1e-12)
    fr = np.fft.rfftfreq(n, 1 / SR)

    plt.figure(figsize=(10, 5))
    mask = fr < 2500
    plt.plot(fr[mask], db[mask])
    plt.title("Спектр сигналу")
    plt.xlabel("Частота, Гц")
    plt.ylabel("Амплітуда, дБ")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("spectrum.png", dpi=150)
    plt.close()

    f, t, s = spectrogram(x, SR, nperseg=2048, noverlap=1792)
    plt.figure(figsize=(10, 5))
    plt.pcolormesh(t, f, 10 * np.log10(s + 1e-12), shading="auto")
    plt.ylim(0, 5000)
    plt.title("Спектрограма сигналу")
    plt.xlabel("Час, с")
    plt.ylabel("Частота, Гц")
    plt.colorbar(label="Потужність, дБ")
    plt.tight_layout()
    plt.savefig("spectrogram.png", dpi=150)
    plt.close()


def task2_compare_windows():
    """Завдання 2: порівняння прямокутного, Ганна та Блекмана."""
    n = 1024
    windows = (
        ("прямокутне", np.ones(n)),
        ("Ганна", np.hanning(n)),
        ("Блекмана", np.blackman(n)),
    )

    results = []
    for k, label in ((100.0, "рівно на біні"), (100.5, "між бінами")):
        frequency = k * SR / n
        t = np.arange(n) / SR
        signal = np.sin(2 * np.pi * frequency * t)

        for name, window in windows:
            spectrum = np.abs(np.fft.rfft(signal * window))
            db = 20 * np.log10(spectrum / (spectrum.max() + 1e-15) + 1e-15)
            far = np.concatenate((db[:95], db[106:]))
            highest = float(far.max())
            results.append((label, name, highest))

    with open("window_comparison.txt", "w", encoding="utf-8") as file:
        file.write("Випадок\tВікно\tНайвищий сторонній пік, дБ\n")
        for label, name, value in results:
            file.write(f"{label}\t{name}\t{value:.1f}\n")

    print("\nЗавдання 2. Найвищий сторонній пік:")
    for label, name, value in results:
        print(f"{label:16s} {name:14s} {value:8.1f} дБ")

    # Додатково зберігаємо наочне порівняння для випадку між бінами.
    n = 1024
    t = np.arange(n) / SR
    signal = np.sin(2 * np.pi * (100.5 * SR / n) * t)
    plt.figure(figsize=(10, 5))
    for name, window in windows:
        spectrum = np.abs(np.fft.rfft(signal * window))
        db = 20 * np.log10(spectrum / (spectrum.max() + 1e-15) + 1e-15)
        fr = np.fft.rfftfreq(n, 1 / SR)
        plt.plot(fr, db, label=name)
    plt.xlim(3500, 5000)
    plt.ylim(-100, 5)
    plt.title("Порівняння вікон: тон між бінами")
    plt.xlabel("Частота, Гц")
    plt.ylabel("Амплітуда, дБ")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("window_comparison.png", dpi=150)
    plt.close()


def task3_time_frequency():
    """Завдання 3: демонстрація компромісу між часом і частотою."""
    dur = 1.4
    t = np.arange(int(dur * SR)) / SR
    x = np.zeros_like(t)

    segment = t < 0.6
    x[segment] = (
        0.5 * np.sin(2 * np.pi * 440 * t[segment])
        + 0.5 * np.sin(2 * np.pi * 480 * t[segment])
    )

    for click_time in (0.80, 0.92, 1.04, 1.16):
        index = int(click_time * SR)
        x[index:index + 40] += np.hanning(40)

    for n in (128, 4096):
        f, tt, s = spectrogram(
            x, SR, nperseg=n, noverlap=int(n * 0.9)
        )
        plt.figure(figsize=(10, 5))
        plt.pcolormesh(tt, f, 10 * np.log10(s + 1e-12), shading="auto")
        plt.ylim(0, 1500)
        plt.title(f"Спектрограма: вікно {n}")
        plt.xlabel("Час, с")
        plt.ylabel("Частота, Гц")
        plt.colorbar(label="Потужність, дБ")
        plt.tight_layout()
        plt.savefig(f"spectrogram_{n}.png", dpi=150)
        plt.close()


def eq(x, bands, sr=SR):
    """Еквалайзер. bands — список (від, до, підсилення в дБ)."""
    sp = np.fft.rfft(x)
    fr = np.fft.rfftfreq(len(x), 1 / sr)
    gain = np.ones(len(sp))

    for low, high, db in bands:
        gain[(fr >= low) & (fr < high)] = 10 ** (db / 20)

    return np.fft.irfft(sp * gain, len(x))


def band_energy(x, low, high, sr=SR):
    """Енергія частотної смуги у дБ."""
    sp = np.abs(np.fft.rfft(x))
    fr = np.fft.rfftfreq(len(x), 1 / sr)
    selected = sp[(fr >= low) & (fr < high)]
    return 10 * np.log10((selected ** 2).sum() + 1e-20)


def task4_equalizer(x):
    """Завдання 4: перевірка еквалайзера та створення трьох пресетів."""
    bands = [(0, 250, 12)]
    y = eq(x, bands)

    ranges = (
        (0, 250),
        (250, 1000),
        (1000, 4000),
        (4000, SR // 2 + 1),
    )

    rows = []
    for low, high in ranges:
        before = band_energy(x, low, high)
        after = band_energy(y, low, high)
        rows.append((low, high, before, after, after - before))

    with open("band_energy.txt", "w", encoding="utf-8") as file:
        file.write("Смуга, Гц\tДо, дБ\tПісля, дБ\tРізниця, дБ\n")
        for low, high, before, after, difference in rows:
            file.write(
                f"{low}-{high}\t{before:.2f}\t{after:.2f}\t{difference:.2f}\n"
            )

    print("\nЗавдання 4. Енергія частотних смуг:")
    for low, high, before, after, difference in rows:
        print(
            f"{low:4d}-{high:5d} Гц: "
            f"{before:8.2f} -> {after:8.2f} дБ "
            f"(зміна {difference:+.2f} дБ)"
        )

    # Графіки спектра до та після підсилення низьких частот.
    n = len(x)
    fr = np.fft.rfftfreq(n, 1 / SR)
    before_sp = np.abs(np.fft.rfft(x))
    after_sp = np.abs(np.fft.rfft(y))

    plt.figure(figsize=(10, 5))
    plt.plot(fr, 20 * np.log10(before_sp / (before_sp.max() + 1e-15) + 1e-12),
             label="До еквалайзера")
    plt.plot(fr, 20 * np.log10(after_sp / (after_sp.max() + 1e-15) + 1e-12),
             label="Після еквалайзера")
    plt.xlim(0, 5000)
    plt.xlabel("Частота, Гц")
    plt.ylabel("Амплітуда, дБ")
    plt.title("Спектр до і після еквалайзера")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("eq_before_after.png", dpi=150)
    plt.close()

    # Пресет «більше басу»: підсилюємо низькі частоти.
    bass = eq(x, [(0, 250, 8), (250, 500, 3)])
    save_wav("preset_bass.wav", bass)

    # Пресет «голос уперед»: підсилюємо діапазон розбірливості голосу.
    voice = eq(x, [(200, 500, -2), (1000, 3500, 5), (3500, 5000, 2)])
    save_wav("preset_voice.wav", voice)

    # Пресет «телефонний звук»: залишаємо приблизно 300–3000 Гц.
    phone = eq(x, [(0, 300, -60), (3000, SR // 2 + 1, -60)])
    save_wav("preset_phone.wav", phone)

    save_wav("eq_test_plus12db.wav", y)


def main():
    print("Лабораторна робота №13 — Спектральний аналіз")
    source = music()
    save_wav("source.wav", source)

    task1_spectrum_and_spectrogram(source)
    task2_compare_windows()
    task3_time_frequency()
    task4_equalizer(source)

    print("\nГотово! Створено WAV-файли, графіки та таблиці вимірювань.")


if __name__ == "__main__":
    main()
