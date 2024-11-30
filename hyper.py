import numpy as np
import sounddevice as sd
from scipy import signal

A = 4
duree = 0.15
Fe = 22000
Te = 1 / Fe

frequencies = [1312, 1410, 1500, 1619, 1722]

t = np.arange(0, duree + Te, Te)

signals = []

for i in range(len(frequencies)):
    signal = A * np.sin(2 * np.pi * frequencies[i] * t)  
    signals.extend(signal)

signal = np.array(signals)

sd.play(signal, samplerate=Fe)