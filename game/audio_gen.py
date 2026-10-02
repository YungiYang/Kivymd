"""Генератор синтезованих звукових ефектів та фонової музики у форматі WAV для всіх біомів."""

import os
import math
import struct
import wave
import random

SAMPLE_RATE = 44100


def _save_wav(filepath: str, samples: list[float], sample_rate: int = SAMPLE_RATE):
    """Зберігає список нормалізованих чисел (-1.0 ... 1.0) у 16-бітний WAV файл."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with wave.open(filepath, "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)

        peak = max(abs(s) for s in samples) if samples else 1.0
        scale = (32767.0 * 0.95) / (peak if peak > 0 else 1.0)

        raw_bytes = bytearray()
        for s in samples:
            val = int(max(-32767, min(32767, s * scale)))
            raw_bytes.extend(struct.pack("<h", val))
        wav_file.writeframes(raw_bytes)


def generate_laser_sound(path: str):
    """Лазерний постріл: швидкий спадний частотний свіп."""
    duration = 0.16
    n_samples = int(duration * SAMPLE_RATE)
    samples = []
    phase = 0.0
    for i in range(n_samples):
        progress = i / n_samples
        freq = 1100.0 * (1.0 - progress) ** 1.8 + 220.0
        phase += 2.0 * math.pi * freq / SAMPLE_RATE
        s = 0.7 * math.sin(phase) + 0.3 * (1.0 if math.sin(phase) > 0 else -1.0)
        env = (1.0 - progress) ** 1.5
        samples.append(s * env)
    _save_wav(path, samples)


def generate_beam_sound(path: str):
    """Фотонний безперервний промінь: пульсуючий енергетичний гул."""
    duration = 0.45
    n_samples = int(duration * SAMPLE_RATE)
    samples = []
    p1, p2, p3 = 0.0, 0.0, 0.0
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        f1 = 440.0 + 15.0 * math.sin(2.0 * math.pi * 8.0 * t)
        f2 = 446.0 - 15.0 * math.cos(2.0 * math.pi * 8.0 * t)
        f3 = 110.0
        p1 += 2.0 * math.pi * f1 / SAMPLE_RATE
        p2 += 2.0 * math.pi * f2 / SAMPLE_RATE
        p3 += 2.0 * math.pi * f3 / SAMPLE_RATE
        s = 0.45 * math.sin(p1) + 0.35 * math.sin(p2) + 0.20 * math.sin(p3)
        fade = min(1.0, i / (SAMPLE_RATE * 0.03)) * min(1.0, (n_samples - i) / (SAMPLE_RATE * 0.03))
        samples.append(s * fade)
    _save_wav(path, samples)


def generate_charge_sound(path: str):
    """Накопичення енергії заряду: висхідний тон із частотним тремоло."""
    duration = 0.65
    n_samples = int(duration * SAMPLE_RATE)
    samples = []
    phase = 0.0
    for i in range(n_samples):
        progress = i / n_samples
        freq = 160.0 + (progress ** 2.0) * 780.0
        phase += 2.0 * math.pi * freq / SAMPLE_RATE
        s = math.sin(phase) * (0.8 + 0.2 * math.sin(2.0 * math.pi * 16.0 * (i / SAMPLE_RATE)))
        env = progress ** 0.8
        samples.append(s * env)
    _save_wav(path, samples)


def generate_plasma_sound(path: str):
    """Важкий плазмовий залп: басовий удар та плазмовий сплеск."""
    duration = 0.32
    n_samples = int(duration * SAMPLE_RATE)
    samples = []
    phase = 0.0
    for i in range(n_samples):
        progress = i / n_samples
        freq = 240.0 * (1.0 - progress) ** 2.5 + 48.0
        phase += 2.0 * math.pi * freq / SAMPLE_RATE
        s = math.sin(phase) + 0.35 * (random.random() * 2.0 - 1.0) * (1.0 - progress)
        env = (1.0 - progress) ** 1.3
        samples.append(s * env)
    _save_wav(path, samples)


def generate_explosion_sound(path: str):
    """Вибух звичайного ворожого судна."""
    duration = 0.45
    n_samples = int(duration * SAMPLE_RATE)
    samples = []
    phase = 0.0
    for i in range(n_samples):
        progress = i / n_samples
        freq = 150.0 * (1.0 - progress) ** 1.5 + 35.0
        phase += 2.0 * math.pi * freq / SAMPLE_RATE
        noise = random.random() * 2.0 - 1.0
        s = 0.45 * math.sin(phase) + 0.55 * noise
        env = (1.0 - progress) ** 1.4
        samples.append(s * env)
    _save_wav(path, samples)


def generate_boss_explosion_sound(path: str):
    """Потужний тривалий вибух боса."""
    duration = 1.35
    n_samples = int(duration * SAMPLE_RATE)
    samples = []
    phase = 0.0
    for i in range(n_samples):
        progress = i / n_samples
        freq = 90.0 * (1.0 - progress) ** 1.2 + 25.0
        phase += 2.0 * math.pi * freq / SAMPLE_RATE
        noise = random.random() * 2.0 - 1.0
        rumble = math.sin(2.0 * math.pi * 32.0 * (i / SAMPLE_RATE))
        s = 0.35 * math.sin(phase) + 0.45 * noise + 0.20 * rumble
        env = (1.0 - progress) ** 1.1
        samples.append(s * env)
    _save_wav(path, samples)


def generate_hit_sound(path: str):
    """Влучання по корпусу корабля."""
    duration = 0.12
    n_samples = int(duration * SAMPLE_RATE)
    samples = []
    phase = 0.0
    for i in range(n_samples):
        progress = i / n_samples
        freq = 360.0 * (1.0 - progress) + 70.0
        phase += 2.0 * math.pi * freq / SAMPLE_RATE
        noise = (random.random() * 2.0 - 1.0) * 0.4
        s = math.sin(phase) + noise
        env = (1.0 - progress) ** 2.0
        samples.append(s * env)
    _save_wav(path, samples)


def generate_shield_sound(path: str):
    """Сяючий кристал силового поля."""
    duration = 0.32
    n_samples = int(duration * SAMPLE_RATE)
    samples = []
    p1, p2, p3 = 0.0, 0.0, 0.0
    for i in range(n_samples):
        progress = i / n_samples
        p1 += 2.0 * math.pi * 980.0 / SAMPLE_RATE
        p2 += 2.0 * math.pi * 1470.0 / SAMPLE_RATE
        p3 += 2.0 * math.pi * 1960.0 / SAMPLE_RATE
        s = 0.45 * math.sin(p1) + 0.35 * math.sin(p2) + 0.20 * math.sin(p3)
        env = (1.0 - progress) ** 1.6
        samples.append(s * env)
    _save_wav(path, samples)


def generate_upgrade_sound(path: str):
    """Урочистий висхідний акорд при виборі покращення."""
    notes = [523.25, 659.25, 783.99, 1046.50]  # C5, E5, G5, C6
    note_dur = 0.09
    samples = []
    for idx, f in enumerate(notes):
        n_samples = int(note_dur * SAMPLE_RATE)
        phase = 0.0
        for i in range(n_samples):
            progress = i / n_samples
            phase += 2.0 * math.pi * f / SAMPLE_RATE
            s = math.sin(phase) + 0.25 * math.sin(phase * 2.0)
            env = (1.0 - progress * 0.4) if idx == len(notes) - 1 else (1.0 - progress)
            samples.append(s * env)
    tail_dur = 0.25
    n_tail = int(tail_dur * SAMPLE_RATE)
    f = notes[-1]
    phase = 0.0
    for i in range(n_tail):
        progress = i / n_tail
        phase += 2.0 * math.pi * f / SAMPLE_RATE
        s = math.sin(phase) + 0.2 * math.sin(phase * 2.0)
        env = (1.0 - progress) ** 1.8
        samples.append(s * env)
    _save_wav(path, samples)


def generate_warning_sound(path: str):
    """Сирена тривоги перед появою боса."""
    duration = 0.65
    n_samples = int(duration * SAMPLE_RATE)
    samples = []
    phase = 0.0
    for i in range(n_samples):
        progress = i / n_samples
        is_high = int(progress * 4.0) % 2 == 0
        freq = 880.0 if is_high else 660.0
        phase += 2.0 * math.pi * freq / SAMPLE_RATE
        s = math.sin(phase)
        env = 0.85 + 0.15 * math.sin(2.0 * math.pi * 6.0 * (i / SAMPLE_RATE))
        samples.append(s * env)
    _save_wav(path, samples)


def generate_game_over_sound(path: str):
    """Сумний низхідний мотив завершення гри."""
    notes = [659.25, 587.33, 493.88, 440.0]  # E5, D5, B4, A4
    note_dur = 0.14
    samples = []
    for f in notes:
        n_samples = int(note_dur * SAMPLE_RATE)
        phase = 0.0
        for i in range(n_samples):
            progress = i / n_samples
            phase += 2.0 * math.pi * f / SAMPLE_RATE
            s = math.sin(phase) + 0.2 * math.sin(phase * 2.0)
            env = (1.0 - progress) ** 1.5
            samples.append(s * env)
    _save_wav(path, samples)


# === НОВІ ЗВУКОВІ ЕФЕКТИ ДЛЯ БІОМІВ ТА СТАТУСНИХ ЕФЕКТІВ ===


def generate_burn_sound(path: str):
    """Шипіння полум'я та підпалу корабля."""
    duration = 0.38
    n_samples = int(duration * SAMPLE_RATE)
    samples = []
    for i in range(n_samples):
        progress = i / n_samples
        noise = random.random() * 2.0 - 1.0
        pop = 1.0 if random.random() < 0.04 else 0.0
        s = (noise * 0.75 + pop * 0.6) * (0.8 + 0.2 * math.sin(2.0 * math.pi * 25.0 * (i / SAMPLE_RATE)))
        env = (1.0 - progress) ** 1.2
        samples.append(s * env * 0.65)
    _save_wav(path, samples)


