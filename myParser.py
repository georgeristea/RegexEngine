from regex import *
from regular_expression import *
import sys

class MyParser:

	def parse(self, string_input):

		stack = [];
		alternate_list = [];
		min_val = max_val = '';
		isrange = 0;
		range_list = [];
		l = [];
		wasDash = False;
		for c in string_input:
			if isrange == 2:
				if c == ']':
					set_items = set();
					for x in range_list:
						set_items.add(x);
					stack.append(RegEx(SYMBOL_SET, set_items));
					isrange = 0;
				else:
					if c == '-':
						wasDash = True;
					else:
						if wasDash == True:
							start = range_list.pop();
							range_list.append((start, c));
							wasDash = False;
						else:
							range_list.append(c);
			elif isrange == 1:
				if c  == '}':
					ok = 0;
					for x in range_list:
						if x != ',':
							if ok == 0:
								min_val += x;
							else:
								max_val += x;
						else:
							ok = 1;
					
					e = stack.pop();
					if ok == 0:
						#nu am virgula
						stack.append(RegEx(RANGE, e, (int(min_val), int(min_val))));
					elif min_val == '':
						stack.append(RegEx(RANGE, e, (-1, int(max_val))));
					elif max_val == '':
						stack.append(RegEx(RANGE, e, (int(min_val), -1)));
					else:
						stack.append(RegEx(RANGE, e, (int(min_val), int(max_val))));
					isrange = 0;

				else:
					range_list.append(c);
			elif c.isalpha() or c.isdigit():
				stack.append(RegEx(SYMBOL_SIMPLE, c));
			elif c == ')':
				while True:
					e1 = stack.pop();
					e2 = stack.pop();
					if e2 == '(':
						if len(l) == 0:
							#print("INTRU");
							stack.append(e1);
						else:
							# inseamna ca am elemente in lista pt alternare
							l.append(e1);
							while len(l) != 1:
								first = l.pop();
								second = l.pop();
								l.append(RegEx(ALTERNATION, first, second));
							stack.append(l.pop());
						break;

					elif e2 == '|':
						# adaug intr-o lista toate elementele intre care am "|"
						l.append(e1);
					else:
						stack.append(RegEx(CONCATENATION, e2, e1));

			elif c == '.':
				stack.append(RegEx(SYMBOL_ANY));
			elif c == '*':
				# scot ultimul RegEx din stiva si aplic * asupra lui
				# !!! o sa trebuiasca sa verific daca nu cumva ce scos este PARANTEZA
				# sau nu mai am ce sa scot (desi ni s-a spus ca nu inputul este valid intotdeauna)
				e = stack.pop();
				stack.append(RegEx(STAR, e));
			elif c == '?':
				e = stack.pop();
				stack.append(RegEx(MAYBE, e));
			elif c == '+':
				e = stack.pop();
				stack.append(RegEx(PLUS, e));
			elif c == '{':
				isrange = 1;
			elif c == '[':
				range_list = [];
				isrange = 2;
			else:
				stack.append(c);


		ok = 0;
		while len(stack) != 0 and ok != 1:
			e1 = stack.pop();
			if len(stack) != 0:
				# daca am mai mult de 1 element pe stiva
				# scot al doilea element si daca nu e "|" le concatenez
				e2 = stack.pop();
				if e2 != '|':
					stack.append(RegEx(CONCATENATION, e2, e1));
				else:
					alternate_list.append(e1);
			else:
				alternate_list.append(e1);
				ok = 1;

		while len(alternate_list) != 1:
			e1 = alternate_list.pop();
			e2 = alternate_list.pop();
			alternate_list.append(RegEx(ALTERNATION, e1, e2));

		return alternate_list.pop();

	def convert_to_re(self, regex):

		if regex.type == EMPTY_STRING:
			return RegularExpression(EMPTY_STRING_RE);
		elif regex.type == SYMBOL_SIMPLE:
			return RegularExpression(SYMBOL_RE, regex.symbol);
		elif regex.type == SYMBOL_ANY:
			# inseamna ca am sau intre toate simbolurile din alfabet
			reg_expr = RegularExpression(ALTERNATION_RE, 
								RegularExpression(SYMBOL_RE, '0'),
								RegularExpression(SYMBOL_RE, '1'));

			for x in CHARSET:
				if x.isdigit() and int(x) != 0 and int(x) != 1:
					reg_expr = RegularExpression(ALTERNATION_RE, reg_expr, 
										RegularExpression(SYMBOL_RE, x));
				elif x.isalpha():
					reg_expr = RegularExpression(ALTERNATION_RE, reg_expr, 
										RegularExpression(SYMBOL_RE, x));					

			return reg_expr;
		elif regex.type == SYMBOL_SET:
			re_list = [];
			for x in regex.symbol_set:
				if isinstance(x, tuple):
					if x[0].isdigit():
						for digit in range(int(x[0]), int(x[1]) + 1):
							re_list.append(RegularExpression(SYMBOL_RE, str(digit)));
					else:
						if ord(x[1]) > ord(x[0]):
							for char in range(ord(x[0]), ord(x[1]) + 1):
								re_list.append(RegularExpression(SYMBOL_RE, chr(char)));
						else:
							# daca am ceva de forma [b-D]  
							# prima data pun toate literele mici [b,c,d,....,z]
							# apoi literele mari pana la D
							for char in range(ord(x[0]), 123):
								#print(chr(char));
								re_list.append(RegularExpression(SYMBOL_RE, chr(char)));
							for char in range(65, ord(x[1]) + 1):
								re_list.append(RegularExpression(SYMBOL_RE, chr(char)));
				else:
					# inseamna ca e un singur caracter
					re_list.append(RegularExpression(SYMBOL_RE, x));

			reg_expr = None;
			while len(re_list) != 1:
				e1 = re_list.pop();
				e2 = re_list.pop();
				re_list.append(RegularExpression(ALTERNATION_RE, e1, e2));

			reg_expr = re_list.pop();
			return reg_expr;
		elif regex.type == RANGE:
			expressions = [];
			reg_expr = None;
			left_expr = self.convert_to_re(regex.lhs); # a
			r = regex.range;
			if r[0] != -1 and r[1] != -1:	# {3, 5}
				for i in range(r[0], r[1] + 1):
					reg_expr = left_expr;
					for times in range(0, i - 1):
						reg_expr = RegularExpression(CONCATENATION_RE, reg_expr, left_expr);
					expressions.append(reg_expr);
			elif r[0] == -1:
				expressions.append(RegularExpression(EMPTY_STRING_RE));
				for i in range(1, r[1] + 1):
					reg_expr = left_expr;
					for times in range(0, i - 1):
						reg_expr = RegularExpression(CONCATENATION_RE, reg_expr, left_expr);
					expressions.append(reg_expr);
			elif r[1] == -1:
				reg_expr = left_expr;
				for i in range(1, r[0]):
					reg_expr = RegularExpression(CONCATENATION_RE, reg_expr, left_expr);
				reg_expr_star = RegularExpression(STAR_RE, left_expr);

				expressions.append(RegularExpression(CONCATENATION_RE, reg_expr, reg_expr_star));

			while len(expressions) != 1:
				e1 = expressions.pop();
				e2 = expressions.pop();
				expressions.append(RegularExpression(ALTERNATION_RE, e1, e2));
			return expressions.pop();

		elif regex.type == MAYBE:
			left_expr = self.convert_to_re(regex.lhs);
			return RegularExpression(ALTERNATION_RE, RegularExpression(EMPTY_STRING_RE), left_expr);
		elif regex.type == STAR:
			left_expr = self.convert_to_re(regex.lhs);
			return RegularExpression(STAR_RE, left_expr);
		elif regex.type == PLUS:
			left_expr = self.convert_to_re(regex.lhs);
			right_expr = RegularExpression(STAR_RE, left_expr);
			return RegularExpression(CONCATENATION_RE, left_expr, right_expr);
		elif regex.type == CONCATENATION:
			left_expr = self.convert_to_re(regex.lhs);
			right_expr = self.convert_to_re(regex.rhs);
			return RegularExpression(CONCATENATION_RE, left_expr, right_expr);
		else:
			left_expr = self.convert_to_re(regex.lhs);
			right_expr = self.convert_to_re(regex.rhs);
			return RegularExpression(ALTERNATION_RE, left_expr, right_expr);			
