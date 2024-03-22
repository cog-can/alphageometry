primitives = {
    'triangle': {
        'format': '{a1} {a2} {a3} = triangle {a1} {a2} {a3}; ',
        'arity': 3
    }
}

primitives_setup = {
    'k2_9': {
        'format': (
            '{a1} {a2} {a3} = triangle {a1} {a2} {a3}; ' +
            '{a4} = midpoint {a4} {a1} {a2}; ' +
            '{a6} = on_line {a6} {a3} {a4}; ' +
            '{a7} = on_line {a7} {a2} {a3}, on_pline {a7} {a6} {a1} {a2}; ' + 
            '{a5} = on_line {a5} {a1} {a2}, on_pline {a5} {a7} {a4} {a3}; '
        ),
        'arity': 7
    },
    'jgex_02_06_01_20_10': {
        'format': (
            '{a1} {a2} {a3} {a4} = quadrangle {a1} {a2} {a3} {a4}; ' + 
            '{a5} = on_line {a5} {a2} {a3}, on_line {a5} {a1} {a4}; ' +
            '{a6} = circle {a6} {a3} {a4} {a5}; '
        ),
        'arity': 6
    },
    'jgex_02_06_41_6_57': {
        'format':
            '{a1} {a2} {a3} = triangle {a1} {a2} {a3}; {a4} = foot {a4} {a1} {a2} {a3}; {a5} = midpoint {a5} {a1} {a4}; ',
        'arity': 5
    },
    'jgex_aux2_22': {
        'format': (
            '{a3} {a1} {a2} = iso_triangle {a3} {a1} {a2}; ' + 
            '{a4} = on_line {a4} {a1} {a3}; ' + 
            '{a5} = on_line {a5} {a2} {a3}, eqdistance {a5} {a2} {a1} {a4}; ' +
            '{a6} = on_line {a6} {a1} {a2}, on_line {a6} {a4} {a5}; '
        ),
        'arity': 6
    },
}
