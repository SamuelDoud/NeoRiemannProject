import itertools

import numpy
import pysynth as ps
from pysynth import *
import wave
from pydub import AudioSegment


def make_wav_from_notes(notes, filename):
    """Creates a .wav file from a set of notes.
    The notes are taken in groups of 3s and a .wav file
    is created from each of those. Then these files are
    stitched together."""
    sounds = []
    filename = filename.replace(".wav", "") + ".wav"
    note_play = tuple([(n, 1) for n in itertools.chain(*notes)])

    for i in range(3):
        name = "sound_" + str(i) + ".wav"
        ps.make_wav(note_play[i::3], fn=name)
        sounds.append(AudioSegment.from_wav(name))
    combined = (sounds[0].overlay(sounds[1])).overlay(sounds[2])
    combined.export(filename, format="wav")
