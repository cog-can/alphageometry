from itertools import cycle, islice
import random
import logging

from primitives import primitives, primitives_setup
from write_solution import write_solution, get_proof_dict
import problem as pr
import graph as gh
import ddar

logging.basicConfig(level=logging.INFO)

class CycleWithCounter:
	def __init__(self, iterable):
		self.cycle = cycle(iterable)
		self.counters = {}
		self.peeked_element = None

	def peek_next(self):
		"""
		Peek at the next element without advancing the iterator.
		"""
		if self.peeked_element is None:
			self.peeked_element = next(self.cycle)
		return self.peeked_element

	def advance_iterator(self):
		"""
		Manually advance the iterator.
		"""
		if self.peeked_element is not None:
			next_element = self.peeked_element
			self.peeked_element = None
			self.counters[next_element] = self.counters.get(next_element, 0) + 1
			return next_element
		else:
			self.peek_next()
			return self.advance_iterator()

	def __iter__(self):
		return self

	def __next__(self):
		return self.advance_iterator()

constrained2arity = {
	'perp': 4, 'para': 4, 'cong': 4, 'coll': 3, 'eqangle': 6, 'cyclic': 5 
}

unique_arg_constrained = ['para', 'coll'] # These constrained predicates must produce arity - 1 unique points as args