def generate_freeze_sound(path: str):
    """Крижаний дзвін та заморожування корпусу."""
    duration = 0.40
    n_samples = int(duration * SAMPLE_RATE)
    samples = []
    p1, p2 = 0.0, 0.0
    for i in range(n_samples):
        progress = i / n_samples
        f1 = 1800.0 * (1.0 - progress * 0.4)
        f2 = 2700.0 * (1.0 - progress * 0.3)
        p1 += 2.0 * math.pi * f1 / SAMPLE_RATE
        p2 += 2.0 * math.pi * f2 / SAMPLE_RATE
        s = 0.6 * math.sin(p1) + 0.4 * math.sin(p2)
        env = (1.0 - progress) ** 1.5
        samples.append(s * env)
    _save_wav(path, samples)


def generate_shock_sound(path: str):
    """Електричний дуговий розряд та EMP удар."""
    duration = 0.28
    n_samples = int(duration * SAMPLE_RATE)
    samples = []
    phase = 0.0
    for i in range(n_samples):
        progress = i / n_samples
        f = 120.0 + random.uniform(-30.0, 30.0)
        phase += 2.0 * math.pi * f / SAMPLE_RATE
        buzz = 1.0 if math.sin(phase) > 0 else -1.0
        noise = (random.random() * 2.0 - 1.0) * 0.5
        s = 0.65 * buzz + 0.35 * noise
        env = (1.0 - progress) ** 1.3
        samples.append(s * env)
    _save_wav(path, samples)


