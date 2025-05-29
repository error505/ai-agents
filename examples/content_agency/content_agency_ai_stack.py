# content_agency_ai_stack.py  –  v1
# ======================================================================
# A complete agent mesh for a social-first content-creation agency.
# • Executive Director delegating to ten route-mode managers
# • Coordinate teams for Ideation, Production, Distribution, Community,
#   Analytics, Ads, QA, Finance
# • Collaborate sentinels for Brand-Tone and Token/Spend
# • Long-term vector + event memory
# ======================================================================

import os, pathlib, logging, asyncio
from typing import List, Optional

from agno.agent import Agent, RunResponse
from agno.team import Team
from agno.memory import VectorFileMemory, FileMemory
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools as RT

# comms / search
from agno.tools.slack import SlackTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.x import XTools
from agno.tools.youtube import YouTubeTools
from agno.tools.pandas import PandasTools
from agno.tools.file import FileTools
from agno.tools.python import PythonTools
from agno.tools.shell import ShellTools
from agno.tools.replicate import ReplicateTools
from agno.tools.gmail import GmailTools

OPENAI = os.getenv("OPENAI_API_KEY", "sk-…")
logging.basicConfig(level=logging.INFO)

MEM = pathlib.Path("./mem")
MEM.mkdir(exist_ok=True, parents=True)
vec_mem = VectorFileMemory(path=str(MEM / "vector"))
evt_mem = FileMemory(path=str(MEM / "events"))


def w(name, role, tools: Optional[List] = None, instr: Optional[List[str]] = None):
    return Agent(
        name=name,
        role=role,
        model=OpenAIChat("gpt-4o-mini", api_key=OPENAI),
        tools=(tools or []) + [RT()],
        instructions=instr or [],
        memory=vec_mem,
        session_memory=evt_mem,
        markdown=True,
        show_tool_calls=False,
    )


# ───── Ideation Team ───────────────────────────────────────────────
trend = w("Trend-Scout", "Scrape trends", [DuckDuckGoTools(), GoogleSearchTools()])
idea = w("Idea-Generator", "Topic hooks", [DuckDuckGoTools()])
seo = w("SEO-Keyword Analyst", "Keyword clusters", [PandasTools()])
calendar = w("Content-Calendar Planner", "30-day schedule", [PandasTools()])

ideation_team = Team(
    "Ideation-Team",
    "coordinate",
    OpenAIChat("gpt-4o-mini", api_key=OPENAI),
    [trend, idea, seo, calendar],
    memory=evt_mem,
    instructions=["Output 30-day idea board"],
)

ideation_mgr = Team(
    "Ideation-Mgr",
    "route",
    OpenAIChat("gpt-4o", api_key=OPENAI),
    [ideation_team],
    tools=[SlackTools()],
    memory=evt_mem,
    instructions=["'idea'/'calendar' → team"],
    markdown=True,
)

# ───── Production Team ─────────────────────────────────────────────
script = w("Script-Writer", "Long/short scripts")
blog = w("Blog-Writer", "SEO blogpost", [DuckDuckGoTools()])
video = w("Video-Editor", "Short-form edit", [ReplicateTools()])
thumb = w("Thumbnail-Designer", "Thumbnail", [ReplicateTools()])
graphic = w("Graphic-Designer", "Carousels", [ReplicateTools()])
multi_team = Team(
    "Production-Team",
    "coordinate",
    OpenAIChat("gpt-4o-mini", api_key=OPENAI),
    [script, blog, video, thumb, graphic],
    memory=evt_mem,
    instructions=["Create all media assets"],
)
prod_mgr = Team(
    "Content-Prod-Mgr",
    "route",
    OpenAIChat("gpt-4o", api_key=OPENAI),
    [multi_team],
    tools=[SlackTools()],
    memory=evt_mem,
    instructions=["route by asset type"],
    markdown=True,
)

# ───── Distribution Team ───────────────────────────────────────────
scheduler = w("Scheduler", "Post queue", [SlackTools()])
crosspost = w("Cross-Poster", "Repurpose", [XTools(), YouTubeTools()])
hashtag = w("Hashtag-Optimizer", "Hashtags", [PandasTools()])
dist_team = Team(
    "Distribution-Team",
    "coordinate",
    OpenAIChat("gpt-4o-mini", api_key=OPENAI),
    [scheduler, crosspost, hashtag],
    memory=evt_mem,
    instructions=["Schedule & post across channels"],
)
dist_mgr = Team(
    "Distribution-Mgr",
    "route",
    OpenAIChat("gpt-4o", api_key=OPENAI),
    [dist_team],
    tools=[SlackTools()],
    memory=evt_mem,
    instructions=["route distribution tasks"],
    markdown=True,
)

