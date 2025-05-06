## Thames Water—the UK’s largest water company Problem / Solution

* **Ageing, siloed systems.**  A Guardian report says key apps still run on software from the late‑1980s; even rebooting servers is risky because spares are cannibalised from other machines. ([The Guardian][1])
* **Chronic leakage & reactive repairs.**  Regulators warn the network needs **£23 bn** just to stay functional; more than 500 million L of water disappear every day. ([The Guardian][2])
* **Customer pain.**  Complaints reaching the Consumer Council for Water jumped **29 % in 2023‑24**; callers wait weeks for an update on burst‑pipe claims. ([The Guardian][3])
* **Digital‑modernisation stalls.**  Vodafone & CSL are wiring new telemetry modems, yet data still lands in batch files that engineers open in Excel. ([Benchmark][4])

> *“So the live picture is: millions of sensors, millions of angry customers, and IT held together with duct‑tape.”*


Business flow we will automate

| Step                       | Pain today                                   | Specialist Agent         | Core Azure / OSS tools                                         | Widget surfaced to users                  |
| -------------------------- | -------------------------------------------- | ------------------------ | -------------------------------------------------------------- | ----------------------------------------- |
| 1. **Sensor ingest**       | Batch CSVs, hours late                       | **Ingest Agent**         | Azure IoT Hub → Time Series Insights                           | none (backend)                            |
| 2. **Leak prediction**     | Crews dispatched only after callers complain | **Leak‑Predictor Agent** | Azure ML (Gradient‑Boost) + ReasoningTools                     | Power BI tile “Top‑10 leaks by risk”      |
| 3. **Work‑order routing**  | Manual Excel rostering                       | **Crew‑Scheduler Agent** | Snowflake Text‑to‑SQL, OR‑Tools MILP                           | Azure Maps iframe of crew routes          |
| 4. **Customer concierge**  | Day‑long phone queues                        | **Concierge Agent**      | Rail‑style live API, Cognitive Search FAQ, Azure Comm Svcs SMS | Embedded chat widget on thameswater.co.uk |
| 5. **Regulatory reporter** | Quarterly PDF compiled by hand               | **Ofwat‑Reporter Agent** | ReasoningTools → XML generator → Blob Storage                  | Signed download link after submission     |

All five run in an Agno **coordinate** team; every response carries MCP headers `{region, pipe_id, timestamp}` for traceability.

---

#### Sample Python (Agno) — trimmed but runnable

```python
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
```

---

#### What customers experience on **thameswater.co.uk**

1. **Real‑time chat**: The Concierge agent greets a user, detects their postcode, and instantly returns
   *“We’re aware of a high‑risk leak 220 m away; crew ETA **15 min**. Here’s your statutory compensation form (PDF).”*
2. **Interactive map**: The chat payload includes `map_url`; the React site embeds an **Azure Maps** iframe so the customer can watch the crew van approach.
3. **Pro‑active SMS**: If the risk model later predicts >30 min slip, Azure Comm Svcs auto‑texts *“Sorry, revised ETA 14:55; we’ve applied a £30 credit to your account.”*

---

### Final takeaway

Thames Water’s leaks, legacy IT and customer frustration are tailor‑made for an **Agentic AI overhaul**.  A light, Azure‑native stack—IoT Hub, ML endpoints, OR‑Tools optimisation, Cognitive Search, Power BI—wrapped in Agno Agent Teams can:

* shrink leak‑to‑repair time from **days to hours**,
* cut complaint load with proactive concierge answers,
* and auto‑generate regulator‑ready XML—all while every step is auditable through MCP headers and embedded dashboards.

[1]: https://www.theguardian.com/business/2024/nov/18/thames-waters-it-falling-apart-and-is-hit-by-cyber-attacks-sources-claim?utm_source=chatgpt.com "Thames Water's IT 'falling apart' and is hit by cyber-attacks, sources claim"
[2]: https://www.theguardian.com/business/2024/nov/17/thames-water-supply-knife-edge-23bn-repairs-needed?utm_source=chatgpt.com "Thames Water supply 'on knife-edge' with £23bn repairs needed"
[3]: https://www.theguardian.com/business/2024/oct/03/unresolved-complaints-water-firms-england-wales?utm_source=chatgpt.com "Unresolved water complaints in England and Wales rise to near ..."
[4]: https://benchmarkmagazine.com/thames-waters-journey-to-digital-transformation-with-vodafone-and-csl/?utm_source=chatgpt.com "Thames Water's Journey to Digital Transformation with Vodafone ..."



