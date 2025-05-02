from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import (
    SnowflakeTools, AzureBlobTools,
    ORTools, ReasoningTools,
    SAPIBPTools, QdrantSearchTools,
    OutlookTools, MapboxRouteTools
)
from agno.team import Team

# 1. Ingest raw data
ingest = Agent(
    name="Ingest Agent",
    role="Load and embed all new supply-chain data",
    model=OpenAIChat(id="gpt-4o"),
    tools=[SnowflakeTools(), AzureBlobTools(), QdrantSearchTools()],
    instructions=["Fetch yesterday’s SAP extracts", "Embed docs to Qdrant"],
    show_tool_calls=True, markdown=True
)

# 2. Forecast demand
forecast = Agent(
    name="Forecast Agent",
    role="Produce SKU-DC demand forecasts",
    model=OpenAIChat(id="gpt-4o"),
    tools=[ReasoningTools(), ORTools()],
    instructions=["Retrieve sales embeddings", "Generate P10/P50/P90 per SKU-DC"],
    show_tool_calls=True, markdown=True
)

# 3. Optimize inventory
optimizer = Agent(
    name="Optimizer Agent",
    role="Compute safety stock levels",
    model=OpenAIChat(id="gpt-4o"),
    tools=[SnowflakeTools(), ORTools(), SAPIBPTools()],
    instructions=[
        "Get live forecast & stock", 
        "Solve MILP for min/max policy", 
        "Push results back to SAP IBP"
    ],
    show_tool_calls=True, markdown=True
)

# 4. Risk detection
risk = Agent(
    name="Risk Agent",
    role="Detect supplier delays and quality issues",
    model=OpenAIChat(id="gpt-4o"),
    tools=[OutlookTools(), QdrantSearchTools(), ReasoningTools()],
    instructions=[
        "Monitor ASN events & supplier emails",
        "Flag >24h delays or quality flags",
        "Create JIRA tickets if needed"
    ],
    show_tool_calls=True, markdown=True
)

# 5. Green routing
routing = Agent(
    name="Routing Agent",
    role="Optimize outbound loads for cost and carbon",
    model=OpenAIChat(id="gpt-4o"),
    tools=[MapboxRouteTools(), ReasoningTools()],
    instructions=[
        "Pull today’s outbound orders",
        "Replan loads for lowest gCO₂/t.km",
        "Generate weekly carrier scorecard"
    ],
    show_tool_calls=True, markdown=True
)

# Build the team in “coordinate” mode
supply_chain_team = Team(
    mode="coordinate",
    members=[ingest, forecast, optimizer, risk, routing],
    model=OpenAIChat(id="gpt-4o"),
    instructions=[
        "Execute the daily replenishment pipeline from ingest to routing",
        "Pass outputs of one agent as inputs to the next",
        "Log MCP headers for audit: plant, horizon, timestamp"
    ],
    success_criteria="All stock policies updated and no unhandled risks",
    show_tool_calls=True,
    markdown=True
)

# Kick off the daily run
supply_chain_team.print_response(
    "Run daily replenishment cycle for Plant Allendorf, horizon 90d",
    stream=True
)
