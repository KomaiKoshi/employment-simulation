import random
import numpy as np

# Rouletteクラス
class Roulette:
    #注意:  Value に 0 値を持つものがない前提。
    #       0値処理はこのクラス外の責任

    def __init__(self, src):
        # PARAM: src is dict as {key_1: val_1,...}
        #        the class make a roulette for keys depened on val_n
        #        If a val_n of key_n is big, then the probabirity of the key_n is big.
        self.src = src

        # constructed roulette
        self.roulette = {}

        # construction of roulette
        self.construct()


    # Construction of roulette based on souce data
    def construct(self):
        self.roulette.clear()
        t = sum(self.src.values())

        prev = 0.0
        for k, v in self.src.items():
            self.roulette[k] = (v + prev) / t
            prev += v


    # Delete key in roulette.
    def delete(self, key):
        del self.src[key]
        self.construct()


    # Throw a dice and return the key for the dice.
    def dice(self):
        dice = np.random.uniform(0,1)
        for k, v in self.roulette.items():
            if (dice <= v):
                return k
        
        #ERROR
        return None

    # to be strings
    def to_s(self):
        s = []
        for k, v in self.roulette.items() :
            s.append(str(k) + "," + str(v) + "\n")
        return "< Roulette \n" + ", ".join(s) + " >"
