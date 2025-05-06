from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.tools import (
    AzureIoTHubTools, TimeSeriesInsightsTools,
    AzureMLTools, SnowflakeTools, ORTools,
    AzureMapsTools, AzureCommTools,
    CognitiveSearchTools, ReasoningTools,
    BlobStorageTools
)

# 1. Ingest
ingest = Agent(
    name="Ingest",
    role="Stream sensors to TSI",
    model=OpenAIChat("gpt-4o"),
    tools=[AzureIoTHubTools(receive=True),
           TimeSeriesInsightsTools(write=True),
           ReasoningTools(add_instructions=True)],
    instructions=[
        "On new IoT batch, standardise schema, push to TSI",
        "Return JSON {batch_id, rows}"
    ], markdown=True, show_tool_calls=True)

# 2. Leak predictor
predict = Agent(
    name="Leak‑Predictor",
    role="Rank pipes by 48 h failure risk",
    model=OpenAIChat("gpt-4o"),
    tools=[AzureMLTools(deployments=["gb_leak"]),
           ReasoningTools()],
    instructions=[
        "Pull last 7d metrics from TSI",
        "Call ML endpoint, threshold prob>0.6",
        "Return [{pipe_id, risk, lat, lon}]"
    ], markdown=True, show_tool_calls=True)

# 3. Scheduler
schedule = Agent(
    name="Crew‑Scheduler",
    role="Assign crews to high‑risk leaks",
    model=OpenAIChat("gpt-4o"),
    tools=[SnowflakeTools(select=True),
           ORTools(milp=True),
           AzureMapsTools(route=True)],
    instructions=[
        "Fetch crew locations & shifts from Snowflake",
        "Solve MILP: min Σ travel_time, cover top‑N leaks",
        "Return map_url + workorders"
    ], markdown=True, show_tool_calls=True)

# 4. Concierge
concierge = Agent(
    name="Concierge",
    role="Answer customer questions & push live ETA",
    model=OpenAIChat("gpt-4o"),
    tools=[CognitiveSearchTools(index="faq"),
           AzureCommTools(sms=True, email=True)],
    instructions=[
        "If postcode matches active leak, embed ETA & comp link",
        "Else answer via FAQ RAG; cite source"
    ], markdown=True, show_tool_calls=True)

# 5. Regulatory
ofwat = Agent(
    name="Ofwat‑Reporter",
    role="Submit quarterly XML returns",
    model=OpenAIChat("gpt-4o"),
    tools=[BlobStorageTools(write=True),
           ReasoningTools()],
    instructions=[
        "Transform schedule+predict data into Ofwat XML schema",
        "Write to Blob, return signed_url"
    ], markdown=True, show_tool_calls=True)

# Orchestrator team
water_ops = Team(
    name="Water‑Ops Orchestrator",
    mode="coordinate",
    model=OpenAIChat("gpt-4o"),
    members=[ingest, predict, schedule, concierge, ofwat],
    instructions=[
        "Run every 15 min; pass JSON downstream",
        "After each cycle, push KPI row to Power BI dataset"
    ],
    success_criteria="Leaks prioritised, crews dispatched, customers informed",
    markdown=True
)

# one‑shot trigger (cron/Azure Function in prod)
response = water_ops.json_response("Run cycle 2025‑05‑06‑12:00")
print("Embed Power BI KPI tile:", response["powerbi_url"])
