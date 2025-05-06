# pip install agno[azure,ortools,translator] railtools
from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.tools import (RailLiveTools, AzureMapsTools, ORTools,
                        TranslatorTools, LogicAppTools, CognitiveSearchTools,
                        ReasoningTools)

live_info = Agent(
    name="Live‑Info",
    role="Predict and explain upcoming delays",
    model=OpenAIChat("gpt-4o"),
    tools=[RailLiveTools(), AzureMapsTools(), ReasoningTools()],
    instructions=[
        "Pull current train_id status",
        "Predict downstream delay >5 min",
        "Return JSON {train_id, eta, cause, map_url}"
    ],
    show_tool_calls=True,
    markdown=True,
)

planner = Agent(
    name="Route‑Planner",
    role="Offer best alternative when connection at risk",
    model=OpenAIChat("gpt-4o"),
    tools=[RailLiveTools(), ORTools(milp=True), ReasoningTools()],
    instructions=[
        "If eta makes connection_prob <0.9, call ORTools to find alt route",
        "Return deep‑link QR ticket URL"
    ],
    markdown=True,
)

refund = Agent(
    name="Compensation",
    role="Auto‑file refund if delay ≥60 min",
    model=OpenAIChat("gpt-4o"),
    tools=[LogicAppTools(endpoint="file_refund")],
    instructions=[
        "Verify eligibility under EU 1371/2007",
        "Call LogicAppTools with passenger data",
        "Return PDF download URL"
    ],
    markdown=True,
)

access = Agent(
    name="Accessibility",
    role="Answer accessibility queries",
    model=OpenAIChat("gpt-4o"),
    tools=[CognitiveSearchTools(index="station-facilities")],
    instructions=["RAG over station brochures; cite sources"],
    markdown=True,
)

polyglot = Agent(
    name="Polyglot",
    role="Translate replies",
    model=OpenAIChat("gpt-4o"),
    tools=[TranslatorTools()],
    instructions=[
        "Detect user language; translate final JSON['reply'] field"
    ],
    markdown=True,
)

concierge = Team(
    name="DB Concierge",
    mode="coordinate",
    model=OpenAIChat("gpt-4o"),
    members=[live_info, planner, refund, access, polyglot],
    instructions=[
        "Start with Live‑Info; branch as needed",
        "Attach map_url or pdf_url so front‑end can iframe",
    ],
    success_criteria="Accurate advice + artefact link delivered",
    markdown=True,
)
