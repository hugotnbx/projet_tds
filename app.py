from flask import Flask, jsonify, request
from scipy.signal import spectrogram, butter, filtfilt
from scipy.io import wavfile
import numpy as np
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

target_frequencies = [1312, 1410, 1500, 1619, 1722]

def convert_to_mono(s):
    if len(s.shape) == 2:
        s = s.mean(axis=1)
    return s

def filter_signal(s, Wn1, Wn2, type, Fs):
    Wn = [Wn1 / (Fs / 2), Wn2 / (Fs / 2)]
    b, a = butter(1, Wn, type)
    s = filtfilt(b, a, s)
    return s

def apply_filter(Fs, s):
    s = filter_signal(s, 1311, 1723, 'band', Fs) 
    s = filter_signal(s, 1313, 1409, 'stop', Fs)
    s = filter_signal(s, 1411, 1499, 'stop', Fs)  
    s = filter_signal(s, 1501, 1618, 'stop', Fs)  
    s = filter_signal(s, 1620, 1721, 'stop', Fs) 
    return s

def read_file(file_path):
    Fs, s = wavfile.read(file_path)
    s = convert_to_mono(s)
    s = apply_filter(Fs, s)
    return Fs, s

def filter_spectrogram(frequencies, spectrogram, freq_min, freq_max):
    indices = (frequencies >= freq_min) & (frequencies <= freq_max)
    return frequencies[indices], spectrogram[indices, :]

def find_max_amplitude(f, t, Sxx, target_frequencies):
    results = []
    for target_frequency in target_frequencies:
        freq_index = np.abs(f - target_frequency).argmin()
        amplitude_at_freq = Sxx[freq_index, :]
        max_index = np.argmax(amplitude_at_freq)
        results.append((target_frequency, t[max_index], amplitude_at_freq[max_index]))
    return results

def classify_signal(max_amplitudes):
    times = [t_max for _, t_max, _ in max_amplitudes]

    for i in range(len(times) - 1):
        if abs(times[i + 1] - times[i]) > 0.35:
            return "indéterminé"
    
    if times == sorted(times):
        return "hyper"
    elif times == sorted(times, reverse=True):
        return "hypo"
    else:
        return "indéterminé"

@app.route('/analyze', methods=['POST'])
def analyze_signal():
    data = request.get_json()
    file_path = data.get('file_path')

    if not file_path:
        return jsonify({"error": "Chemin du fichier manquant"}), 400

    try:
        Fs, s = read_file(file_path)
        f, t, Sxx = spectrogram(s, Fs, window='hamming', nperseg=1024, noverlap=512)
        f_filtered, Sxx_filtered = filter_spectrogram(f, Sxx, 1000, 2000)
        max_amplitudes = find_max_amplitude(f_filtered, t, Sxx_filtered, target_frequencies)
        signal_class = classify_signal(max_amplitudes)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.pcolormesh(t, f_filtered, np.log10(Sxx_filtered + 1e-10), shading='gouraud')
        for target_frequency, t_max, _ in max_amplitudes:
            ax.axvline(x=t_max, color='red', linestyle='--', label=f'{target_frequency} Hz - {t_max:.2f}s')
        ax.set_ylabel('Fréquences (Hz)')
        ax.set_xlabel('Temps (s)')
        ax.set_title(f"Spectrogramme du signal filtré (1000-2000 Hz)")
        ax.legend()

        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        plt.close(fig)

        return jsonify({
            "classification": signal_class,
            "spectrogram": output.getvalue().decode('latin1')
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
