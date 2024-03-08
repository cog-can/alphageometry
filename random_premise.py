from itertools import cycle, islice
from typing import Tuple
import random
import logging
from pprint import pprint

import problem as pr
import graph as gh
import ddar

logging.basicConfig(level=logging.INFO)

class CycleWithCounter:
	def __init__(self, iterable):
		self.cycle = cycle(iterable)
		self.counters = {}

	def __next__(self):
		next_element = next(self.cycle)
		self.counters[next_element] = self.counters.get(next_element, 0) + 1
		if self.counters[next_element] == 1:
			return next_element
		else:
			return f"{next_element}{self.counters[next_element]}"
	
	def __iter__(self):
		return self

constrained2arity = {
	'perp': 4, 'para': 4, 'cong': 4, 'coll': 3, 'eqangle': 6, 'cyclic': 5 
}

unique_arg_constrained = ['para', 'coll'] # These constrained predicates must produce arity - 1 unique points as args

constrained2weights = {
	'perp': 0.2, 'para': 0.12, 'cong': 0.2, 'coll': 0.24, 'eqangle': 0.12, 'cyclic': 0.12
}

primitives2arity = {
	'triangle': 3, 'isquare': 4, 'segment': 2
}

primitives2weights = {
	'triangle': 0.5, 'isquare': 0.2, 'segment': 0.3
}

def unique_choices(population, weights=None, k=1):
    if k > len(population):
        raise ValueError("Cannot select more unique elements than available in the population")
    
    result = []
    while len(result) < k:
        element = random.choices(population, weights, k=1)[0]
        if element not in result:
            result.append(element)
    
    return result

def translate_constrained_to_constructive(
		point: str, name: str, args: list[str]
) -> tuple[str, list[str]]:
	"""Translate a predicate from constraint-based to construction-based.

	Args:
		point: str: name of the new point
		name: str: name of the predicate, e.g., perp, para, etc.
		args: list[str]: list of predicate args.

	Returns:
		(name, args): translated to constructive predicate.
	"""
	if name in ['T', 'perp']:
		a, b, c, d = args
		if point in [c, d]:
			a, b, c, d = c, d, a, b
		if point == b:
			a, b = b, a
		if point == d:
			c, d = d, c
		if a == c and a == point:
			return 'on_dia', [a, b, d]
		return 'on_tline', [a, b, c, d]

	elif name in ['P', 'para']:
		a, b, c, d = args
		if point in [c, d]:
			a, b, c, d = c, d, a, b
		if point == b:
			a, b = b, a
		return 'on_pline', [a, b, c, d]

	elif name in ['D', 'cong']:
		a, b, c, d = args
		if point in [c, d]:
			a, b, c, d = c, d, a, b
		if point == b:
			a, b = b, a
		if point == d:
			c, d = d, c
		if a == c and a == point:
			return 'on_bline', [a, b, d]
		if b in [c, d]:
			if b == d:
				c, d = d, c  # pylint: disable=unused-variable
			return 'on_circle', [a, b, d]
		return 'eqdistance', [a, b, c, d]

	elif name in ['C', 'coll']:
		a, b, c = args
		if point == b:
			a, b = b, a
		if point == c:
			a, b, c = c, a, b
		return 'on_line', [a, b, c]

	elif name in ['^', 'eqangle']:
		a, b, c, d, e, f = args

		if point in [d, e, f]:
			a, b, c, d, e, f = d, e, f, a, b, c

		x, b, y, c, d = b, c, e, d, f
		if point == b:
			a, b, c, d = b, a, d, c

		if point == d and x == y:  # x p x b = x c x p
			return 'angle_bisector', [point, b, x, c]

		if point == x:
			return 'eqangle3', [x, a, b, y, c, d]

		return 'on_aline', [a, x, b, c, y, d]

	elif name in ['cyclic', 'O']:
		print([x for x in args if x != point])
		a, b, c = [x for x in args if x != point]
		return 'on_circum', [point, a, b, c]

	return name, args

def build_primitive(name, arity, cyc, sampled_points):
		args = list(islice(cyc, arity))
		sampled_points.extend(args)
		return f"{' '.join(args)} = {name} {' '.join(args)}; "

