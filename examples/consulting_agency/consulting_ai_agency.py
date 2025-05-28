# ======================================================================
# All-in-one AI-agent stack for a marketing / growth agency
#  • functional teams (Content, Comms, Sales, Marketing, Research, …)
#  • Developer PoC team, Lead-Gen pipeline, QA, SecOps, Experiments, Onboarding
#  • NEW: Documentation squad inside Project-Management
#  • Vector + File memory
#  • FastAPI endpoint /api/generate-leads
# ======================================================================

import os, json, logging, asyncio, pathlib
from typing import List, Optional

from fastapi import FastAPI, APIRouter
from pydantic import BaseModel

from agno.agent import Agent, RunResponse
from agno.team import Team
from agno.memory import FileMemory, VectorFileMemory
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools as RT

# toolkits --------------------------------------------------------------
from agno.tools.slack import SlackTools
from agno.tools.twilio import TwilioTools
from agno.tools.gmail import GmailTools
from agno.tools.googlecalendar import GoogleCalendarTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.google_maps import GoogleMapsTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.wikipedia import WikipediaTools
from agno.tools.yfinance import YFinanceTools
from agno.tools.pandas import PandasTools
from agno.tools.csv import CsvTools
from agno.tools.email import EmailTools
from agno.tools.replicate import ReplicateTools
from agno.tools.notion import NotionTools
from agno.tools.googledrive import GoogleDriveTools
from agno.tools.file import FileTools
from agno.tools.python import PythonTools
from agno.tools.shell import ShellTools

OPENAI = os.getenv("OPENAI_API_KEY", "sk-replace-me")
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("agency")

# ========== MEMORY =====================================================
MEM_DIR = pathlib.Path("./memory")
MEM_DIR.mkdir(parents=True, exist_ok=True)
brain_mem = VectorFileMemory(path=str(MEM_DIR / "vector"))
history_mem = FileMemory(path=str(MEM_DIR / "events"))


# ========== WORKER FACTORY =============================================
def worker(
    name: str,
    role: str,
    tools: Optional[List] = None,
    instr: Optional[List[str]] = None,
):
    return Agent(
        name=name,
        role=role,
        model=OpenAIChat("gpt-4o-mini", api_key=OPENAI),
        tools=(tools or []) + [RT()],
        instructions=instr or [],
        markdown=True,
        memory=brain_mem,
        session_memory=history_mem,
        show_tool_calls=True,
    )


# ========== FUNCTIONAL WORKERS =========================================
content_workers = [
    worker(
        "Content-Ideator",
        "Generate hooks",
        [DuckDuckGoTools(), WikipediaTools()],
        ["Return 5 angles & hooks JSON"],
    ),
    worker("LinkedIn-Post-Writer", "Write LinkedIn post"),
    worker("YouTube→Blog", "YT → blog"),
    worker("LinkedIn→Newsletter", "Post → newsletter"),
    worker("YouTube→LinkedIn", "YT highlights → LinkedIn"),
    worker("LinkedIn→X", "Shorten LinkedIn to X"),
]

comms_workers = [
    worker("Slack-Assistant", "Slack replies", [SlackTools()]),
    worker("LinkedIn-DM-Assistant", "LinkedIn DM"),
    worker("WhatsApp-Assistant", "WhatsApp", [TwilioTools()]),
    worker("Calendar-Assistant", "Calendar", [GoogleCalendarTools()]),
    worker("Gmail-Assistant", "Gmail drafts", [GmailTools()]),
]

marketing_workers = [
    worker("Ad-Designer", "Ad creative", [ReplicateTools()]),
    worker(
        "Social-Performance-Analyst", "Social KPIs", [GoogleDriveTools(), PandasTools()]
    ),
    worker("Ad-Performance-Analyst", "ROAS", [GoogleDriveTools(), PandasTools()]),
]

research_workers = [
    worker("General-Researcher", "Web research", [DuckDuckGoTools()]),
    worker("GTM-Strategist", "GTM brief", [PandasTools()]),
]

outbound_workers = [
    worker("Intent-Signal-Analyst", "Score intent", [DuckDuckGoTools(), PandasTools()]),
    worker("Outbound-Copywriter", "Cold email", [GmailTools()]),
]

# ========== DEVELOPER TEAM =============================================
frontend_dev = worker(
    "Frontend-Dev",
    "React/TS PoC",
    [FileTools(), ShellTools()],
    ["Scaffold Vite+TS; return file list"],
)
backend_dev = worker(
    "Backend-Dev",
    "FastAPI PoC",
    [PythonTools(), FileTools(), ShellTools()],
    ["Scaffold FastAPI; return file list"],
)
integrator = worker(
    "Fullstack-Integrator",
    "Wire stack",
    [FileTools(), ShellTools()],
    ["Add CORS/env; return deploy cmd"],
)

developer_manager = Team(
    "Developer-Manager",
    "route",
    OpenAIChat("gpt-4o", api_key=OPENAI),
    members=[frontend_dev, backend_dev, integrator],
    tools=[SlackTools()],
    memory=history_mem,
    instructions=[
        "Keywords React/UI → Frontend-Dev; FastAPI/backend → Backend-Dev; "
        "integrate/deploy → Fullstack-Integrator. Post #dev"
    ],
    markdown=True,
)


