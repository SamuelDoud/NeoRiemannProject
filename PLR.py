import re

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

    def __len__(self):
        return 0

class Chord(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def order(self):
        pass

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")"

    def __eq__(self, other):
        return (self.x == other.x and self.y == other.y and self.z == other.z)

#this is the PLR function object, you define the mod here
PLR_test = PLR(12)
#this is a sample chord
chord_test = Chord(0, 4, 7)
#Just showing how functions are written
print(PLR_test.function_unravel("PLR(PL)4PPPL(LR)2L"))
print(PLR_test.L(chord_test))
#you can transform a chord with a function string
results = PLR_test.transform("PLR(PL)4PPP", chord_test, all_chords=True)
for result in results:
    print(result)
