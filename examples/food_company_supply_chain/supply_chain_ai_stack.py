# supply_chain_ai_stack.py  –  v1
# ======================================================================
# End-to-end Supply-Chain AI mesh, built on Agno
#
# • Control-Tower Director (coordinate)
# • 7 route-mode managers (Demand, Production, Logistics, Procurement,
#   Sustainability, Risk, QA/Governance)
# • 5 coordinate teams (Demand-Forecast, Production-Plan, Green-Logistics,
#   Procurement-Ops, Risk-Sentinel) + Scenario-Simulator + Onboarding (ops)
# • 2 collaborate sentinels (Cost-Sentinel, Exception-Resolver)
# • Long-term vector + event memory
# • FastAPI stub for /api/forecast (optional)
# ======================================================================

import os, pathlib, logging, asyncio
from typing import List, Optional

from fastapi import FastAPI, APIRouter
from pydantic import BaseModel

from agno.agent import Agent, RunResponse
from agno.team import Team
from agno.memory import VectorFileMemory, FileMemory
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools as RT

# ---------- TOOL STUBS (replace with real SDK wrappers) ---------------
from agno.tools.slack import SlackTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.pandas import PandasTools
from agno.tools.ortools import ORTools  # If Agno ships OR-Tools wrapper, OR-Tools is an open source software suite for optimization, tuned for tackling the world's toughest problems in vehicle routing, flows, integer and linear programming, and constraint programming.
from agno.tools.yfinance import YFinanceTools
from agno.tools.email import EmailTools
from agno.tools.file import FileTools
from agno.tools.shell import ShellTools
from agno.tools.python import PythonTools

# ⇣ create thin “CustomAPITools” if you haven’t written them yet
from types import SimpleNamespace as _S


class CustomAPITools(_S):
    pass


GoogleMapsTools = CustomAPITools
OpenChargeMapTools = CustomAPITools
PetrolAPITools = CustomAPITools
AzureIoTTools = CustomAPITools
SAPTools = CustomAPITools

# ----------------------------------------------------------------------
OPENAI = os.getenv("OPENAI_API_KEY", "sk-…")
logging.basicConfig(level=logging.INFO)

MEM_BASE = pathlib.Path("./mem")
MEM_BASE.mkdir(exist_ok=True, parents=True)
vector_mem = VectorFileMemory(path=str(MEM_BASE / "vector"))
event_mem = FileMemory(path=str(MEM_BASE / "events"))


# ------------------------ worker factory ------------------------------
def w(name, role, tools: Optional[List] = None, instr: Optional[List[str]] = None):
    return Agent(
        name=name,
        role=role,
        model=OpenAIChat("gpt-4o-mini", api_key=OPENAI),
        tools=(tools or []) + [RT()],
        instructions=instr or [],
        memory=vector_mem,
        session_memory=event_mem,
        markdown=True,
        show_tool_calls=False,
    )


# ========= DEMAND-FORECAST TEAM  ======================================
stat_fc = w("Stat-Forecaster", "ARIMAX/Prophet", [PandasTools()])
promo_lift = w("Promo-Lift Analyst", "Promo elasticity", [PandasTools()])
social = w(
    "Social-Demand Sensor",
    "TikTok/X spikes",
    [DuckDuckGoTools(), GoogleSearchTools()],
    ["Write demand_uplift event when >10k mentions"],
)
sop_sync = w("Demand-S&OP Synth", "Reconcile demand/capacity")

demand_team = Team(
    "Demand-Forecast Team",
    "coordinate",
    OpenAIChat("gpt-4o-mini", api_key=OPENAI),
    members=[stat_fc, promo_lift, social, sop_sync],
    memory=event_mem,
    instructions=["Generate 18-mo unconstrained forecast"],
)

demand_mgr = Team(
    "Demand-Mgr",
    "route",
    OpenAIChat("gpt-4o", api_key=OPENAI),
    [demand_team],
    memory=event_mem,
    instructions=["'forecast' → team; 'promo' → Promo-Lift …"],
    tools=[SlackTools()],
    markdown=True,
)