def delete_aux_and_deps(txt, to_delete):
	print(f"Original {txt}")
	auxs = txt.split('; ')
	constructions = dict()
	for aux in auxs[1:]:
		point, *preds = aux.split(' = ')
		preds = [pred.split(', ') for pred in preds][0]
		for pred in preds:
			name, *args = pred.split(' ')
			constructions.setdefault(point, []).append((name, args))
	
	# reassamble
	result = auxs[0] + '; '
	for point, preds in constructions.items():
		if point == to_delete:
			continue
		pred_strs = []
		for pred in preds:
			name, args = pred
			if to_delete not in args:
				pred_strs += [f"{name} {' '.join(args)}"]

		if pred_strs:
			result += f"{point} = " + ', '.join(pred_strs) + '; '

	print(result[:-2])

def build_aux(name, arity, point_from: cycle | str, sampled_points) -> str:
	'''
		Build a randomly sampled auxilary construction
		args:
			name (str): constrained predicate name
			arity (int): num of args
			point_from (cycle | str): point name str or iterable to get point name from
			sampled_points (list[str]): points this predicate may depend on
		returns:
			str: random constructive predicate
	'''
	if name == 'cyclic': # Cant generate cyclic yet TODO
		return None

	if isinstance(point_from, str):
		point = point_from
	else:
		point = next(point_from)
		
	try:	
		if name in unique_arg_constrained:
			if arity > len(sampled_points) + 1:
				return None
			dep_args = unique_choices(sampled_points, k=arity - 1)
		else:
			dep_args = (
				unique_choices(sampled_points, k = arity // 2 - 1) +
				unique_choices(sampled_points, k = arity // 2)
			)
	except ValueError:
		return None
		
	constructive_name, constructive_args = translate_constrained_to_constructive(
		point, name, [point] + dep_args
	)
	return f"{constructive_name} {' '.join(constructive_args)}"

def generate_random_aux(point_names, sampled_points):
	num_deps = random.randint(1,2)
	predicate_names = random.choices(
		list(constrained2weights.keys()),
		list(constrained2weights.values()),
		k=num_deps
	)
	predicates = []
	point = next(point_names)
	for predicate_name in predicate_names:
		aux_str = build_aux(
			predicate_name,
			constrained2arity[predicate_name],
			point,
			sampled_points
		)
		# print('aux_str::: ', aux_str)
		
		if aux_str:
			predicates.append(aux_str)

	sampled_points.append(point)
	if predicates:
		return f"{point} = {', '.join(predicates)}; "
	else:
		return None
	
def generate_random_problem(defs : pr.Definition) -> str:
	point_names = CycleWithCounter([
		'A','B','C','D','E','F','G','H','J','K','L','M',  
		'N','O','P','Q','R','S','T','U','V','W','Y','Z'
	])
	construction_str = ''
	sampled_points = []
	primitive = random.choices(
		list(primitives2weights.keys()),
		list(primitives2weights.values())
	)[0]

	num_aux = random.randint(4, 20)
	num_aux = 12
	construction_str += build_primitive(
		primitive, primitives2arity[primitive], point_names, sampled_points
	)

	for _ in range(num_aux):
		random_construction = generate_random_aux(point_names, sampled_points)
		if not random_construction:
			continue
		# Try to build problem
		try:
			tmp = construction_str + random_construction
			p = pr.Problem.from_txt(tmp[:-2], translate=False)
			_, _ = gh.Graph.build_problem(p, defs, max_tries=10)
		except:
			print("Failed to build graph")
			continue
		construction_str = tmp

	return construction_str[:-2]


if __name__ == '__main__':
	delete_aux_and_deps('A B C D = isquare A B C D; E = eqdistance E D C B, on_line E D A; M = on_aline M B E C B A', 'E')

	defs = pr.Definition.from_txt_file('defs.txt', to_dict=True)
	rules = pr.Theorem.from_txt_file('rules.txt', to_dict=True)
	for _ in range(1000):
		try:
			txt = generate_random_problem(defs)
			print(txt)
			p = pr.Problem.from_txt(txt, translate=False)
			g, _ = gh.Graph.build_problem(p, defs)
			g, level_times, status, branches, all_added = ddar.solve_all(
				g,
				rules,
				p,
				max_level=20,
				timeout=10
			)
		except Exception as e:
			print(e)
			continue

		if len(level_times) >= 5 and len(level_times) < 8:
			with open('candidates_5.txt', 'a') as file:
				file.write('\n' + txt)
		if len(level_times) >= 8:
			with open('candidates_8.txt', 'a') as file:
				file.write('\n' + txt)