# ───── Community Team ──────────────────────────────────────────────
engage = w("Community-Responder", "Reply comments", [SlackTools()])
trend_alert = w("Micro-Trend Alert", "Daily microtrend", [DuckDuckGoTools()])
community_team = Team(
    "Community-Team",
    "coordinate",
    OpenAIChat("gpt-4o-mini", api_key=OPENAI),
    [engage, trend_alert],
    memory=evt_mem,
    instructions=["Manage replies, surface trends"],
)
comm_mgr = Team(
    "Community-Mgr",
    "route",
    OpenAIChat("gpt-4o", api_key=OPENAI),
    [community_team],
    tools=[SlackTools()],
    memory=evt_mem,
    instructions=["community tasks"],
    markdown=True,
)

# ───── Analytics Team ──────────────────────────────────────────────
perf = w("Performance-Analyst", "Engagement KPI", [PandasTools()])
ab = w("A/B Tester", "Variant test", [PandasTools()])
analytics_team = Team(
    "Analytics-Team",
    "coordinate",
    OpenAIChat("gpt-4o-mini", api_key=OPENAI),
    [perf, ab],
    memory=evt_mem,
    instructions=["Weekly performance pack"],
)
analytics_mgr = Team(
    "Analytics-Mgr",
    "route",
    OpenAIChat("gpt-4o", api_key=OPENAI),
    [analytics_team],
    tools=[SlackTools()],
    memory=evt_mem,
    instructions=["analytics tasks"],
    markdown=True,
)

# ───── Ads Team ────────────────────────────────────────────────────
copy = w("Ad-Copywriter", "Ad copy", [DuckDuckGoTools()])
segment = w("Audience-Segmenter", "Segment lookalike", [PandasTools()])
ads_team = Team(
    "Ads-Team",
    "coordinate",
    OpenAIChat("gpt-4o-mini", api_key=OPENAI),
    [copy, segment],
    memory=evt_mem,
    instructions=["Create and measure paid ads"],
)
ads_mgr = Team(
    "Ads-Mgr",
    "route",
    OpenAIChat("gpt-4o", api_key=OPENAI),
    [ads_team],
    tools=[SlackTools()],
    memory=evt_mem,
    instructions=["route ad tasks"],
    markdown=True,
)

# ───── QA / Brand Governance ───────────────────────────────────────
brand_tone = w("Brand-Tone Reviewer", "On-brand check")
qa_mgr = Team(
    "QA-Mgr",
    "route",
    OpenAIChat("gpt-4o", api_key=OPENAI),
    [brand_tone],
    tools=[SlackTools()],
    memory=evt_mem,
    instructions=["Review every asset before post"],
    markdown=True,
)

# ───── Finance / Cost Sentinel ─────────────────────────────────────
finance = w("Finance-Tracker", "Cost + ROI", [PandasTools()])
cost_sent = w("Token-Spend Sentinel", "OpenAI spend", [PandasTools()])
fin_mgr = Team(
    "Finance-Mgr",
    "route",
    OpenAIChat("gpt-4o", api_key=OPENAI),
    [finance, cost_sent],
    tools=[SlackTools()],
    memory=evt_mem,
    instructions=["Daily cost + ROI report"],
    markdown=True,
)

# ───── EXECUTIVE DIRECTOR ──────────────────────────────────────────
exec_dir = Team(
    "Exec-Director",
    "coordinate",
    OpenAIChat("gpt-4o", api_key=OPENAI),
    members=[
        ideation_mgr,
        prod_mgr,
        dist_mgr,
        comm_mgr,
        analytics_mgr,
        ads_mgr,
        qa_mgr,
        fin_mgr,
    ],
    tools=[SlackTools(), GmailTools()],
    memory=vec_mem,
    instructions=[
        "Delegate, wait for Slack summaries.",
        "Compose daily digest → #exec_updates & email.",
    ],
    markdown=True,
)

# ------------------ CLI DEMO --------------------------------------
if __name__ == "__main__":
    exec_dir.print_response(
        "I need next month’s content calendar for TikTok and LinkedIn, "
        "five hook ideas per week, and a video script for the best hook.",
        stream=True,
    )