def generate_splash_sound(path: str):
    """Сплеск води та удар гідро-торпеди."""
    duration = 0.35
    n_samples = int(duration * SAMPLE_RATE)
    samples = []
    phase = 0.0
    for i in range(n_samples):
        progress = i / n_samples
        f = 460.0 * (1.0 - progress) ** 2.0 + 80.0
        phase += 2.0 * math.pi * f / SAMPLE_RATE
        noise = (random.random() * 2.0 - 1.0) * 0.6 * (1.0 - progress)
        s = 0.5 * math.sin(phase) + 0.5 * noise
        env = (1.0 - progress) ** 1.4
        samples.append(s * env)
    _save_wav(path, samples)


def generate_warp_sound(path: str):
    """Гіперпросторовий стрибок при зміні рівня."""
    duration = 0.85
    n_samples = int(duration * SAMPLE_RATE)
    samples = []
    phase = 0.0
    for i in range(n_samples):
        progress = i / n_samples
        freq = 80.0 + (progress ** 1.8) * 920.0
        phase += 2.0 * math.pi * freq / SAMPLE_RATE
        whoosh = (random.random() * 2.0 - 1.0) * (0.3 + 0.5 * progress)
        s = 0.6 * math.sin(phase) + 0.4 * whoosh
        env = math.sin(math.pi * progress) ** 0.8
        samples.append(s * env)
    _save_wav(path, samples)


