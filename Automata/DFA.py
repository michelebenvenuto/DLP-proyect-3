from Automata.FA import FA
from pythomata import SimpleDFA
import time
class DFA(FA):
    def simulate(self,chars):
        s = self.startState
        for i in range(len(chars)):
            c = ord(chars[i])
            if c not in self.alphabet:
                return False, False
            s = self.move(s,c)
        if s in self.accpetingStates:
            return True, s
        else:
            return False, s
    