constrained2weights = {
	'perp': 0.2, 'para': 0.12, 'cong': 0.2, 'coll': 0.24, 'eqangle': 0.12, 'cyclic': 0.12
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

def insert_args_into_format(format_string, args):
    arg_mapping = {f'a{i+1}': arg for i, arg in enumerate(args)}
    formatted_string = format_string.format(**arg_mapping)
    
    return formatted_string

def build_defined_primitive(cyc, sampled_points):
	primitive = random.choice(list(primitives_setup.keys()))

	arity = primitives_setup[primitive]['arity']
	args = list(islice(cyc, arity))
	sampled_points.extend(args)

	return insert_args_into_format(primitives_setup[primitive]['format'], args), arity

def build_primitive(name, arity, cyc, sampled_points):
	args = list(islice(cyc, arity))
	sampled_points.extend(args)
	return f"{' '.join(args)} = {name} {' '.join(args)}; "

def delete_aux_and_deps(txt, to_delete: list[str]):
	print(f"Original {txt}")
	print(f"To Delete::: {to_delete}")
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
		if point in to_delete:
			continue
		pred_strs = []
		for pred in preds:
			name, args = pred
			if not set(to_delete).intersection(set(args)):
				pred_strs += [f"{name} {' '.join(args)}"]

		if pred_strs:
			result += f"{point} = " + ', '.join(pred_strs) + '; '
		else:
			result += f"{point} = free {point}; "

	print(f"after delete::: {result[:-2]}")
	return result[:-2]

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

def generate_random_aux(point_names : CycleWithCounter, sampled_points, num_deps):
	predicate_names = random.choices(
		list(constrained2weights.keys()),
		list(constrained2weights.values()),
		k=num_deps
	)
	predicates = []
	point = point_names.peek_next()
	for predicate_name in predicate_names:
		aux_str = build_aux(
			predicate_name,
			constrained2arity[predicate_name],
			point,
			sampled_points
		)
		
		if aux_str:
			predicates.append(aux_str)

	if predicates:
		return point, f"{point} = {', '.join(predicates)}; "
	else:
		return None, None
	
def generate_random_problem(defs : pr.Definition) -> str:
	point_names = CycleWithCounter([
		'A','B','C','D','E','F','G','H','J','K','L','M',  
		'N','O','P','Q','R','S','T','U','V','W','Y','Z'
	])

	construction_str = ''
	sampled_points = []

	num_aux = random.randint(1, 6)
	tmp, primitive_arity = build_defined_primitive(point_names, sampled_points)
	construction_str += tmp
	print(f"Defined primitive::: {construction_str}")

	while num_aux > 0:
		num_deps = random.randint(1, 2)
		point, random_construction = generate_random_aux(point_names, sampled_points, num_deps)
		if not random_construction:
			continue
		# Try to build problem
		try:
			tmp = construction_str + random_construction
			print("Trying to build::: ", tmp[:-2])
			p = pr.Problem.from_txt(tmp[:-2], translate=False)
			_, _ = gh.Graph.build_problem(p, defs, max_tries=10)
		except:
			print("Failed to build graph")
			continue

		construction_str = tmp
		num_aux -= 1
		point_names.advance_iterator()
		sampled_points.append(point)

	return construction_str[:-2], primitive_arity

def try_random_problem():
	defs = pr.Definition.from_txt_file('defs.txt', to_dict=True)
	rules = pr.Theorem.from_txt_file('rules.txt', to_dict=True)
	check = False
	num_tries = 0
	while not check:
		try:
			txt, primitive_arity = generate_random_problem(defs)
			print(f'Primitive {txt}')
			p = pr.Problem.from_txt(txt, translate=False)
			g, _ = gh.Graph.build_problem(p, defs)
			g, level_times, status, branches, all_added, last_dd_added = ddar.solve_all(
				g,
				rules,
				p,
				max_level=20,
				timeout=10
			)

		except:
			continue
		
		if not last_dd_added:
			continue

		goal_argnames = []
		for arg in last_dd_added.args:
			goal_argnames.append(arg.name)
			
		goal = pr.Construction.from_txt(f"{last_dd_added.name} {' '.join(goal_argnames)}")
		# setup, aux, proof_steps, refs = ddar.get_proof_steps(
		# 	g, goal, merge_trivials=False
		# )

		proof_dict = get_proof_dict(
			g, goal, get_setup=True
		)

		setup = proof_dict['setup']
		aux = proof_dict['aux']
		point_names = []
		for premises, [points] in (setup + aux):
			point_names.extend([p.name for p in points])

		all_points = [p.name for p in g.all_points()]
		
		pred_1, rest = txt.split('; ', 1)
		_, *pred_1_args = pred_1.split(' ')

		print(f"All points in g {all_points}")
		print(f"Setup aux points {point_names}")

		to_delete = (set(all_points) - set(point_names + pred_1_args))
		# simple_txt = pred_1 + '; ' + delete_aux_and_deps(rest, to_delete)
		simple_txt = delete_aux_and_deps(txt, to_delete)

		num_tries += 1
		# print(f"Num Refs::: {len(refs)} Point Names::: {point_names}::{len(point_names)} Setup Len::: {len(setup)}")
		# print(f"Discriminator {(len(refs) - len(setup)) / len(point_names)}")
		# print(f"Len refs - len Setup :::{(len(refs) - len(setup))}")


		# if (len(refs) - len(setup)) / len(point_names) > 1.0 and len(refs) - len(setup) > 4:
		# 	check = True

		proof_len = len(proof_dict['solution_steps'])
		point_len = len(point_names)

		print(f"Discriminator {proof_len - point_len + primitive_arity}")
		print(f"NumPoints ::: {point_len}")
		print(f"ProofLen ::: {proof_len}")

		if proof_len + primitive_arity - point_len > 3 and proof_len > 3:
			check = True
		if num_tries > 20:
			check = True 

	## Run DDAR with the simple txt
	goal = f"{last_dd_added.name} {' '.join(goal_argnames)}"
	p = pr.Problem.from_txt(simple_txt, translate=False)
	g, _ = gh.Graph.build_problem(p, defs)
	g, level_times, status, branches, all_added, last_dd_added = ddar.solve_all(
		g,
		rules,
		p,
		max_level=20,
		timeout=10
	)
	solution_str = write_solution(g, pr.Construction.from_txt(goal), None)
	proof_dict = get_proof_dict(g, pr.Construction.from_txt(goal))

	return (
		len(level_times),
		simple_txt,
		f"{last_dd_added.name} {' '.join(goal_argnames)}", # goal
		txt,
		solution_str,
		proof_dict
	)


if __name__ == '__main__':
	level, simple_txt, goal, txt, solution, proof_dict = try_random_problem()
	# for _ in range(1000):
	# 	level, simple_txt, goal, txt, solution = try_random_problem()
	# 	print(f'+++++++++ SIMPLE TXT +++++++++\n{simple_txt}')

	# 	if level >= 5 and level < 8:
	# 		with open('candidates_5.tsv', 'a') as file:
	# 			file.write(f"{str(level)}\t" + 
	# 					f"{goal}\t" + 
	# 					f"{simple_txt}\t" +
	# 					f"{txt}\n"
	# 			)
	# 	if level >= 8:
	# 		with open('candidates_8.tsv', 'a') as file:
	# 			file.write(f"{str(level)}\t" + 
	# 					f"{goal}\t" + 
	# 					f"{simple_txt}\t" +
	# 					f"{txt}\n"
	# 			)