# === МУЗИЧНІ ТРЕКИ ДЛЯ 5 БІОМІВ ===


def generate_bgm_track(path: str):
    """Космічний саундтрек за замовчуванням (Space)."""
    bpm = 120
    beat_dur = 60.0 / bpm
    total_beats = 16
    total_samples = int(beat_dur * total_beats * SAMPLE_RATE)
    samples = [0.0] * total_samples
    bass_roots = [73.42, 58.27, 65.41, 55.0]  # D, Bb, C, A

    for bar in range(4):
        root = bass_roots[bar]
        bar_start = int(bar * 4 * beat_dur * SAMPLE_RATE)
        for sixteenth in range(16):
            note_start = bar_start + int(sixteenth * (beat_dur / 4.0) * SAMPLE_RATE)
            note_len = int((beat_dur / 4.0) * SAMPLE_RATE * 0.85)
            phase = 0.0
            for i in range(note_len):
                idx = note_start + i
                if idx < total_samples:
                    phase += 2.0 * math.pi * root / SAMPLE_RATE
                    val = 0.5 * math.sin(phase) + 0.25 * math.sin(phase * 2.0)
                    env = (1.0 - i / note_len) ** 1.4
                    samples[idx] += val * env * 0.45

    for b in range(total_beats):
        kick_start = int(b * beat_dur * SAMPLE_RATE)
        kick_len = int(0.12 * SAMPLE_RATE)
        k_phase = 0.0
        for i in range(kick_len):
            idx = kick_start + i
            if idx < total_samples:
                prog = i / kick_len
                k_freq = 130.0 * (1.0 - prog) ** 3.0 + 42.0
                k_phase += 2.0 * math.pi * k_freq / SAMPLE_RATE
                samples[idx] += math.sin(k_phase) * (1.0 - prog) * 0.55

        hh_start = kick_start + int((beat_dur / 2.0) * SAMPLE_RATE)
        hh_len = int(0.04 * SAMPLE_RATE)
        for i in range(hh_len):
            idx = hh_start + i
            if idx < total_samples:
                prog = i / hh_len
                samples[idx] += (random.random() * 2.0 - 1.0) * (1.0 - prog) * 0.18

    melody_notes = [
        293.66, 349.23, 440.00, 587.33,
        233.08, 293.66, 349.23, 466.16,
        261.63, 329.63, 392.00, 523.25,
        220.00, 261.63, 329.63, 440.00,
    ]
    for step, freq in enumerate(melody_notes):
        step_start = int(step * beat_dur * SAMPLE_RATE)
        step_len = int(beat_dur * SAMPLE_RATE * 0.9)
        phase = 0.0
        for i in range(step_len):
            idx = step_start + i
            if idx < total_samples:
                phase += 2.0 * math.pi * freq / SAMPLE_RATE
                s = math.sin(phase) + 0.3 * math.sin(phase * 3.0)
                env = (1.0 - i / step_len) ** 1.2
                samples[idx] += s * env * 0.30

    _save_wav(path, samples)