# ========= PRODUCTION TEAM ============================================
mat_avail = w("Material-Availability", "Check RM, PM in SAP", [SAPTools()])
capacity = w("Capacity-Solver", "Finite-cap MIP", [ORTools()])
shift_seq = w("Shift-Sequencer", "Line/shift pattern", [ORTools()])
inv_doc = w("Inventory-Health Doctor", "Dead/slow stock", [PandasTools()])
talent = w("Talent-Scheduler", "Labour roster", [SAPTools(), SlackTools()])

prod_team = Team(
    "Production-Plan Team",
    "coordinate",
    OpenAIChat("gpt-4o-mini", api_key=OPENAI),
    [mat_avail, capacity, shift_seq, inv_doc, talent],
    memory=event_mem,
    instructions=["Create feasible weekly prod plan"],
)

prod_mgr = Team(
    "Production-Mgr",
    "route",
    OpenAIChat("gpt-4o", api_key=OPENAI),
    [prod_team],
    tools=[SlackTools()],
    memory=event_mem,
    instructions=["route by keywords"],
    markdown=True,
)

# ========= GREEN-LOGISTICS TEAM =======================================
eco_route = w(
    "Eco-Route Optimizer",
    "Least-CO₂ path",
    [GoogleMapsTools(route_matrix=True), ORTools()],
)
traffic = w(
    "Traffic-Intel",
    "Live delay/CO₂",
    [GoogleMapsTools(traffic=True), DuckDuckGoTools()],
)
roadworks = w("Construction-Monitor", "Roadworks horizon", [GoogleSearchTools()])
fuel_trk = w("Fuel-Price Tracker", "Daily fuel €/L", [PetrolAPITools()])
charge_pl = w(
    "Charge-Planner",
    "EV charge stops",
    [OpenChargeMapTools(), GoogleMapsTools(ev=True)],
)
reverse = w("Reverse-Logistics Agent", "Pickup & back-haul", [ORTools()])

log_team = Team(
    "Green-Logistics Team",
    "coordinate",
    OpenAIChat("gpt-4o-mini", api_key=OPENAI),
    [eco_route, traffic, roadworks, fuel_trk, charge_pl, reverse],
    memory=event_mem,
    instructions=["Optimise daily transport plan; CO₂ & cost KPI"],
)

log_mgr = Team(
    "Logistics-Mgr",
    "route",
    OpenAIChat("gpt-4o", api_key=OPENAI),
    [log_team],
    tools=[SlackTools()],
    memory=event_mem,
    instructions=["route logistics requests"],
    markdown=True,
)

# ========= PROCUREMENT TEAM ===========================================
should_cost = w("Should-Cost", "Cost curve ML", [PandasTools()])
sup_score = w("Supplier-Scorecard", "Risk/ESG", [YFinanceTools()])
rfx = w("RFx Autobidder", "Auto-bid scripts", [SlackTools()])
div_tracker = w("Supplier-Diversity Tracker", "D&I metrics", [GoogleSearchTools()])

proc_team = Team(
    "Procurement-Ops",
    "coordinate",
    OpenAIChat("gpt-4o-mini", api_key=OPENAI),
    [should_cost, sup_score, rfx, div_tracker],
    memory=event_mem,
    instructions=["End-to-end sourcing pipeline"],
)

proc_mgr = Team(
    "Procurement-Mgr",
    "route",
    OpenAIChat("gpt-4o", api_key=OPENAI),
    [proc_team],
    tools=[SlackTools()],
    memory=event_mem,
    instructions=["route sourcing tasks"],
    markdown=True,
)

# ========= SUSTAINABILITY TEAM ========================================
regen = w("Regen-Agri Monitor", "Farmer KPI", [GoogleSearchTools()])
scope3 = w("Scope3 Calculator", "GHG", [PandasTools()])
pack = w("Packaging-Optimizer", "Mono mat swap", [DuckDuckGoTools()])

sus_team = Team(
    "Sustainability Team",
    "coordinate",
    OpenAIChat("gpt-4o-mini", api_key=OPENAI),
    [regen, scope3, pack],
    memory=event_mem,
    instructions=["Generate monthly CSR dataset"],
)

sus_mgr = Team(
    "Sustainability-Mgr",
    "route",
    OpenAIChat("gpt-4o", api_key=OPENAI),
    [sus_team],
    tools=[SlackTools()],
    memory=event_mem,
    instructions=["route sustainability queries"],
    markdown=True,
)

