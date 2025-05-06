# ── pip install agno[azure,ortools] qdrant_client ──
from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.tools import (
    AzureIoTHubTools, TimeSeriesInsightsTools,
    AzureMLTools, SnowflakeTools, ORTools,
    AzureCommTools, MonitorWorkbookTools,
    ReasoningTools
)

# 1. Ingest Agent ────────────────────────
ingest = Agent(
    name="Ingest Agent",
    role="Load latest sensor batches and create embeddings",
    model=OpenAIChat(id="gpt-4o"),
    tools=[
        AzureIoTHubTools(receive=True),
        TimeSeriesInsightsTools(write=True),
        ReasoningTools(add_instructions=True)
    ],
    instructions=[
        "Listen for new CSV blobs from IoT Hub",
        "Clean nulls, unify timestamps",
        "Write to Time Series Insights",
        "Return JSON: {batch_id, rows_written}"
    ],
    markdown=True, show_tool_calls=True,
)

# 2. Predict‑Failure Agent ──────────────
predict = Agent(
    name="Predict‑Failure Agent",
    role="Forecast component failure risk 48 h ahead",
    model=OpenAIChat(id="gpt-4o"),
    tools=[
        AzureMLTools(deployments=["mtbf‑xgb"]),
        ReasoningTools(add_instructions=True)
    ],
    instructions=[
        "Fetch last 7 days telemetry from TSI",
        "Call Azure ML endpoint ‘mtbf‑xgb’",
        "Return JSON: [{asset_id, failure_prob, eta_hr}]"
    ],
    markdown=True, show_tool_calls=True,
)

# 3. Schedule‑Optimizer Agent ───────────
planner = Agent(
    name="Schedule‑Optimizer Agent",
    role="Minimise train delays while inserting maintenance windows",
    model=OpenAIChat(id="gpt-4o"),
    tools=[
        SnowflakeTools(select=True),
        ORTools(milp=True),
        ReasoningTools(add_instructions=True)
    ],
    instructions=[
        "Query Snowflake for train paths & slot availability",
        "Formulate MILP: minimise sum(delay_minutes)",
        "Hard‑constraint: failure_prob ≥ 0.7 ⇒ maintenance before ETA",
        "Return JSON: [{train_id, new_slot, exp_delay}]"
    ],
    markdown=True, show_tool_calls=True,
)

# 4. Passenger‑Alert Agent ──────────────
alert = Agent(
    name="Passenger‑Alert Agent",
    role="Send personalised delay or platform changes",
    model=OpenAIChat(id="gpt-4o"),
    tools=[
        AzureCommTools(sms=True, email=True),
        ReasoningTools(add_instructions=True)
    ],
    instructions=[
        "For each train with exp_delay > 5 min, craft message",
        "Call AzureCommTools.send_sms(email)",
        "Return JSON: {messages_sent}"
    ],
    markdown=True, show_tool_calls=True,
)

# 5. Orchestrator Team ──────────────────
orchestrator = Team(
    name="Rail Ops Orchestrator",
    mode="coordinate",
    model=OpenAIChat(id="gpt-4o"),
    members=[ingest, predict, planner, alert],
    tools=[MonitorWorkbookTools(write=True)],
    instructions=[
        "Run pipeline nightly 02:00 CET",
        "Pass outputs downstream as described",
        "After alerts, write KPI rows to Monitor Workbook ‘Rail‑KPIs’",
        "Return iframe URL of workbook for embedding in chat"
    ],
    success_criteria="All high‑risk assets scheduled & passengers notified",
    markdown=True, show_tool_calls=True,
    add_datetime_to_instructions=True
)

# ▶ Kick off once (cron or Azure Function in prod)
iframe = orchestrator.json_response(
    "Run nightly rail‑ops pipeline for 2025‑05‑05",
    show_intermediate_steps=False
)
print("Embed this in React:", iframe["link"])