def generate_lava_bgm(path: str):
    """Лавовий саундтрек: агресивний пульсуючий інферно-бас та важкий перкусійний біт."""
    bpm = 126
    beat_dur = 60.0 / bpm
    total_beats = 16
    total_samples = int(beat_dur * total_beats * SAMPLE_RATE)
    samples = [0.0] * total_samples
    roots = [43.65, 41.20, 36.71, 38.89]  # F1, E1, D1, Eb1 (важкий низький лавовий тон)

    for bar in range(4):
        root = roots[bar]
        b_start = int(bar * 4 * beat_dur * SAMPLE_RATE)
        for eighth in range(8):
            n_start = b_start + int(eighth * (beat_dur / 2.0) * SAMPLE_RATE)
            n_len = int((beat_dur / 2.0) * SAMPLE_RATE * 0.9)
            p = 0.0
            for i in range(n_len):
                idx = n_start + i
                if idx < total_samples:
                    p += 2.0 * math.pi * root / SAMPLE_RATE
                    distort = math.tanh(math.sin(p) * 2.2)
                    samples[idx] += distort * 0.40

    for b in range(total_beats):
        k_start = int(b * beat_dur * SAMPLE_RATE)
        k_len = int(0.16 * SAMPLE_RATE)
        p = 0.0
        for i in range(k_len):
            idx = k_start + i
            if idx < total_samples:
                prog = i / k_len
                freq = 150.0 * (1.0 - prog) ** 2.2 + 38.0
                p += 2.0 * math.pi * freq / SAMPLE_RATE
                samples[idx] += math.sin(p) * (1.0 - prog) * 0.65

    # Лавовий синтезаторний мотив
    lava_riff = [174.61, 207.65, 233.08, 196.00, 164.81, 196.00, 220.00, 155.56]
    for s_idx, f in enumerate(lava_riff * 2):
        s_start = int(s_idx * beat_dur * SAMPLE_RATE)
        s_len = int(beat_dur * SAMPLE_RATE * 0.8)
        p = 0.0
        for i in range(s_len):
            idx = s_start + i
            if idx < total_samples:
                p += 2.0 * math.pi * f / SAMPLE_RATE
                val = 0.7 * math.sin(p) + 0.3 * math.sin(p * 3.0)
                samples[idx] += val * (1.0 - i / s_len) ** 1.3 * 0.35

    _save_wav(path, samples)


def generate_water_bgm(path: str):
    """Водний океанічний саундтрек: плавні глибинні синтові пади та хвильове звучання."""
    bpm = 105
    beat_dur = 60.0 / bpm
    total_beats = 16
    total_samples = int(beat_dur * total_beats * SAMPLE_RATE)
    samples = [0.0] * total_samples
    water_chords = [
        [207.65, 261.63, 311.13],  # Ab major
        [174.61, 207.65, 261.63],  # F minor
        [155.56, 196.00, 233.08],  # Eb major
        [138.59, 174.61, 207.65],  # Db major
    ]

    for bar, chord in enumerate(water_chords):
        b_start = int(bar * 4 * beat_dur * SAMPLE_RATE)
        bar_len = int(4 * beat_dur * SAMPLE_RATE)
        for f in chord:
            p = 0.0
            for i in range(bar_len):
                idx = b_start + i
                if idx < total_samples:
                    t = i / SAMPLE_RATE
                    p += 2.0 * math.pi * f / SAMPLE_RATE
                    swell = 0.5 + 0.5 * math.sin(2.0 * math.pi * 0.25 * t)
                    samples[idx] += math.sin(p) * swell * 0.22

    # Водяні бульбашкові арпеджіо
    bubble_notes = [523.25, 622.25, 783.99, 932.33]
    for b in range(total_beats * 2):
        f = bubble_notes[b % len(bubble_notes)]
        st = int(b * (beat_dur / 2.0) * SAMPLE_RATE)
        ln = int(0.18 * SAMPLE_RATE)
        p = 0.0
        for i in range(ln):
            idx = st + i
            if idx < total_samples:
                p += 2.0 * math.pi * f / SAMPLE_RATE
                samples[idx] += math.sin(p) * (1.0 - i / ln) ** 2.0 * 0.18

    _save_wav(path, samples)


