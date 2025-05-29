## 🧠 **Executive Layer**

**Agent**: `Executive-Director`
**Mode**: `coordinate`
**Tools**: SlackTools, TwilioTools
**Responsibilities**:

* Delegates to all managers and teams
* Posts daily digest to `#executive_updates` and WhatsApp
* Triggers `Cost-Sentinel` daily at 23:00 UTC

---

## 🧩 **Functional Manager Teams**

### 📚 Content Team

**Manager**: `Content-Manager`
**Agents**:

* `Content-Ideator`: Generates hooks (DuckDuckGo, Wikipedia)
* `LinkedIn-Post-Writer`: Writes LinkedIn posts
* `YouTube→Blog`: Transforms YouTube to blog
* `LinkedIn→Newsletter`: LinkedIn post to newsletter
* `YouTube→LinkedIn`: Highlights to LinkedIn
* `LinkedIn→X`: Shortens content for X

---

### 💬 Comms Team

**Manager**: `Comms-Manager`
**Agents**:

* `Slack-Assistant`: Slack replies (SlackTools)
* `LinkedIn-DM-Assistant`: Handles LinkedIn DMs
* `WhatsApp-Assistant`: Handles WhatsApp (TwilioTools)
* `Calendar-Assistant`: Manages Google Calendar
* `Gmail-Assistant`: Writes Gmail drafts

---

### 📈 Marketing Team

**Manager**: `Marketing-Manager`
**Agents**:

* `Ad-Designer`: Creates ads (ReplicateTools)
* `Social-Performance-Analyst`: Social KPIs (GDrive, Pandas)
* `Ad-Performance-Analyst`: ROAS analysis (GDrive, Pandas)

---

### 🔬 Research Team

**Manager**: `Research-Manager`
**Agents**:

* `General-Researcher`: Web research (DuckDuckGo)
* `GTM-Strategist`: Go-to-market briefs (Pandas)

---

### ✉️ Outbound Team

**Manager**: `Outbound-Manager`
**Agents**:

* `Intent-Signal-Analyst`: Scores leads' intent (DuckDuckGo, Pandas)
* `Outbound-Copywriter`: Writes cold emails (GmailTools)

---

## 💼 Sales Team

**Manager**: `Sales-Manager`
**Sub-team**: `Lead-Gen Team` (see below)
**Agents**:

* `Competitive-Intel`: Battle cards (DuckDuckGo, Wikipedia)
* `Pricing-Strategist`: Builds pricing tables (Pandas)
* `Offer-Packager`: Creates Good/Better/Best tiers
* `Sales-Enablement`: Creates decks (GoogleDrive, FileTools)
* `Pipeline-Forecaster`: Forecasts bookings (CSV, Pandas)
* `Pre-Call-Assistant`: Discovery brief
* `Post-Call-Assistant`: Meeting recap
* `Lead-Researcher`: Manual lookup
* `CRM-Assistant`: Updates CRM (CSV)

---

## 🧪 Experiments Team

**Team**: `Experiments`
**Mode**: `coordinate`
**Agents**:

* `Experiment-Planner`: A/B test definitions (Pandas)
* `Experiment-Runner`: Executes and monitors (Shell)
* `Experiment-Reporter`: Reports outcomes (Pandas)

---

## 👋 Onboarding Team

**Team**: `Onboarding-Team`
**Mode**: `coordinate`
**Agents**:

* `Slack-Channel-Bot`: Creates Slack workspace
* `Drive-Space-Bot`: Sets up Google Drive
* `CRM-Deal-Bot`: Creates CRM entries (CSV)

---

## 🧪 QA & Governance

### QA

**Manager**: `Review-Manager`
**Agents**:

* `Review-Critique`: Brand/style QA (rewrites content off-brand)

### Security

**Manager**: `Security-Manager`
**Agents**:

* `SecOps-Linter`: Code scan for secrets, PII, CORS issues (PythonTools)

---

## 🧾 Cost Monitoring

**Agent**: `Cost-Sentinel`
**Mode**: `collaborate`
**Tools**: PandasTools
**Role**:

* Collects cost tags
* Posts daily #finops chart

---

## 🧑‍💻 Developer Team

**Manager**: `Developer-Manager`
**Agents**:

* `Frontend-Dev`: Builds React/Vite apps (File, Shell)
* `Backend-Dev`: Builds FastAPI backends (Python, Shell)
* `Fullstack-Integrator`: Integrates, adds CORS, envs

---

## 📄 Documentation Team *(New in v6)*

**Part of**: `Project-Manager`
**Agents**:

* `Doc-Architect`: Designs doc skeleton
* `API-Doc-Writer`: Markdown + code samples (PythonTools)
* `Changelog-Agent`: Creates release notes
* `Tutorial-Writer`: Onboarding guides
* `Notion-Assistant`: Updates Notion workspace
* `GDrive-Assistant`: Manages GDrive assets

---

## 🧠 Lead-Gen Pipeline (11 steps)

**Team**: `Lead-Gen Team`
**Mode**: `coordinate`
**Pipeline**:

1. `Parser`: Extracts query params
2. `Searcher`: Google LinkedIn search
3. `Extractor`: Extracts name, company, etc.
4. `Enricher`: Adds firmographic data
5. `Scorer`: Adds 0-100 score
6. `Emailer`: Writes outreach email
7. `Sentiment`: Scores company sentiment
8. `FollowUp`: Adds followup emails (Day 3, 8)
9. `Bounce`: MX check
10. `Geo`: Adds lat/lng, map
11. `Summariser`: Markdown table

---

## 🚀 FastAPI Endpoint

| **Endpoint** | `/api/generate-leads`                                                                                             |
| ------------ | ----------------------------------------------------------------------------------------------------------------- |
| **Input**    | JSON: `{ "message": "..." }`                                                                                      |
| **Response** | `{ "leads_markdown": "..." }`                                                                                     |
| **Purpose**  | Enables direct, stateless access to Lead-Gen without invoking the chat loop. Still uses 11 agents under the hood. |
| **Benefits** | Parallelism, clean integration with CRM, reuse in Zapier/UIs                                                      |

---

## 🔢 Agent Count (v6 Total)

| Category                      | Count  |
| ----------------------------- | ------ |
| Route-mode managers           | 10     |
| Coordinate teams (incl. Exec) | 5      |
| Sentinel                      | 1      |
| Worker agents                 | 55     |
| **Total agents**              | **71** |

---

## ✅ Example Tasks via Executive-Director

| Request                                               | Outcome                                          |
| ----------------------------------------------------- | ------------------------------------------------ |
| “Pull 10 CFO leads in Germany”                        | Lead-Gen pipeline is triggered                   |
| “Build a React PoC for a pricing calculator”          | Developer team delivers file structure           |
| “Outline and generate API docs for BlueRail client”   | Documentation agents kick in via Project-Manager |
| “Scan the GitHub repo for secrets or bad CORS config” | Security Manager runs SecOps-Linter              |
| “Run A/B test on pricing headlines”                   | Experiment team plans, runs, and reports         |
| “Create Slack + Drive + CRM for Acme Inc”             | Onboarding team spins up all systems             |

---


### 🗺️ Agent hierarchy 
![image](https://github.com/user-attachments/assets/2c70296b-e581-4716-8dda-2c07c0e5e238)
