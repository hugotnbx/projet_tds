from flask import Flask, jsonify
import numpy as np
from scipy import signal
from scipy.io import wavfile
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Liste des fichiers à classifier
files_to_classify = ['alarms/hyper.wav', 'alarms/hypo.wav', 'alarms/vache_hyper.wav']

# Listes de classification des signaux
hyper_signals = []
hypo_signals = []
other_signals = []

# Signaux de références
Fs, reference_hyper = wavfile.read('alarms/hyper.wav')
Fs, reference_hypo = wavfile.read('alarms/hypo.wav')

def nomalize_signal(s):
    max_amplitude = np.max(np.abs(s))
    return s / max_amplitude

def convert_to_mono(s):
    if len(s.shape) == 2:  
        return s.mean(axis=1)
    return s

def filter_signal(s, Fs, center_freq, bandwidth=2):
    nyquist = Fs / 2
    Wn1 = (center_freq - bandwidth) / nyquist
    Wn2 = (center_freq + bandwidth) / nyquist
    Wn = [Wn1, Wn2]
    b, a = signal.butter(1, Wn, btype='stop')
    return signal.filtfilt(b, a, s)

def apply_filter(Fs, s):
    frequencies = [1312, 1410, 1500, 1619, 1722]
    for f in frequencies:
        s = filter_signal(s, Fs, f)
    return s

def calculate_similarity(s, s_reference):
    s = (s - np.mean(s)) / np.std(s)
    s_reference = (s_reference - np.mean(s_reference)) / np.std(s_reference)
    s = nomalize_signal(s)
    s_reference = nomalize_signal(s_reference)
    correlation = np.correlate(s, s_reference, mode='valid')
    return np.max(np.abs(correlation))

def classify_signal(file, reference_hyper, reference_hypo, threshold=0.8):
    global hyper_signals, hypo_signals, other_signals
    Fs, s = wavfile.read(file)
    s = convert_to_mono(s)
    s = apply_filter(Fs, s)
    similarity_hyper = calculate_similarity(s, reference_hyper)
    similarity_hypo = calculate_similarity(s, reference_hypo)

    if similarity_hyper >= threshold and similarity_hyper > similarity_hypo:
        hyper_signals.append(file)
    elif similarity_hypo >= threshold and similarity_hypo > similarity_hyper:
        hypo_signals.append(file)
    else:
        other_signals.append(file)

@app.route('/classify', methods=['GET'])
def classify():
    global hyper_signals, hypo_signals, other_signals
    hyper_signals.clear()
    hypo_signals.clear()
    other_signals.clear()

    for file in files_to_classify:
        classify_signal(file, reference_hyper, reference_hypo)

    return jsonify({
        'hyper_signals': hyper_signals,
        'hypo_signals': hypo_signals,
        'other_signals': other_signals
    })

if __name__ == '__main__':
    app.run(debug=True)
