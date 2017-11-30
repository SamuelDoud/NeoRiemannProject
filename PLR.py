import re

import Player

class PLR(object):
    def __init__(self, mod=12):  
        self.function_unravel_re = re.compile(r"(\([PLR]+\)[0-9]+)|([PLR]+)")
        self.function_unravel_power_re = re.compile(r"[0-9]+")
        self.function_unravel_extract_re = re.compile(r"[PLR]*")
        self.mod_int = mod
        self.function_mapping = {"P":self.P, "L":self.L, "R":self.R}
      
    def P(self, chord):
        return self.I(chord, n=chord.x+chord.z)

    def L(self, chord):
        return self.I(chord, n=chord.y+chord.z)

    def R(self, chord):
        return self.I(chord, n=chord.x+chord.y)

    def T(self, chord, n):
        return Chord(self.modulo(chord.x + n), self.modulo(chord.y + n),  self.modulo(chord.z + n))

    def I(self, chord, n):
        return Chord(self.modulo(-1 * chord.x + n), self.modulo(-1 * chord.y + n),  self.modulo(-1 * chord.z + n))

    def modulo(self, n):
        return n % self.mod_int

    def transform(self, function, start_chord, all_chords=False):
        #read Left to Right
        chord_map = [start_chord]
        for key in reversed(self.function_unravel(function.upper())):
            chord_map.append(self.function_mapping[key](chord_map[-1]))
        if not all_chords:
            return chord_map[-1]
        return chord_map

    def function_unravel(self, function_str):
        res_funct = ""
        functions = self.function_unravel_re.findall(function_str)
        for function in functions:
            function = ''.join(function)
            power = self.function_unravel_power_re.findall(function)
            function = ''.join(self.function_unravel_extract_re.findall(function))
            res_funct += function * (int(power[0]) if power else 1)
        return res_funct

    def make_music(self, function, base_chord):
        results = self.transform(function, base_chord, all_chords=True)
        notes = []
        for result in results:
            notes += result.to_notes()
        Player.make_wav_from_notes(notes, str(base_chord.chord_name()) + "-" + str(function))

    def __len__(self):
        return 0

class Chord(object):
    chord_map_order = ["c", "db", "d", "eb", "e", "f", "f#", "g", "ab", "a", "bb", "b"]
    inverted_chord_map_order = ["fm", "f#m", "gm", "g#m", "am", "bbm", "bm", "cm", "c#m", "dm", "d#m", "em"]
    notes = ["c", "c#", "d", "eb", "e", "f", "f#", "g", "ab", "a", "bb", "b"]
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.chord_map = {}
        self.construct()

    def construct(self):
        mod = len(Chord.notes)
        start_chord = (0, 4, 7)
        inverted_start_chord = (0, 8, 5)
        for i in range(mod):
            self.chord_map[Chord.add_to(start_chord, i, mod)] = Chord.chord_map_order[i]
            self.chord_map[Chord.add_to(inverted_start_chord, i, mod)] = Chord.inverted_chord_map_order[i]

    def convert(tup):
        return tuple(Chord.notes[x] for x in tup)

    def minor(self):
        pass

    def chord_name(self):
        return self.chord_map[(self.x, self.y, self.z)]

    def to_notes(self):
        return (Chord.notes[self.x], Chord.notes[self.y], Chord.notes[self.z])

    def order(self):
        pass

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"

    def __eq__(self, other):
        return (self.x == other.x and self.y == other.y and self.z == other.z)

    def add_to(tup, add, mod=12):
        return tuple((((x + add) % mod) for x in tup))

#this is the PLR function object, you define the mod here
PLR_test = PLR(12)
#this is a sample chord
chord_test = Chord(0, 4, 7)
#Just showing how functions are written
print(PLR_test.function_unravel("PLR(PL)4PPPL(LR)2L"))
print(PLR_test.L(chord_test))
#you can transform a chord with a function string
results = PLR_test.transform("PLR(PL)4PPP", chord_test, all_chords=True)
notes = []
for result in results:
    print(result.to_notes())
    notes += result.to_notes()

#Player.make_wav_from_notes(notes, "test_construction")
PLR_test.make_music("(LR)9", Chord(0,8,5))
