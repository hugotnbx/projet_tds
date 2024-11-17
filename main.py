import numpy as np
from scipy import signal
from scipy.io import wavfile

# Liste des signaux à classifier
files_to_classify = ['alarms/hyper.wav', 'alarms/hypo.wav', 'alarms/vache_hyper.wav', 'alarms/moustique_hyper.wav', 'alarms/hyper_fanfare.wav', 'alarms/hypo_fanfare.wav'] 

# Listes de classification des signaux
hyper_signals = []
hypo_signals = []
other_signals = []

# Signaux de références
Fs, reference_hyper = wavfile.read('alarms/hyper.wav')
Fs, reference_hypo = wavfile.read('alarms/hypo.wav')

# Fonction pour convertir un signal stéréo en mono
def convert_to_mono(s):
    if len(s.shape) == 2:  
        s = s.mean(axis=1) 
        
    return s

# Fonction pour filtrer un signal
def filter_signal(s, Fs, center_freq, bandwidth=2):
    nyquist = Fs / 2
    Wn1 = (center_freq - bandwidth) / nyquist
    Wn2 = (center_freq + bandwidth) / nyquist
    Wn = [Wn1, Wn2]
    
    b, a = signal.butter(1, Wn, btype='stop')
    s = signal.filtfilt(b, a, s)
    
    return s

# Fonction pour appliquer le filtrage d'un signal
def apply_filter(Fs, s):
    frequencies = [1312, 1410, 1500, 1619, 1722] 
    
    for f in frequencies:
        s = filter_signal(s, Fs, f)

    return s

# # Fonction pour filtrer un signal
# def filter_signal(s, Wn1, Wn2, type, Fs):
#     Wn = [Wn1 / (Fs / 2), Wn2 / (Fs / 2)] 
#     b, a = signal.butter(1, Wn, type) 
#     s = signal.filtfilt(b, a, s)
    
#     return s

# # Fonction pour appliquer le filtrage d'un signal
# def apply_filter(Fs, s):
#     s = filter_signal(s, 1311, 1723, 'band', Fs)
#     s = filter_signal(s, 1313, 1409, 'stop', Fs)
#     s = filter_signal(s, 1411, 1499, 'stop', Fs)
#     s = filter_signal(s, 1501, 1618, 'stop', Fs)
#     s = filter_signal(s, 1620, 1721, 'stop', Fs)

#     return s

# Fonction permettant de calculer la similarité entre deux signaux
def calculate_similarity(s, s_reference):
    s = (s - np.mean(s)) / np.std(s)
    s_reference = (s_reference - np.mean(s_reference)) / np.std(s_reference)

    correlation = np.correlate(s, s_reference, mode='valid')
    max_corr = np.max(np.abs(correlation))

    return max_corr

# Fonction permettant de classifier un signal
def classify_signal(file, reference_hyper, reference_hypo, threshold=0.8):
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

# Classification des signaux
for file in files_to_classify:
    classify_signal(file, reference_hyper, reference_hypo)

# Affichage des résultats
print("Signaux d'hyperglycémie :", hyper_signals)
print("Signaux hypoglycémie :", hypo_signals)
print("Autres signaux :", other_signals)