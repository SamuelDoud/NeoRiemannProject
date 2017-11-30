import numpy
import pysynth_b as ps
from pysynth_b import *
import wave
from pydub import AudioSegment


def make_wav_from_notes(notes, filename):
	sounds = []
	filename = filename.replace(".wav", "") + ".wav"
	note_play = tuple([(n, 4) for n in notes])
	for i in range(3):
		name = "sound_" + str(i) +".wav"
		ps.make_wav(note_play[i::3], fn=name)
		sounds.append(AudioSegment.from_wav(name))
	combined = (sounds[0].overlay(sounds[1])).overlay(sounds[2])
	combined.export(filename, format="wav")