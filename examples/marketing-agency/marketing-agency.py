from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.tools import (
    # Comms
    SlackTools, GmailTools, TwilioTools, XTools, GoogleCalendarTools,
    # Search / scraping
    DuckDuckGoTools, YouTubeTools, WikipediaTools,
    # Data & local utils
    PandasTools, CsvTools, CalculatorTools,
    # Project / storage
    FileTools, GoogleSheetsTools, GoogleDriveTools, NotionTools,
    # General reasoning
    ReasoningTools
)

# ─────────────────────── 1)  WORKER AGENT FACTORIES ────────────────────── #
def worker(name, role, tools, extra_instr=None):
    return Agent(
        name=name,
        role=role,
        model=OpenAIChat("gpt-4o"),
        tools=tools + [ReasoningTools()],
        instructions=(extra_instr or []),
        markdown=True,
        show_tool_calls=True,
    )

# Content workers
content_workers = [
    worker("Content-Ideator", "Generate post ideas",
           [DuckDuckGoTools(), WikipediaTools()],
           ["Return list of 5 angles & hooks"]),

    worker("LinkedIn-Post-Writer", "Write LinkedIn posts",
           [XTools()], ["Tone: authoritative but friendly, 280-300 words"]),

    worker("YouTube→Blog", "Repurpose YT script to blog",
           [YouTubeTools()], ["Create 800-word SEO-ready article"]),

    worker("LinkedIn→Newsletter", "Turn LinkedIn post into newsletter",
           [], ["Embed a CTA in final paragraph"]),

    worker("YouTube→LinkedIn", "YT highlights into LinkedIn",
           [YouTubeTools()], ["Return 2200-char post + 3 hashtags"]),

    worker("LinkedIn→X", "Shorten LinkedIn post for X",
           [XTools()], ["Return 1–3 tweets under 280 chars each"]),
]

# Comms workers
comms_workers = [
    worker("Slack-Assistant", "Draft Slack replies", [SlackTools()]),
    worker("LinkedIn-DM-Assistant", "Draft LinkedIn DMs", [XTools()]),
    worker("WhatsApp-Assistant", "Write WhatsApp msgs", [TwilioTools()]),
    worker("Calendar-Assistant", "Schedule meetings", [GoogleCalendarTools()]),
    worker("Gmail-Assistant", "Draft emails", [GmailTools()]),
]

# Sales workers
sales_workers = [
    worker("Pre-Call-Assistant", "Prepare call brief",
           [DuckDuckGoTools()], ["Return bullets: company, pain points, hook"]),
    worker("Post-Call-Assistant", "Summarise call & next steps",
           [GmailTools()], ["Send recap email via GmailTools.send_email()"]),
    worker("Lead-Researcher", "Research leads",
           [DuckDuckGoTools(), WikipediaTools()]),
    worker("CRM-Assistant", "Update CRM CSV",
           [CsvTools(), PandasTools()]),
]

# Outbound workers
outbound_workers = [
    worker("Intent-Signal-Analyst", "Analyse buyer intent",
           [DuckDuckGoTools(), PandasTools()],
           ["Score leads 0-100"]),
    worker("Outbound-Copywriter", "Write cold email",
           [GmailTools()], ["Personalise first line"]),
]

# Research workers
research_workers = [
    worker("General-Researcher", "Long-form web research",
           [DuckDuckGoTools(), WikipediaTools()]),
    worker("Swipe-File-Analyst", "Tag swipe files",
           [FileTools()]),
    worker("Clay-Expert", "Enrich data via Clay API",
           [ReasoningTools()]),
    worker("GTM-Strategist", "Produce GTM brief",
           [PandasTools(), CalculatorTools()]),
]

# Marketing workers
marketing_workers = [
    worker("Ad-Designer", "Generate ad concept",
           [ReplicateTools()] if 'ReplicateTools' in globals() else []),
    worker("Social-Performance-Analyst", "Analyse social KPIs",
           [GoogleSheetsTools(), PandasTools()]),
    worker("Ad-Performance-Analyst", "Analyse ad spend & ROAS",
           [GoogleSheetsTools(), PandasTools(), CalculatorTools()]),
]

# Project workers
project_workers = [
    worker("Notion-Assistant", "Update Notion",
           [NotionTools()]),
    worker("GDrive-Assistant", "Handle Google Drive files",
           [GoogleDriveTools()]),
]

# ───────────────────── 2)  MANAGER AGENTS  (one per sub-team) ───────────── #
def manager(name, child_agents, inbound_channel):
    """Return a manager Agent that decides which child to invoke."""
    return Team(
        name=name,
        mode="route",            # manager chooses exactly one child
        model=OpenAIChat("gpt-4o"),
        members=child_agents,
        instructions=[
            f"You are the {name}. Decide which specialist handles the task.",
            "After the child agent responds, summarise outcome for Executive Director.",
            f"Use ReasoningTools internally; report via Slack channel #{inbound_channel}."
        ],
        markdown=True,
        show_members_responses=False,
    )

content_manager  = manager("Content-Manager",  content_workers, "content")
comms_manager    = manager("Comms-Manager",    comms_workers,   "comms")
sales_manager    = manager("Sales-Manager",    sales_workers,   "sales")
outbound_manager = manager("Outbound-Manager", outbound_workers,"outbound")
research_manager = manager("Research-Manager", research_workers,"research")
marketing_manager= manager("Marketing-Manager",marketing_workers,"marketing")
project_manager  = manager("Project-Manager",  project_workers, "projects")

# ───────────────────── 3)  EXECUTIVE DIRECTOR TEAM ─────────────────────── #
exec_director = Team(
    name="Executive-Director",
    mode="coordinate",                  # may call several managers
    model=OpenAIChat("gpt-4o"),
    members=[
        content_manager, comms_manager, sales_manager,
        outbound_manager, research_manager, marketing_manager,
        project_manager
    ],
    tools=[SlackTools(), TwilioTools()],
    instructions=[
        "You are the Executive Director. Receive tasks from the human.",
        "Delegate to the appropriate Manager(s).",
        "Collect summaries. Then:",
        " • Post a concise summary to Slack channel #executive_updates",
        " • Send a WhatsApp update via TwilioTools.send_whatsapp()",
        "Respond back to the human with the same summary."
    ],
    markdown=True,
    show_members_responses=False,
    add_datetime_to_instructions=True
)

# ───────────────────── 4)  RUN ─────────────────────────────────── #
if __name__ == "__main__":
    exec_director.print_response(
        "We need a LinkedIn post announcing our new AI consulting service, "
        "a matching cold email for top-3 leads, and a first draft of next "
        "week’s ad budget breakdown.",
        stream=True
    )
