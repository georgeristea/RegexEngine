# try:
#     from graphviz import Digraph
# except ImportError:
#     pass
import string
CHARSET = string.digits + string.ascii_letters

from regular_expression import *
from nfa import *
from dfa import *
import sys
import pickle


class Test:

	def re_to_nfa(self, re):
	    """Convert a Regular Expression to a Nondeterminstic Finite Automaton"""
	    alphabet = CHARSET + "";
	    if re.is_simple_type():
	      if re.type == SYMBOL_RE:
	        # pt un sg. simbol
	        return NFA(alphabet, {0, 1}, 0, {1}, {(0, re.symbol) : frozenset({1})});
	      elif re.type == EMPTY_STRING_RE:
	        # pt. epsilon
	        return NFA(alphabet, {0, 1}, 0, {1}, {(0, "") : frozenset({1})});
	      else:
	        # pt. multimea vida
        	return NFA(alphabet, {0}, 0, set(), {});
	    else:
	      if re.type == CONCATENATION_RE:
	        nfa_left = self.re_to_nfa(re.lhs);
	        nfa_right = self.re_to_nfa(re.rhs);
	        self.rename_states(nfa_right, nfa_left);
	        # construiesc alfabetul
	        # adaug toate starile in automatul final
	        states = nfa_left.states.union(nfa_right.states);

	        for key in nfa_left.delta: 
	          if key in nfa_right.delta: 
	            nfa_left.delta[key] = nfa_left.delta[key].union(nfa_right.delta[key]);
	        nfa_left.delta.update(nfa_right.delta);
	        
	        # trebuie sa am tranzitie pe "epsilon" din fosta stare
	        # finala in starea initiala a celui de-al doilea automat
	        key = (nfa_left.final_states.pop(), "");
	        value = set({nfa_right.start_state});

	        if key in nfa_left.delta:
	          nfa_left.delta[key] = nfa_left.delta[key].union(value);
	        else:
	          nfa_left.delta.update({key: value});
	          # returnez noul automat
	        return NFA(alphabet, states, nfa_left.start_state, nfa_right.final_states, nfa_left.delta);
	        
	      elif re.type == ALTERNATION_RE:
	        # adaug o stare initiala si una finala
	        # si tranzitii din starea initiala pe "epsilon" catre urm. stare
	        # si din ultima stare pe "epsilon" catre starea finala adaugata
	        nfa_left = self.re_to_nfa(re.lhs);
	        nfa_right = self.re_to_nfa(re.rhs);
	        self.rename_states(nfa_right, nfa_left);
	        state_init, state_final = self.new_states(nfa_left, nfa_right);
	        states = nfa_left.states.union(nfa_right.states).union({state_init, state_final});
	        
	        for key in nfa_left.delta: 
	          if key in nfa_right.delta: 
	            nfa_left.delta[key] = nfa_left.delta[key].union(nfa_right.delta[key]); 
	        nfa_left.delta.update(nfa_right.delta);
	        
	        key = (nfa_left.final_states.pop(), "");
	        value = frozenset({state_final});
	        if key in nfa_left.delta:
	          nfa_left.delta[key] = nfa_left.delta[key].union(value);
	        else:
	          nfa_left.delta.update({key: value});

	        key = (nfa_right.final_states.pop(), "");
	        value = frozenset({state_final});
	        if key in nfa_left.delta:
	          nfa_left.delta[key] = nfa_left.delta[key].union(value);
	        else:
	          nfa_left.delta.update({key: value});
	        
	        nfa_left.delta.update({(state_init, ""): frozenset({nfa_left.start_state}).union( 
	                                                  frozenset({nfa_right.start_state}))});
	        # returnez noul automat format prin "reuniune"
	        return NFA(alphabet, states, state_init, {state_final}, nfa_left.delta);

	      else:
	        # inseamna ca am e*
	        # trebuie sa adaug doua tranzitii pe "epsilon":
	        # de la starea initiala la starea finala
	        # de la starea finala la starea initiala
	        nfa_left = self.re_to_nfa(re.lhs);
	        key = (next(iter(nfa_left.final_states)), "");
	        value = frozenset({nfa_left.start_state});
	        if key in nfa_left.delta:
	          nfa_left.delta[key] = nfa_left.delta[key].union(value);
	        else:
	          nfa_left.delta.update({key: value});

	        key = (nfa_left.start_state, "");
	        value = frozenset(nfa_left.final_states);
	        if key in nfa_left.delta:
	          nfa_left.delta[key] = nfa_left.delta[key].union(value);
	        else:
	          nfa_left.delta.update({key: value});

	        return nfa_left
	        
	def rename_states(self, target, reference):
	    off = max(reference.states) + 1;
	    target.start_state += off;
	    target.states = set(map(lambda s: s + off, target.states));
	    target.final_states = set(map(lambda s: s + off, target.final_states));
	    new_delta = {};
	    for (state, symbol), next_states in target.delta.items():
	        new_next_states = set(map(lambda s: s + off, next_states));
	        new_delta[(state + off, symbol)] = new_next_states;

	    target.delta = new_delta;


	def new_states(self, *nfas):
	    state = 0;
	    for nfa in nfas:
	        m = max(nfa.states);
	        if m >= state:
	            state = m + 1;

	    return state, state + 1;

	def convert_nfa_to_dfa(self, nfa):

		states_DFA = set();
		delta_DFA = {};
		start_state = self.epsilon_closure(nfa, set({nfa.start_state}));
		states_DFA.add(start_state);
		final_states_DFA = set();
		marked = {};
		# setez starea actuala din DFA ca si nevizitata deocamdata
		marked[start_state] = False;
		is_end = False;
		while is_end == False:
			is_end = True;
			for state in states_DFA.copy():
				if marked[state] == False:
					# inseamna ca mai am stari care nu au fost vizitate in DFA
					is_end = False;
					# pentru fiecare caracter din alfabet
					# trebuie sa construiesc tranzitia corespunzatare pentru DFA
					for char in nfa.alphabet:
						# pt. caracterul char trebuie sa vad unde pot 
						# ajunge in NFA
						states_NFA_from_char = self.get_state_on_char(nfa, state, char);
						next_state_DFA = self.epsilon_closure(nfa, states_NFA_from_char);
						if next_state_DFA not in states_DFA:
							states_DFA.add(next_state_DFA);
							marked[next_state_DFA] = False;

						delta_DFA[(state, char)] = next_state_DFA;

					# marchez starea ca si vizitata
					marked[state] = True;



		for state in states_DFA:
			for x in state:
				if x in nfa.final_states:
					final_states_DFA.add(state);
					break;

		return DFA(nfa.alphabet, states_DFA, start_state, final_states_DFA, delta_DFA);



	def get_state_on_char(self, nfa, state_DFA, char):

		result = set();
		for i in state_DFA:
			# pentru fiecare stare(nfa) din state_DFA
			# trebuie sa verific tranzitiile din delta'(nfa)
			for (state, symbol) in nfa.delta.keys():
				if state == i and symbol == char:
					result = result.union(nfa.delta[(state, symbol)]);

		return result;
	# functie care imi calculeaza epsilon_closure
	# pentru un set de stari dintr-un nfa
	def epsilon_closure(self, nfa, states):

		stack = [];
		# epsilon closure de starea '0' sigur contine starea '0'
		result = states;
		for state in states:
			stack.append(state);

		while len(stack) != 0:
			s = stack.pop();
			# daca exista in dictionar tranzitie pe epsilon din starea s
			if (s, '') in nfa.delta.keys():
				states_from_s = nfa.delta[(s, '')];
				for u in states_from_s.copy():
					if u not in result:
						# adaug toate starile care nu sunt deja in set-ul final
						result.add(u);
						stack.append(u);

		return frozenset(result);


	def start_DFA(self, dfa, word):

		state = dfa.start_state;
		for char in word:
			if char != '\n':
				state = dfa.delta[(state, char)];

		if state in dfa.final_states:
			return True;
		else:
			return False;

