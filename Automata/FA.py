import string
import graphviz
class FA():
    def __init__(self, states ,alphabet, transF, startState, acceptingStates):
        self.states = states
        self.alphabet = alphabet
        self.transF = transF
        self.startState = startState
        self.accpetingStates = acceptingStates

    #simulation function for both DFA AND NFA
    def simulate(self,chars):
        pass

    def move(self,state, char):
        return self.transF[state][char]
    
    # Clean the transition funciton of an Automata
    # Usefull when generating a FA from another structure (NFA or regex)
    def clean(self):
        alphabet = 1
        curr_keys = self.transF.keys()
        keys_to_letters = {}
        for key in curr_keys:
            letter = str(alphabet)
            alphabet +=1
            keys_to_letters[key] = letter 
        newTransF = {}
        for key in curr_keys:
            newTransF[keys_to_letters[key]] = {}
            for char in self.transF[key].keys():
                newTransF[keys_to_letters[key]][char] = keys_to_letters[self.transF[key][char]]
        self.transF = newTransF
        newStates = set()
        for state in self.states:
            newStates.add(keys_to_letters[state])
        self.states = newStates
        newAcceptingStates = set()
        for state in self.accpetingStates:
            newAcceptingStates.add(keys_to_letters[state])
        self.accpetingStates = newAcceptingStates
        self.startState = keys_to_letters[self.startState]

    def show(self):
        print("States:")
        print(self.states)
        print("Alphabet:")
        print(self.alphabet)
        print("Transition Funtion:")
        print(self.transF)
        print("Start State:")
        print(self.startState)
        print("Accpeting States:")
        print(self.accpetingStates)       
    
    def render(self, path):
        graph = graphviz.Digraph('Render of Finite Automata', format= "png")
        for state in self.states:
            if state == self.startState:
                graph.node(str(state), color = "red")
            if state in self.accpetingStates:
                graph.node(str(state), shape = 'doublecircle')
            else:
                graph.node(str(state))
        for node in self.transF.keys():
            for char in self.transF[node].keys():
                goesTo = self.transF[node][char]
                for item in goesTo:
                    graph.edge(str(node), str(item), label=char)
        graph.render(path)

"""
Transition function V1
{
    state:{
        char: states
        char: states
        .
        .
        .
    }
    state:{
        char: states
        char: states
        .
        .
        .
    }
    .
    .
    .
}
"""