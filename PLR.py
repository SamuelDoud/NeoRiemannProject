import re
import random

import Player

class PLR(object):
    def __init__(self, mod=12):  
        self.function_unravel_re = re.compile(r"(\([\[\]PLR]+\)[0-9]+)|([\[\]PLR]+)")
        self.function_unravel_power_re = re.compile(r"[0-9]+")
        self.function_unravel_extract_re = re.compile(r"[\[\]PLR]*")
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

    def order(self, chord, function_str, max_index=100, make_music=True):
        name = "-".join(function_str)
        chord_start_list = [chord] +  [self.transform(f, chord) for f in function_str[1:]]
        function_str = function_str[0]
        encounter = []
        new_chord = chord
        chord_index = 0
        while chord_index < len(chord_start_list) and len(encounter) < max_index:
            encounter.append(new_chord)
            new_chord = self.transform(function_str, new_chord)
            if new_chord == chord_start_list[chord_index]:
                chord_index += 1
                if chord_index < len(chord_start_list):
                    new_chord = chord_start_list[chord_index]
        if make_music:
            self.make_music(name, chord, chords_override=encounter)
        return len(encounter)
            

    def transform(self, function, start_chord, all_chords=False):
        #read Left to Right
        chord_map = [start_chord]
        last = 0
        for key in self.function_unravel(function.upper())[::-1]:
            if key == "[":
                chord_map = chord_map[:-last] + [chord_map[-1]]
            elif key == "]":
                last = 0
            else:
                last += 1
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

    def make_music(self, function, base_chord, chords_override=None):
        if not chords_override:
            name = base_chord.chord_name() + "-" +str(function)
            chords =self.transform(function, base_chord, all_chords=True)
        else:
            name = base_chord.chord_name() + "-subgroup-" + (function)
            chords = chords_override
        chords_list = [res.to_notes() for res in chords]
        Player.make_wav_from_notes(chords_list, "music/" + name)

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
        self.p, self.l, self.r = None, None, None
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

    def find_function(self, chord_to, encountered=[], funct_str="", max_length=10):
        """Given a chord, find a set of functions that links the two notes."""
        plr = PLR(12)
        functions = {"P": plr.P,"L": plr.L,"R": plr.R}
        function_strs = []
        if self in encountered or len(funct_str) > max_length:
            return [""]
        new_encountered = list(encountered) + [self]
        if self == chord_to:
            return [funct_str]
        for name in functions:
            new_chord = functions[name](self)
            function_strs.extend(new_chord.find_function(chord_to,
                                                         new_encountered, funct_str=name+funct_str))
        return sorted([f_str for f_str in function_strs if f_str], key=len)


    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"

    def __eq__(self, other):
        return (self.x == other.x and self.y == other.y and self.z == other.z)

    def add_to(tup, add, mod=12):
        return tuple((((x + add) % mod) for x in tup))


#this is the PLR function object, you define the mod here
PLR_test = PLR(12)
#this is a sample chord
'''
chord_test = Chord(0, 4, 7)
#Just showing how functions are written
print(PLR_test.function_unravel("PLR(PL)4PPPL(LR)2L"))
print(PLR_test.L(chord_test))
#you can transform a chord with a function string
results = PLR_test.transform("P[LR](PL)4PPP", chord_test, all_chords=True)
notes = []
for result in results:
    print(result.to_notes())
    notes += result.to_notes()
'''
C = Chord(0, 4, 7)
Gm = Chord(2, 10, 7)
Bb = Chord(10, 2, 5)

print(PLR_test.order(C, "[PLR]"))
functs_to_Gm = C.find_function(Gm)
functs_to_Bb = C.find_function(Bb)

for funct in functs_to_Gm:
    print(funct + ", " + str(len(funct)))
'''
print("-" * 80)
for funct in functs_to_Bb:
    print(funct + ", " + str(len(funct)))

#Player.make_wav_from_notes(notes, "test_construction")
PLR_test.make_music("[LP](LR)9", Chord(0,8,5))'''



#Producing subgroups
C = Chord(0, 4, 7)
'''
#Order 2
PLR_test.order(C, ["L"])
PLR_test.order(C, ["(LR)6"])
for n in range(12):
    PLR_test.order(C, ["(LR)" + str(n) + "L"])

#Order 4
PLR_test.order(C, ["(LR)3"])
for n in range(6):
    PLR_test.order(C, ["(LR)6", "(LR)" + str(n) + "L"])

#Order 6

PLR_test.order(C, ["(LR)2"])
for n in range(4):
    PLR_test.order(C, ["(LR)4", "(LR)" + str(n) + "L"])


#Order 8
for n in range(3):
    PLR_test.order(C, ["(LR)3", "(LR)" + str(n) + "L"])

#Order 12

PLR_test.order(C, ["LR"])
PLR_test.order(C, ["(LR)2", "L"])
PLR_test.order(C, ["(LR)2", "(LR)L"])


#Order 3
PLR_test.order(C, ["(LR)4"])

#Order 24
PLR_test.order(C, ["LR", "L"])
'''
