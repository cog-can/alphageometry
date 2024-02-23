import unittest
from absl.testing import absltest
import dd
import ddar
import graph as gh
import problem as pr
from pprint import pprint
import logging
import pretty as pt
from graph_parse import get_all_rels

def natural_language_statement(logical_statement: pr.Dependency) -> str:
  """Convert logical_statement to natural language.

  Args:
    logical_statement: pr.Dependency with .name and .args

  Returns:
    a string of (pseudo) natural language of the predicate for human reader.
  """
  names = [a.name.upper() for a in logical_statement.args]
  names = [(n[0] + '_' + n[1:]) if len(n) > 1 else n for n in names]
  return pt.pretty_nl(logical_statement.name, names)


def proof_step_string(
    proof_step: pr.Dependency, refs: dict[tuple[str, ...], int], last_step: bool
) -> str:
  """Translate proof to natural language.

  Args:
    proof_step: pr.Dependency with .name and .args
    refs: dict(hash: int) to keep track of derived predicates
    last_step: boolean to keep track whether this is the last step.

  Returns:
    a string of (pseudo) natural language of the proof step for human reader.
  """
  premises, [conclusion] = proof_step

  premises_nl = ' & '.join(
      [
          natural_language_statement(p) + ' [{:02}]'.format(refs[p.hashed()])
          for p in premises
      ]
  )

  if not premises:
    premises_nl = 'similarly'

  refs[conclusion.hashed()] = len(refs)

  conclusion_nl = natural_language_statement(conclusion)
  if not last_step:
    conclusion_nl += ' [{:02}]'.format(refs[conclusion.hashed()])

  return f'{premises_nl} \u21d2 {conclusion_nl}'


def write_solution(g: gh.Graph, p: pr.Problem, out_file: str) -> None:
  """Output the solution to out_file.

  Args:
    g: gh.Graph object, containing the proof state.
    p: pr.Problem object, containing the theorem.
    out_file: file to write to, empty string to skip writing to file.
  """
  setup, aux, proof_steps, refs = ddar.get_proof_steps(
      g, p.goal, merge_trivials=False
  )

  solution = '\n=========================='
  solution += '\n * From theorem premises:\n'
  premises_nl = []
  for premises, [points] in setup:
    solution += ' '.join([p.name.upper() for p in points]) + ' '
    if not premises:
      continue
    premises_nl += [
        natural_language_statement(p) + ' [{:02}]'.format(refs[p.hashed()])
        for p in premises
    ]
  solution += ': Points\n' + '\n'.join(premises_nl)

  solution += '\n\n * Auxiliary Constructions:\n'
  aux_premises_nl = []
  for premises, [points] in aux:
    solution += ' '.join([p.name.upper() for p in points]) + ' '
    aux_premises_nl += [
        natural_language_statement(p) + ' [{:02}]'.format(refs[p.hashed()])
        for p in premises
    ]
  solution += ': Points\n' + '\n'.join(aux_premises_nl)

  # some special case where the deduction rule has a well known name.
  r2name = {
      'r32': '(SSS)',
      'r33': '(SAS)',
      'r34': '(Similar Triangles)',
      'r35': '(Similar Triangles)',
      'r36': '(ASA)',
      'r37': '(ASA)',
      'r38': '(Similar Triangles)',
      'r39': '(Similar Triangles)',
      'r40': '(Congruent Triangles)',
      'a00': '(Distance chase)',
      'a01': '(Ratio chase)',
      'a02': '(Angle chase)',
  }

  solution += '\n\n * Proof steps:\n'
  for i, step in enumerate(proof_steps):
    _, [con] = step
    nl = proof_step_string(step, refs, last_step=i == len(proof_steps) - 1)
    rule_name = r2name.get(con.rule_name, '')
    nl = nl.replace('\u21d2', f'{rule_name}\u21d2 ')
    solution += '{:03}. '.format(i + 1) + nl + '\n'

  solution += '==========================\n'
  logging.info(solution)
  if out_file:
    with open(out_file, 'w') as f:
      f.write(solution)
    logging.info('Solution written to %s.', out_file)

def flatten_txt(txt):
      return txt.replace('\n', '').replace('      ', ' ')[1:-1]