def generate_cyber_bgm(path: str):
    """Кібер-саундтрек: швидкий 135 BPM електронний арпеджіатор та неоновий драйв."""
    bpm = 135
    beat_dur = 60.0 / bpm
    total_beats = 16
    total_samples = int(beat_dur * total_beats * SAMPLE_RATE)
    samples = [0.0] * total_samples
    cyber_roots = [82.41, 98.00, 110.00, 123.47]  # E2, G2, A2, B2

    for bar in range(4):
        r = cyber_roots[bar]
        b_start = int(bar * 4 * beat_dur * SAMPLE_RATE)
        for sixteenth in range(16):
            n_start = b_start + int(sixteenth * (beat_dur / 4.0) * SAMPLE_RATE)
            n_len = int((beat_dur / 4.0) * SAMPLE_RATE * 0.75)
            p = 0.0
            for i in range(n_len):
                idx = n_start + i
                if idx < total_samples:
                    p += 2.0 * math.pi * r / SAMPLE_RATE
                    samples[idx] += (1.0 if math.sin(p) > 0 else -1.0) * (1.0 - i / n_len) * 0.32

    for b in range(total_beats):
        k_start = int(b * beat_dur * SAMPLE_RATE)
        k_len = int(0.10 * SAMPLE_RATE)
        p = 0.0
        for i in range(k_len):
            idx = k_start + i
            if idx < total_samples:
                p += 2.0 * math.pi * (140.0 * (1.0 - i / k_len) + 45.0) / SAMPLE_RATE
                samples[idx] += math.sin(p) * 0.60

    _save_wav(path, samples)


def generate_ice_bgm(path: str):
    """Крижаний саундтрек: кришталеві дзвіночки, холодні пади та прозорий ембієнт."""
    bpm = 110
    beat_dur = 60.0 / bpm
    total_beats = 16
    total_samples = int(beat_dur * total_beats * SAMPLE_RATE)
    samples = [0.0] * total_samples
    ice_chords = [440.0, 349.23, 523.25, 392.0]  # A, F, C, G

    for bar, root in enumerate(ice_chords):
        b_start = int(bar * 4 * beat_dur * SAMPLE_RATE)
        b_len = int(4 * beat_dur * SAMPLE_RATE)
        p1, p2 = 0.0, 0.0
        for i in range(b_len):
            idx = b_start + i
            if idx < total_samples:
                p1 += 2.0 * math.pi * root / SAMPLE_RATE
                p2 += 2.0 * math.pi * (root * 1.5) / SAMPLE_RATE
                samples[idx] += (0.6 * math.sin(p1) + 0.4 * math.sin(p2)) * 0.28

    ice_sparkles = [880.0, 1046.50, 1318.51, 1567.98, 1760.0]
    for b in range(total_beats * 2):
        f = ice_sparkles[b % len(ice_sparkles)]
        st = int(b * (beat_dur / 2.0) * SAMPLE_RATE)
        ln = int(0.15 * SAMPLE_RATE)
        p = 0.0
        for i in range(ln):
            idx = st + i
            if idx < total_samples:
                p += 2.0 * math.pi * f / SAMPLE_RATE
                samples[idx] += math.sin(p) * (1.0 - i / ln) ** 1.8 * 0.22

    _save_wav(path, samples)


def generate_all_audio(target_dir: str):
    """Генерує повний набір аудіофайлів гри (базові + біомні)."""
    os.makedirs(target_dir, exist_ok=True)
    sounds = {
        "laser.wav": generate_laser_sound,
        "beam.wav": generate_beam_sound,
        "charge.wav": generate_charge_sound,
        "plasma.wav": generate_plasma_sound,
        "explosion.wav": generate_explosion_sound,
        "boss_explosion.wav": generate_boss_explosion_sound,
        "hit.wav": generate_hit_sound,
        "shield.wav": generate_shield_sound,
        "upgrade.wav": generate_upgrade_sound,
        "warning.wav": generate_warning_sound,
        "game_over.wav": generate_game_over_sound,
        "burn.wav": generate_burn_sound,
        "freeze.wav": generate_freeze_sound,
        "shock.wav": generate_shock_sound,
        "splash.wav": generate_splash_sound,
        "warp.wav": generate_warp_sound,
        "bgm.wav": generate_bgm_track,
        "bgm_lava.wav": generate_lava_bgm,
        "bgm_water.wav": generate_water_bgm,
        "bgm_cyber.wav": generate_cyber_bgm,
        "bgm_ice.wav": generate_ice_bgm,
    }
    for filename, fn in sounds.items():
        file_path = os.path.join(target_dir, filename)
        fn(file_path)
    print(f"Всі {len(sounds)} аудіофайлів успішно згенеровано в {target_dir}!")


if __name__ == "__main__":
    audio_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "audio"
    )
    generate_all_audio(audio_dir)
