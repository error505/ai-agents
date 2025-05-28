### 📊 Current AI-Agent

| Layer                           | Mode          | Count | Agents & Core Tasks                                                                                                                                                                                                                                |
| ------------------------------- | ------------- | ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Executive**                   | `coordinate`  | 1     | **Executive-Director** – delegates, aggregates Slack summaries, posts digest & WhatsApp, triggers Cost-Sentinel nightly                                                                                                                            |
| **Route-mode managers**         | `route`       | 10    | Content-Mgr · Comms-Mgr · Marketing-Mgr · Research-Mgr · Outbound-Mgr · **Project-Mgr** (now with doc squad) · Sales-Mgr · Developer-Mgr · Review-Mgr (QA) · Security-Mgr                                                                          |
| **Coordinate teams (mid-tier)** | `coordinate`  | 3     | **Lead-Gen Team** (11-step pipeline) · **Experiments Team** (plan/run/report A/Bs) · **Onboarding Team** (Slack + Drive + CRM spin-up)                                                                                                             |
| **Collaborate sentinel**        | `collaborate` | 1     | **Cost-Sentinel** – listens to MCP cost tags, posts daily spend chart                                                                                                                                                                              |
| **Worker agents**               | —             | 56    | 6 Content · 5 Comms · 3 Marketing · 2 Research · 2 Outbound · 6 Project (doc + ops) · 3 Developer · 9 Sales specialists · 11 Lead-Gen micros · 1 QA Critique · 3 Experiment workers · 3 Onboarding bots · 1 SecOps linter · 1 Cost sentinel worker |

**Grand total → 71 autonomous agents**
(15 containers / managers / sentinels + 56 individual workers)

---

### 🛠️ Using the stack — sample prompts

| Goal                      | Say to Executive-Director                                                         |
| ------------------------- | --------------------------------------------------------------------------------- |
| **Generate leads**        | “Pull 12 VP-Engineering leads in Ontario and email drafts.”                       |
| **Quick PoC site**        | “Spin up a React-TS landing page that calls /api/leads.”                          |
| **FastAPI stub**          | “I need a FastAPI micro-service with `POST /quote` for a demo.”                   |
| **Package & price**       | “Package our AI Audit into Good/Better/Best and give me a price table.”           |
| **Full docs**             | “Outline full project docs for client BlueRail, then write the API section.”      |
| **A/B test**              | “Run an A/B headline test for the pricing page and stop losers after 500 visits.” |
| **New-client onboarding** | “Onboard Acme Corp — create Slack, Drive, CRM deal.”                              |
| **Security sweep**        | “Scan the React PoC repo for secrets or open CORS.”                               |

The Executive-Director auto-routes each request; you just use natural language—no need to address workers directly.

---

### 🗺️ Agent hierarchy (Mermaid)

```mermaid
graph TD
  ED[Executive-Director (coordinate)]
  
  subgraph Managers
    CM[Content-Mgr]
    CoM[Comms-Mgr]
    MM[Marketing-Mgr]
    RM[Research-Mgr]
    OM[Outbound-Mgr]
    PM[Project-Mgr]
    SM[Sales-Mgr]
    DM[Developer-Mgr]
    QM[Review-Mgr]
    SecM[Security-Mgr]
  end
  
  subgraph CoordTeams
    LG[Lead-Gen Team\n(coordinate)]
    EXP[Experiments Team\n(coordinate)]
    ONB[Onboarding Team\n(coordinate)]
  end
  
  CS[Cost-Sentinel\n(collaborate)]
  
  ED -->|delegates| CM
  ED --> CoM
  ED --> MM
  ED --> RM
  ED --> OM
  ED --> PM
  ED --> SM
  ED --> DM
  ED --> QM
  ED --> SecM
  ED --> LG
  ED --> EXP
  ED --> ONB
  ED --> CS
  
  %% just one worker sample per pool to keep diagram readable
  CM --> CI[Content-Ideator]
  PM --> DocA[Doc-Architect]
  DM --> FE[Frontend-Dev]
  SM --> Comp[Competitive-Intel]
  LG --> Parser[Parser]
  ONB --> Chan[Slack-Channel-Bot]
  QM --> Crit[Review-Critique]
  SecM --> Lint[SecOps-Linter]
```

*Rectangles = managers / teams; rounded = example workers.*

---
![image](https://github.com/user-attachments/assets/2c70296b-e581-4716-8dda-2c07c0e5e238)


### 🚀 Next steps

* **Run a dry-run**:
  `python marketing_agency_ai_stack.py` and watch the Slack channels populate.
* **Hit the REST lead service**:
  `curl -X POST localhost:8000/api/generate-leads -d '{"message":"10 CFOs in France"}'`
* **Customize**: update routing keywords or memory paths as your org evolves.