# txt = 'f g h i j = pentagon f g h i j; a = intersection_ll a f j g h; b = intersection_ll b f g h i; c = intersection_ll c g h i j; d = intersection_ll d h i f j; e = intersection_ll e f g i j; o1 = circle o1 a f g; o2 = circle o2 b g h; o3 = circle o3 c h i; o4 = circle o4 d j i; o5 = circle o5 e j f; k = intersection_cc k o5 o1 f; l = intersection_cc l o1 o2 g; m = intersection_cc m o2 o3 h; n = intersection_cc n o3 o4 i; o = intersection_cc o o4 o5 j; ox = circle k l m ? cyclic k l m n'
# txt = 'a f g = triangle a f g; c = on_line a f; d = on_line d a g; e = on_line e c f; b = on_pline b d f g ? simtri a f g a c d'
# txt = 'a f g = triangle a f g; d = on_line a g; b = on_pline b d f g; c = on_line b d, on_line a f ? simtri a f g a c d'
# txt = 'a f g = triangle a f g; d = on_line a g; b = on_pline b d f g; c = intersection_ll c b d a f ? simtri a f g a c d'
# txt = 'a f g = triangle a f g; d = on_line a g; b = on_pline b d f g; c = intersection_ll c b d a f; e = intersection_ll e b g a f ? simtri a f g a c d'
# txt = 'a c = segment a c; d = segment c d, segment a d; b = segment b c, on_line c d; e = segment c e, segment b e, on_line a c; g = segment d g, segment e g, on_line b e, on_line a d; f = segment e f, segment e g, on_line c e, on_pline b d f g ? simtri a f g a c d'
# txt = 'x y a b c d = e5128 x y a b c d ? perp a b b c'
# txt = 'a = free a; c = free c; d = free d; b = on_line c d; e = on_line a c; g = on_line b e, on_line a d; f = on_line c e, on_pline f g b d ? simtri a f g a c d'
# txt = 'a = free a; b = free b; d = free d; c = on_line a d, on_tline c b b a ? y'
txt = 'a = free a; b = free b; c = on_tline c b b a; d = on_tline d b c a, on_line a c ? simtri d a b d b c'
txt = 'a b c d = isquare a b c d; o = on_line a c, on_line b d; e = on_line c d; m = on_line a e, on_line b c; i = on_line o m, on_line b e ? aconst o i i b 1pi/4'
# txt = 'A = free A; C = free C; F = on_line F C A; D = on_dia D C A; B = on_tline B F A C; E = on_line E A F, on_tline E D A C ? para B F E D'
# txt = 'A = free A; C = free C; F = on_line F C A; B = on_dia B C A, on_tline B F A C; D = on_dia D C A; E = on_line E A F, on_tline E D A C ? para B F E D'
# txt = 'A = free A; C = free C; F = on_line F C A; B = on_dia B C A, on_tline B F A C; D = on_dia D C A; E = on_line E A F, on_tline E D A C ? eqangle A F A D D E D C'
# txt = 'F = free F; A = free A; E = free E; C = on_line C A F; H = on_line H A E; B = on_line B A E; D = on_pline D F B C, on_line D F E ? simtri A F E A C B'
# txt = 'E = free E; F = free F; D = on_line D F E; A = free A; C = on_line C A F; H = on_line H A E; B = on_line B A E, on_pline B C D F ? simtri A F E A C B'


print(txt)
defs = pr.Definition.from_txt_file('defs.txt', to_dict=True)
for dname, d in defs.items():
    print('=' * 10)
    print('Name::: ', dname)
    d: pr.Definition
    construction : pr.Construction = d.construction
    rely : dict[str, str] = d.rely
    deps : pr.Clause = d.deps
    basics : list[tuple[str, pr.Construction]] = d.basics
    numerics : pr.Construction = d.numerics
    basics_txt = ''
    for basic_tuple in basics:
        names_list, cons_list = basic_tuple
        cons_names = [cons.txt() for cons in cons_list]
        basics_txt += f'{names_list} = {cons_names}; '
    # print('Construction::: ', construction.txt())
    # print('Rely:::', rely)
    # print('Deps::: ', deps.txt())
    # print('Basics::: ', basics_txt)
    # print('Numerics::: ', list(map(pr.Construction.txt, numerics)))

p = pr.Problem.from_txt(txt,translate=False)
g, _ = gh.Graph.build_problem(p, defs)
# algebraic = g.derive_algebra(1, True)
gh.nm.draw(
      g.type2nodes[gh.Point],
      g.type2nodes[gh.Line],
      g.type2nodes[gh.Circle],
      g.type2nodes[gh.Segment],
      save_to='drawer_tests/test.png')

rules = pr.Theorem.from_txt_file('rules.txt', to_dict=True)
# ddar.solve(g, rules, p, max_level=1000)
ddar.solve_all(g, rules, p, max_level=1000)
write_solution(g, p, "drawer_tests/test.txt")
goal_args = g.names2nodes(p.goal.args)
# print(g.check(p.goal.name, goal_args))
print("-" * 10)
get_all_rels(g)