# ========== LEAD-GEN PIPELINE ===========================================
def la(name, role, instr, tools=None):
    return Agent(
        name=name,
        role=role,
        model=OpenAIChat("gpt-4o-mini", api_key=OPENAI),
        tools=(tools or []) + [RT()],
        instructions=instr,
        markdown=False,
        session_memory=history_mem,
    )


parser = la("Parser", "Extract params", ["Return JSON {role,location,count}"])
searcher = la(
    "Searcher", "Google LinkedIn", ["Build query & return list"], [GoogleSearchTools()]
)
extract = la("Extractor", "Result → lead", ["Return lead JSON first_name…"])
enrich = la("Enricher", "Firmographic", ["Add company_size,website,email"])
score = la("Scorer", "Score 0-100", ["Add score"])
emailer = la("Emailer", "Outreach email", ["Add outreach_email"])
sent = la(
    "Sentiment",
    "Company sentiment",
    ["Add sentiment_summary & sentiment_score"],
    [GoogleSearchTools(fixed_max_results=5), YFinanceTools(company_news=True)],
)
follow = la("FollowUp", "Follow-ups", ["Add followup_d3 & followup_d8"])
bounce = la("Bounce", "MX check", ["Add deliverable"], [EmailTools()])
geo = la("Geo", "Lat/Lng", ["Add latitude,longitude,map_url"], [GoogleMapsTools()])
summar = Agent(
    "Summariser",
    "Markdown table",
    OpenAIChat("gpt-4o-mini", api_key=OPENAI),
    tools=[PandasTools(), RT()],
    instructions=["Return markdown table sorted by score"],
    markdown=True,
)

leadgen_team = Team(
    "Lead-Gen Team",
    "coordinate",
    OpenAIChat("gpt-4o-mini", api_key=OPENAI),
    members=[
        parser,
        searcher,
        extract,
        enrich,
        score,
        emailer,
        sent,
        follow,
        bounce,
        geo,
        summar,
    ],
    memory=history_mem,
    instructions=["Full pipeline, save leads.json & md to ./outputs"],
    markdown=True,
)

# ========== SALES SPECIALISTS ==========================================
competitive = worker(
    "Competitive-Intel", "Battle card", [DuckDuckGoTools(), WikipediaTools()]
)
pricing = worker("Pricing-Strategist", "Price table", [PandasTools()])
packager = worker("Offer-Packager", "Good/Better/Best")
enablement = worker("Sales-Enablement", "Deck", [GoogleDriveTools(), FileTools()])
forecast = worker(
    "Pipeline-Forecaster", "Bookings forecast", [CsvTools(), PandasTools()]
)
pre_call = worker("Pre-Call-Assistant", "Discovery brief")
post_call = worker("Post-Call-Assistant", "Recap email")
lead_lookup = worker("Lead-Researcher", "Manual lookup")
crm_update = worker("CRM-Assistant", "Update CRM", [CsvTools()])

sales_manager = Team(
    "Sales-Manager",
    "route",
    OpenAIChat("gpt-4o", api_key=OPENAI),
    members=[
        leadgen_team,
        pre_call,
        post_call,
        lead_lookup,
        crm_update,
        competitive,
        pricing,
        packager,
        enablement,
        forecast,
    ],
    tools=[SlackTools()],
    memory=history_mem,
    instructions=[
        "lead/prospect → Lead-Gen; competitor → Competitive-Intel; "
        "price/margin/bundle → Pricing-Strategist; package → Offer-Packager; "
        "deck/demo → Sales-Enablement; forecast → Pipeline-Forecaster. "
        "Else Pre/Post/Lookup/CRM. Post #sales."
    ],
    markdown=True,
)

# ========== QA & OPS AGENTS ============================================
critique = worker(
    "Review-Critique",
    "Brand/style QA",
    instr=["Rewrite if off-brand; return final version"],
)
review_manager = Team(
    "Review-Manager",
    "route",
    OpenAIChat("gpt-4o", api_key=OPENAI),
    members=[critique],
    tools=[SlackTools()],
    memory=history_mem,
    instructions=["Run QA on assets; post #qa"],
    markdown=True,
)

exp_plan = worker("Experiment-Planner", "Define A/B", [PandasTools()])
exp_run = worker("Experiment-Runner", "Launch & monitor", [ShellTools()])
exp_rep = worker("Experiment-Reporter", "Summarise", [PandasTools()])

experiments_team = Team(
    "Experiments",
    "coordinate",
    OpenAIChat("gpt-4o-mini", api_key=OPENAI),
    members=[exp_plan, exp_run, exp_rep],
    tools=[SlackTools()],
    memory=history_mem,
    instructions=["Plan→Run→Report. Stop losers. Post #growth"],
    markdown=True,
)

chan_bot = worker("Slack-Channel-Bot", "Create Slack", [SlackTools()])
drive_bot = worker("Drive-Space-Bot", "Create Drive", [GoogleDriveTools()])
crm_bot = worker("CRM-Deal-Bot", "Init CRM", [CsvTools()])

