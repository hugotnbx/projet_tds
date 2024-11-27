from flask import Flask, jsonify, request
from scipy.signal import spectrogram, butter, filtfilt
from scipy.io import wavfile
import numpy as np
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
    if times == sorted(times):
        return "hyper"
    elif times == sorted(times, reverse=True):
        return "hypo"
    else:
        return "indéterminé"

@app.route('/classify', methods=['GET'])
def classify():
    files = [
            'alarms/hyper.wav', 'alarms/hypo.wav', 
            'alarms/new/hyper_vache_0DB.wav', 'alarms/new/hyper_vache_10DB.wav', 'alarms/new/hyper_vache_20DB.wav', 'alarms/new/hyper_vache_30DB.wav',
            'alarms/new/hypo_vache_0DB.wav', 'alarms/new/hypo_vache_10DB.wav', 'alarms/new/hypo_vache_20DB.wav', 'alarms/new/hypo_vache_30DB.wav',
            'alarms/new/hyper_bébé_0DB.wav', 'alarms/new/hyper_bébé_10DB.wav', 'alarms/new/hyper_bébé_20DB.wav', 'alarms/new/hyper_bébé_30DB.wav',
            'alarms/new/hypo_bébé_0DB.wav', 'alarms/new/hypo_bébé_10DB.wav', 'alarms/new/hypo_bébé_20DB.wav', 'alarms/new/hypo_bébé_30DB.wav',
            'alarms/new/hyper_chien_0DB.wav', 'alarms/new/hyper_chien_10DB.wav', 'alarms/new/hyper_chien_20DB.wav', 'alarms/new/hyper_chien_30DB.wav',
            'alarms/new/hypo_chien_0DB.wav', 'alarms/new/hypo_chien_10DB.wav', 'alarms/new/hypo_chien_20DB.wav', 'alarms/new/hypo_chien_30DB.wav',
            'alarms/new/hyper_discussion_0DB.wav', 'alarms/new/hyper_discussion_10DB.wav', 'alarms/new/hyper_discussion_20DB.wav', 'alarms/new/hyper_discussion_30DB.wav',
            'alarms/new/hypo_discussion_0DB.wav', 'alarms/new/hypo_discussion_10DB.wav', 'alarms/new/hypo_discussion_20DB.wav', 'alarms/new/hypo_discussion_30DB.wav',
            'alarms/new/hyper_moustique_0DB.wav', 'alarms/new/hyper_moustique_10DB.wav', 'alarms/new/hyper_moustique_20DB.wav', 'alarms/new/hyper_moustique_30DB.wav',
            'alarms/new/hypo_moustique_0DB.wav', 'alarms/new/hypo_moustique_10DB.wav', 'alarms/new/hypo_moustique_20DB.wav', 'alarms/new/hypo_moustique_30DB.wav',
            ]
    results = {"hyper_signals": [], "hypo_signals": [], "other_signals": []}
    
    for file_path in files:
        Fs, s = read_file(file_path)
        f, t, Sxx = spectrogram(s, Fs, window='hamming', nperseg=1024, noverlap=512)
        f_filtered, Sxx_filtered = filter_spectrogram(f, Sxx, 1000, 2000)
        max_amplitudes = find_max_amplitude(f_filtered, t, Sxx_filtered, target_frequencies)
        classification = classify_signal(max_amplitudes)
        
        if classification == "hyper":
            results["hyper_signals"].append(file_path)
        elif classification == "hypo":
            results["hypo_signals"].append(file_path)
        else:
            results["other_signals"].append(file_path)
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
