import graph as gh
from dd import match_all


def get_all_rels(g: gh.Graph):
    rels = ['coll', 'para', 'perp', 'cong', 'eqangle', 'eqangle6', 'eqratio', 'eqratio6', 'cyclic', 'midp', 'circle']
    all_rels_dict = dict.fromkeys(rels, [])
    name2point = g._name2point
    point2name = {v: k for k, v in name2point.items()}
    for rel in rels:
        curr_generator = match_all(name = rel, g=g)
        for match in curr_generator:
            # print(rel, [point2name[p] for p in match])
            all_rels_dict[rel].append([point2name[p] for p in match])


    return all_rels_dict