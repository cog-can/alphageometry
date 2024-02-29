import graph as gh
from dd import match_all

predicate_arities = {
    'coll': (3, 1),
    'para': (2, 2),
    'perp': (2, 2),
    'cong': (2, 2),
    'eqangle': (4, 2),
    'eqangle6': (3, 2),
    'eqratio': (4, 2),
    'eqratio6': (3, 2),
    'cyclic': (3, 1),
    'midp': (3, 1),
    'circle': (3, 1)
}

def format_predicate(name, args):
    arity = predicate_arities[name]
    format_str = ''
    for i in range(arity[0]):
        format_str += ''.join(args[i * arity[1]: (i + 1) * arity[1]]) + ' '
    return format_str

def get_all_rels(g: gh.Graph):
    rels = ['coll', 'para', 'perp', 'cong', 'eqangle', 'eqangle6', 'eqratio', 'eqratio6', 'cyclic', 'midp', 'circle']
    all_rels_dict = dict.fromkeys(rels, [])
    name2point = g._name2point
    point2name = {v: k for k, v in name2point.items()}
    for rel in rels:
        all_rels_dict[rel] = []
        curr_generator = match_all(name = rel, g=g)
        for match in curr_generator:
            args = [point2name[p] for p in match]
            all_rels_dict[rel].append(format_predicate(rel, args))

    return all_rels_dict

def get_cache(g: gh.Graph):
    conclusions = g.cache.keys()
    conc_str = ""
    for conc in conclusions:
        conc_str += ' '.join(conc) + '\n'

    return conc_str
