import numpy as np
import sounddevice as sd
from scipy.io.wavfile import read, write
import os

path = "C:/Users/0ropo/Documents/Cours/bac3/traitements de signaux/projetTDS/sons/recorded_sound.wav"
# path = "C:/Users/Hugo Troonbeeckx/OneDrive - EPHEC asbl/Documents/BAC3/Q1/Traitement des signaux et données/Projet/projet_tds/alarms/recorded_sound.wav"

def sound_recording(duration):
    fe = 44100
    recorded_sound = sd.rec(int(duration * fe), samplerate=fe, channels=1, dtype='float64')
    #pwd=os.getcwd()
    print("Recording Audio")
    sd.wait()
    print("Audio recording complete , Play Audio")
    sd.play(recorded_sound, fe)
    sd.wait()
    print("Play Audio Complete")
    write(path, fe, recorded_sound)
    return np.squeeze(recorded_sound)