import unittest
from absl.testing import absltest
import dd
import ddar
import graph as gh
import problem as pr
from pprint import pprint
import logging
import pretty as pt
from graph_parse import get_all_rels, get_cache
from write_solution import write_solution
import trace_back

import logging
logging.basicConfig(level=logging.INFO)

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
# txt = 'a b c d = isquare a b c d; o = on_line a c, on_line b d; e = on_line c d; m = on_line a e, on_line b c; i = on_line o m, on_line b e ? aconst o i i b 1pi/4'
# txt = 'A = free A; C = free C; F = on_line F C A; D = on_dia D C A; B = on_tline B F A C; E = on_line E A F, on_tline E D A C ? para B F E D'
# txt = 'A = free A; C = free C; F = on_line F C A; B = on_dia B C A, on_tline B F A C; D = on_dia D C A; E = on_line E A F, on_tline E D A C ? para B F E D'
# txt = 'A = free A; C = free C; F = on_line F C A; B = on_dia B C A, on_tline B F A C; D = on_dia D C A; E = on_line E A F, on_tline E D A C ? eqangle A F A D D E D C'
# txt = 'F = free F; A = free A; E = free E; C = on_line C A F; H = on_line H A E; B = on_line B A E; D = on_pline D F B C, on_line D F E ? simtri A F E A C B'
# txt = 'E = free E; F = free F; D = on_line D F E; A = free A; C = on_line C A F; H = on_line H A E; B = on_line B A E, on_pline B C D F ? simtri A F E A C B'
# txt = 'a = free a; b = free b; c = on_tline c b b a; d = on_tline d b c a, on_line a c ? simtri d a b d b c'
txt = 'A B C D = isquare A B C D; E = on_aline E B A A B D; F = on_line F A B; H = on_pline H A E B, eqdistance H D C A; J = on_pline J A B H; L = on_circle L D C'

print(txt)
defs = pr.Definition.from_txt_file('defs.txt', to_dict=True)
p = pr.Problem.from_txt(txt,translate=False)
g, _ = gh.Graph.build_problem(p, defs)
gh.nm.draw(
      g.type2nodes[gh.Point],
      g.type2nodes[gh.Line],
      g.type2nodes[gh.Circle],
      g.type2nodes[gh.Segment],
      save_to='drawer_tests/test.png')

rules = pr.Theorem.from_txt_file('rules.txt', to_dict=True)
ddar.solve_all(g, rules, p, max_level=1000)
'eqangle B H D H D H B D'
goal = pr.Construction.from_txt('eqangle B H D H D H B D')
setup, aux, proof_steps, refs = ddar.get_proof_steps(
      g, goal, merge_trivials=False
)
print(f'setup {setup}')
print(f'aux {aux}')
print(f'proofsteps {proof_steps}')
print(f'refs {refs}')

print(f'points from setup')
point_names = []
for premises, [points] in setup:
      point_names.extend([p.name for p in points])
      print(points)

print(point_names)

# write_solution(g, p, "drawer_tests/test.txt")
# # goal_args = g.names2nodes(p.goal.args)
# print('Checking rconst', g.check('rconst', g.names2nodes("acab") + ['5/3']))
# print("-" * 10)
# get_all_rels(g)
# print(get_cache(g))
# rats = [rat._l for rat in g.type2nodes[gh.Ratio]]
# for rat in rats:
#     print(rat)
#     if rat[0]:
#         print([m.name for m in rat])