onboarding_team = Team(
    "Onboarding-Team",
    "coordinate",
    OpenAIChat("gpt-4o-mini", api_key=OPENAI),
    members=[chan_bot, drive_bot, crm_bot],
    tools=[SlackTools()],
    memory=history_mem,
    instructions=["Spin Slack+Drive+CRM for new client; post #ops"],
    markdown=True,
)

seclint = worker(
    "SecOps-Linter",
    "Scan code",
    [PythonTools()],
    ["Scan for keys, PII, open CORS; output risk level"],
)
sec_manager = Team(
    "Security-Manager",
    "route",
    OpenAIChat("gpt-4o", api_key=OPENAI),
    members=[seclint],
    tools=[SlackTools()],
    memory=history_mem,
    instructions=["Run on every code artefact; post #security"],
    markdown=True,
)

cost_agent = worker(
    "Cost-Sentinel",
    "Aggregate spend",
    [PandasTools()],
    ["Collect mcp-tags {cost}, post daily chart #finops"],
)

# ========== DOCUMENTATION WORKERS (NEW) ================================
doc_architect = worker(
    "Doc-Architect",
    "Outline docs",
    instr=["Return JSON tree of sections: Intro, Install, API, Changelog, FAQ"],
)
api_doc_writer = worker(
    "API-Doc-Writer",
    "OpenAPI & snippets",
    tools=[PythonTools()],
    instr=["Generate Markdown API section with curl & Python examples"],
)
changelog_agent = worker(
    "Changelog-Agent",
    "Release notes",
    instr=["Format changelog in Markdown ## [x.y.z] – YYYY-MM-DD"],
)
tutorial_writer = worker(
    "Tutorial-Writer",
    "Step-by-step guides",
    instr=["Produce getting-started tutorial in Markdown"],
)

# ========== PROJECT MANAGER (updated) ===================================
project_workers = [
    worker("Notion-Assistant", "Update Notion", [NotionTools()]),
    worker("GDrive-Assistant", "Handle GDrive", [GoogleDriveTools()]),
    doc_architect,
    api_doc_writer,
    changelog_agent,
    tutorial_writer,
]

project_manager = Team(
    "Project-Manager",
    "route",
    OpenAIChat("gpt-4o", api_key=OPENAI),
    members=project_workers,
    tools=[SlackTools()],
    memory=history_mem,
    instructions=[
        "Route: outline/docs → Doc-Architect; API docs → API-Doc-Writer; "
        "changelog → Changelog-Agent; tutorial/how-to → Tutorial-Writer; "
        "else Notion/GDrive. Post #projects."
    ],
    markdown=True,
)


# ========== MANAGER FACTORY ============================================
def mk_mgr(name, crew, chan):
    return Team(
        name,
        "route",
        OpenAIChat("gpt-4o", api_key=OPENAI),
        members=crew,
        tools=[SlackTools()],
        memory=history_mem,
        instructions=[f"Route tasks, post summary to #{chan}"],
        markdown=True,
    )


content_manager = mk_mgr("Content-Manager", content_workers, "content")
comms_manager = mk_mgr("Comms-Manager", comms_workers, "comms")
marketing_manager = mk_mgr("Marketing-Manager", marketing_workers, "marketing")
research_manager = mk_mgr("Research-Manager", research_workers, "research")
outbound_manager = mk_mgr("Outbound-Manager", outbound_workers, "outbound")

# ========== EXECUTIVE DIRECTOR =========================================
exec_director = Team(
    "Executive-Director",
    "coordinate",
    OpenAIChat("gpt-4o", api_key=OPENAI),
    members=[
        content_manager,
        comms_manager,
        sales_manager,
        marketing_manager,
        outbound_manager,
        research_manager,
        project_manager,
        developer_manager,
        review_manager,
        experiments_team,
        onboarding_team,
        sec_manager,
        cost_agent,
    ],
    tools=[SlackTools(), TwilioTools()],
    memory=brain_mem,
    instructions=[
        "Delegate to managers, wait for Slack summaries.",
        "Run Cost-Sentinel daily 23:00 UTC.",
        "Compose digest → post #executive_updates and WhatsApp.",
        "Echo digest to requester.",
    ],
    markdown=True,
)

# ========== FASTAPI LEAD ENDPOINT ======================================
app = FastAPI(title="Agency AI Service")
router = APIRouter(prefix="/api")


class LeadRequest(BaseModel):
    message: str


@router.post("/generate-leads")
async def generate_leads(req: LeadRequest):
    res: RunResponse = await asyncio.to_thread(
        leadgen_team.run, req.message, stream=False
    )
    return {"leads_markdown": res.content}


app.include_router(router)

# ========== CLI DEMO ====================================================
if __name__ == "__main__":
    exec_director.print_response(
        "Onboard client BlueRail, outline documentation, "
        "generate API docs for the pricing calculator, "
        "build React PoC, and pull 5 CFO leads in Germany.",
        stream=True,
    )