# ========= RISK-SENTINEL TEAM ==========================================
clim = w("Climate-Alert", "Flood/drought", [GoogleSearchTools()])
geo = w("Geo-Political Alert", "Sanctions", [GoogleSearchTools()])
cyber = w("Cyber-Supply Alert", "Cyber risk", [DuckDuckGoTools()])
iot = w("IoT Anomaly Sentinel", "Cold-chain", [AzureIoTTools()])

risk_team = Team(
    "Risk-Sentinel",
    "coordinate",
    OpenAIChat("gpt-4o-mini", api_key=OPENAI),
    [clim, geo, cyber, iot],
    memory=event_mem,
    instructions=["Broadcast high-risk events"],
)

risk_mgr = Team(
    "Risk-Mgr",
    "route",
    OpenAIChat("gpt-4o", api_key=OPENAI),
    [risk_team],
    tools=[SlackTools()],
    memory=event_mem,
    instructions=["forward risk alerts"],
    markdown=True,
)

# ========= QA / GOVERNANCE ============================================
qa_reviewer = w("Compliance-Reviewer", "Check docs & tone")
qa_mgr = Team(
    "QA-Mgr",
    "route",
    OpenAIChat("gpt-4o", api_key=OPENAI),
    [qa_reviewer],
    tools=[SlackTools()],
    memory=event_mem,
    instructions=["review outputs"],
    markdown=True,
)

# ========= FINANCE MODULE =============================================
lane_cost = w("Lane-Cost Forecaster", "€/ton-km model", [PandasTools()])
carbon_oracle = w("Carbon-Cost Oracle", "EUA pricing")
fin_mgr = Team(
    "Finance-Mgr",
    "route",
    OpenAIChat("gpt-4o", api_key=OPENAI),
    [lane_cost, carbon_oracle],
    tools=[SlackTools()],
    memory=event_mem,
    instructions=["Route finance queries"],
    markdown=True,
)

# ========= SCENARIO SIMULATOR TEAM =====================================
whatif_gen = w("Scenario-Generator", "Create shocks")
whatif_run = w("Scenario-Runner", "Digital twin VRP", [ORTools()])
whatif_rep = w("Scenario-Reporter", "Write PPTX", [FileTools()])

scenario_team = Team(
    "Scenario-Simulator",
    "coordinate",
    OpenAIChat("gpt-4o-mini", api_key=OPENAI),
    [whatif_gen, whatif_run, whatif_rep],
    memory=event_mem,
    instructions=["Run what-ifs; post to #supply-board"],
)

# ========= SENTINELS ===================================================
cost_sent = w("Cost-Sentinel", "Token & CO₂ spend", [PandasTools()])
ex_resolv = w(
    "Exception-Resolver",
    "Plan vs actual",
    [SlackTools()],
    instr=["Open war-room on exception"],
)

# ========= CONTROL-TOWER DIRECTOR =====================================
exec_dir = Team(
    "Control-Tower Director",
    "coordinate",
    OpenAIChat("gpt-4o", api_key=OPENAI),
    members=[
        demand_mgr,
        prod_mgr,
        log_mgr,
        proc_mgr,
        sus_mgr,
        risk_mgr,
        qa_mgr,
        fin_mgr,
        scenario_team,
        cost_sent,
        ex_resolv,
    ],
    tools=[SlackTools()],
    memory=vector_mem,
    instructions=[
        "Delegate requests to managers/teams.",
        "Listen for sentinel events and surface daily KPI deck.",
        "Post digest to #ctl_tower and echo to requester.",
    ],
    markdown=True,
)

# ========= FASTAPI (optional) ==========================================
app = FastAPI(title="Supply-Chain AI")
router = APIRouter(prefix="/api")


class ForecastRequest(BaseModel):
    market: str


@router.post("/forecast")
async def forecast(req: ForecastRequest):
    """Return 18-mo unconstrained forecast markdown."""
    res: RunResponse = await asyncio.to_thread(
        demand_team.run, f"Forecast demand for {req.market}", stream=False
    )
    return {"forecast_md": res.content}


app.include_router(router)

# ========= CLI DEMO ====================================================
if __name__ == "__main__":
    exec_dir.print_response(
        "Rhine water level drops 1m for two weeks. "
        "Run scenario, re-optimise logistics, and give CO2 + cost delta.",
        stream=True,
    )
