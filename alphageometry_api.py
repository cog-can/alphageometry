from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import json
from pydantic import BaseModel

from PIL import Image

from write_solution import natural_language_statement, write_solution
from graph_parse import get_all_rels

import problem as pr
import graph as gh
import ddar

DEFS = pr.Definition.from_txt_file('defs.txt', to_dict=True)
RULES = pr.Theorem.from_txt_file('rules.txt', to_dict=True)

class ConstructionStr(BaseModel):
    txt: str

class WhyQuery(BaseModel):
    txt: str
    query: str

# Keep a simple cache of proof states for saturated problem defs
# TODO maybe redis here 
proof_cache = dict()

app = FastAPI(
    title       = "Alpha Geometry API",
    description = """
                    API for running alphageometry in different configurations.
                  """,
    version     = "v1",
)

origins = [
    "http://localhost",
    "http://localhost:8008",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def save_openapi_json():
    openapi_data = app.openapi()
    with open("openapi.json", "w") as file:
        json.dump(openapi_data, file)

@app.get("/", include_in_schema=False)
async def redirect():
    return RedirectResponse("/docs")

@app.get('/healthcheck', status_code=status.HTTP_200_OK)
def perform_healthcheck():
    return {'healthcheck': 'Everything OK!'}

@app.post('/run_ddar', status_code=status.HTTP_200_OK)
def run_ddar(construction_str: ConstructionStr) -> dict:
    txt = construction_str.txt
    p = pr.Problem.from_txt(txt,translate=False)
    if txt in proof_cache.keys():
        g = proof_cache[txt]
        solution = 'Bactracked From Cache\n==========================\n' 
    else:
        g, _ = gh.Graph.build_problem(p, DEFS)
        ddar.solve_all(g, RULES, p, max_level=1000) # Force saturation
        solution = ''
    # Cache the proof state
    if '?' in txt:
        premises = txt.split(' ? ')[0]
    else:
        premises = txt

    proof_cache[premises] = g
    rels_dict = get_all_rels(g)
    if p.goal:
        goal_args = g.names2nodes(p.goal.args)
        if g.check(p.goal.name, goal_args):
            solution += write_solution(g, p, "drawer_tests/test.txt")
            rels_dict["solution"] = solution
        else:
            rels_dict["solution"] = solution + "False"
    else:
        rels_dict["solution"] = solution + "No Goal"
    return rels_dict

@app.post("/plot")
def plot_figure(construction_str: ConstructionStr):
    txt = construction_str.txt
    p = pr.Problem.from_txt(txt,translate=False)
    g, _ = gh.Graph.build_problem(p, DEFS)

    buffer = gh.nm.draw(
      g.type2nodes[gh.Point],
      g.type2nodes[gh.Line],
      g.type2nodes[gh.Circle],
      g.type2nodes[gh.Segment],
      save_to='drawer_tests/test.png')
    
    buffer.seek(0)

    # Return the content of the BytesIO buffer as response
    return Response(content=buffer.getvalue(), media_type="image/png")

@app.post("/ask_why")
def ask_why(why: WhyQuery):
    txt = why.txt # Only premises
    query = why.query
    if txt in proof_cache.keys():
        g = proof_cache[txt]
        solution_str = (
            'Bactracked From Cache\n==========================\n' + 
            write_solution(g, pr.Construction.from_txt(query), out_file=None)
        )
    else:
        p = pr.Problem.from_txt(txt,translate=False)
        g, _ = gh.Graph.build_problem(p, DEFS)
        ddar.solve_all(g, RULES, p, max_level=1000) # Force saturation
        proof_cache[txt] = g
        solution_str = write_solution(g, pr.Construction.from_txt(query), out_file=None)
    return {'solution_str': solution_str}
