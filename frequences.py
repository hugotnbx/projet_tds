from numpy import fft
import numpy as np
from scipy.io import wavfile

file = 'alarms/hyper.wav'

Fs, s = wavfile.read(file)

f  = fft.fftfreq(len(s), 1/Fs)
TF = fft.fft(s)  

frequence_cible = 1312
indice_cible = np.argmin(np.abs(f - frequence_cible))

masque = np.zeros_like(TF)
masque[indice_cible] = 1 

signal_isole_frequentiel = TF * masque

indice_max = np.argmax(signal_isole_frequentiel)
valeur_max = signal_isole_frequentiel[indice_max]

print(indice_max)
print(valeur_max)
