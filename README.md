# 🌍 GSI Radar
### Grassroots Science & Innovation Intelligence Engine

> An AI-powered autonomous system that continuously discovers, structures, scores, and maps human innovation — from high-level institutional projects to undocumented grassroots solutions — complete with risk detection, knowledge lineage tracing, and intervention prioritisation.

<div align="center">

[![GitHub Actions](https://img.shields.io/badge/Automated-GitHub_Actions-2088FF?style=flat-square&logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Powered by Gemini](https://img.shields.io/badge/AI-Gemini_2.5_Flash-4285F4?style=flat-square&logo=google&logoColor=white)](https://aistudio.google.com)
[![Live on GitHub Pages](https://img.shields.io/badge/Dashboard-GitHub_Pages-222222?style=flat-square&logo=github&logoColor=white)](https://pages.github.com)
[![Data Updated](https://img.shields.io/badge/Data_Interval-Every_2_Days-00ffcc?style=flat-square)](#-schedule--automation)

*Built for those who innovate quietly — before the world notices.*

</div>

---

## 📋 Table of Contents

- [What is GSI Radar?](#-what-is-gsi-radar)
- [Why It Exists](#-why-it-exists)
- [What Makes It Different](#-what-makes-it-different)
- [Live Dashboards](#-live-dashboards)
- [System Architecture](#-system-architecture)
- [The 5-Layer Pipeline](#-the-5-layer-pipeline)
- [Priority Scoring Engine (PSE)](#-priority-scoring-engine-pse)
- [Boolean Classification Triggers](#-boolean-classification-triggers)
- [Data Intelligence Model](#-data-intelligence-model--full-schema)
- [Schedule & Automation](#-schedule--automation)
- [Project Structure](#-project-structure)
- [Setup & Deployment](#-setup--deployment)
- [Environment Variables](#-environment-variables)
- [Use Cases](#-use-cases)
- [Limitations & Known Blind Spots](#-limitations--known-blind-spots)
- [Roadmap](#-roadmap)
- [Disclaimer](#-disclaimer)

---

## 🔍 What is GSI Radar?

**Grassroots Science & Innovation (GSI)** refers to practical, problem-solving knowledge developed by individuals, communities, and institutions — most often *outside* formal research systems, and frequently never documented at all.

GSI Radar is an **autonomous AI intelligence engine** that runs on a schedule, continuously discovering and structuring innovations from across the web. It does not wait for submissions or rely on institutional databases. It actively hunts.

The system covers the full innovation spectrum:

| Layer | Who | Example |
|---|---|---|
| **Grassroots** | Individual inventors, rural communities | DIY biosand water filter built from local materials |
| **Semi-formal** | NGOs, community cooperatives, pilot projects | Village-run micro-hydro system, NGO-supported seed bank |
| **Institutional** | Universities, governments, funded research | SDG-aligned water purification programme |

Every entry is enriched with **risk assessment**, **replicability scoring**, **geographic coordinates**, and **knowledge provenance** — not just a title and summary.

---

## 💡 Why It Exists

Most global innovation systems — including those aligned with UNESCO, UNDP, or major research universities — tend to surface:

- ✅ Validated, peer-reviewed knowledge
- ✅ Funded and formally recognised programmes
- ✅ English-language, digitally-visible work

What they miss:

- ❌ Practices that exist only in oral tradition
- ❌ Innovations with no institutional sponsor
- ❌ Solutions that are *working* but *dangerous*
- ❌ Technologies that predate documentation infrastructure
- ❌ Brilliant ideas in communities with no internet presence

**The consequence:** programmes are designed without knowledge of what communities have already invented. Safety interventions arrive too late. Funding goes to reinventing wheels while proven local solutions remain invisible.

GSI Radar focuses on four principles:

1. **Science from below** — capturing knowledge before it is institutionally recognised
2. **Innovation before validation** — documenting what is *working* before it passes a peer review gate
3. **Risk before disaster** — flagging dangerous practices so intervention can be proactive, not reactive
4. **Potential before recognition** — ensuring high-impact, low-cost solutions are visible to those who can scale them

---

## ⚖️ What Makes It Different

| Dimension | Traditional Innovation Systems | GSI Radar |
|---|---|---|
| **Scope** | Institutional & validated only | Grassroots → institutional full spectrum |
| **Discovery** | Requires formal submission | Fully autonomous web discovery |
| **Risk visibility** | None | Risk score 1–10 per entry |
| **Safety flagging** | None | Critical flags + intervention triggers |
| **Knowledge tracing** | Rarely tracked | Full lineage: traditional, self-taught, internet, adapted |
| **Cost data** | Rarely included | Cost level + replicability difficulty |
| **Updating** | Static or annual | Continuously evolving (every 2 days) |
| **Coverage bias** | English, formal, funded | Actively pursues undocumented & informal |

---

## 🖥️ Live Dashboards

This repository powers **two distinct frontend interfaces** for different audiences, both fed from the same `data.json` and `resume.json` files:

### 1. Innovation Radar Dashboard (`dashboard_plus_map_prototype.html`)
An interactive intelligence dashboard designed for **analysts and decision-makers**:
- 🗺️ Leaflet map with marker clustering (handles 100k+ points)
- 📊 ECharts radar chart per innovation in a detail modal
- 📋 Multi-tab navigation: Map / Cards / Resume / Export
- 🔍 Full-text search + multi-filter sidebar
- 📤 Export to OAI-DC–compliant XML, JSON, and printable PDF per card
- 🔵 AI-generated quarterly intelligence report tab (Resume)

### 2. GII Bulletin (`journal_copy.html`)
An academic journal-style publication designed for **researchers, NGOs, and policy readers**:
- 📰 A4 editorial layout (Playfair Display + Crimson Pro typography)
- 🌗 Dark / light mode with `localStorage` persistence
- 📈 Chart.js visualisations: category distribution, risk histogram, risk × priority scatter
- 🕸️ `vis-network` knowledge graph connecting innovations by shared category
- 📍 Leaflet clustered map
- 📄 Paginated, sortable, filterable data register (Appendix A)
- 📥 CSV export with all 15 fields, properly quoted
- 🖨️ Print-to-PDF mode with clean white layout

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        SCHEDULER (GitHub Actions)               │
│   Triggers: every 2 days (data) | every 90 days (report)       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         scraper.py                              │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  L1      │→ │  L2      │→ │  L3      │→ │  L4      │       │
│  │DISCOVERY │  │EXTRACTION│  │   RISK   │  │ LINEAGE  │       │
│  │(search)  │  │(structure│  │(scoring) │  │(provenance│      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                                                    │            │
│                                       ┌────────────▼──────────┐│
│                                       │   L5: PSE SYNTHESIS   ││
│                                       │ Priority Score 0–100  ││
│                                       │ + Deduplication       ││
│                                       └───────────┬───────────┘│
└───────────────────────────────────────────────────┼────────────┘
                                                    │
                    ┌───────────────────────────────┘
                    │
          ┌─────────▼──────────┐         ┌─────────────────────┐
          │    data.json       │         │    resume.json       │
          │ (append-only DB)   │         │ (quarterly reports)  │
          └─────────┬──────────┘         └──────────┬──────────┘
                    │                               │
          ┌─────────▼───────────────────────────────▼──────────┐
          │              GitHub Pages (static hosting)          │
          │                                                     │
          │  ┌────────────────────┐  ┌──────────────────────┐  │
          │  │  Radar Dashboard   │  │    GII Bulletin       │  │
          │  │ (dashboard.html)   │  │  (journal_copy.html)  │  │
          │  └────────────────────┘  └──────────────────────┘  │
          └─────────────────────────────────────────────────────┘
```

---

## ⚙️ The 5-Layer Pipeline

Each discovery run processes candidates through five sequential layers. A failure at Layer 1 or 2 silently discards the candidate. Failures at Layers 3–4 apply safe defaults.

---

### 🔍 Layer 1 — Discovery

**What:** A single keyword is randomly selected from a pool of **60 curated search phrases** across 10 thematic domains. That keyword is submitted to the Gemini API with **Google Search grounding enabled** — meaning Gemini actively retrieves live web content before responding.

**Why random selection:** Prevents systematic overrepresentation of any single domain across consecutive runs. Over time, all 10 domains receive proportional coverage.

**The 10 thematic domains covered:**

| Domain | Example Keywords |
|---|---|
| Agriculture & Food | "DIY farming tools self-taught farmer", "homemade pesticide organic village" |
| Water & Sanitation | "improvised water filter rural village", "clay pot water purification traditional" |
| Energy & Electricity | "homemade biogas digester cow dung", "wind turbine scrap metal village maker" |
| Health & Medicine | "improvised stretcher ambulance rural community", "low cost prosthetic limb local maker" |
| Construction & Shelter | "plastic bottle brick house slum innovation", "earthbag construction community self-built" |
| Education & Communication | "offline education tool rural school DIY", "solar powered tablet charging station village" |
| Tools & Manufacturing | "blacksmith innovation local tool adaptation Africa", "scrap metal workshop village innovation" |
| Environment & Waste | "plastic waste upcycling community enterprise", "river cleanup tool homemade community" |
| Transportation | "cargo bicycle modification local welder", "low cost boat motor adaptation fisher community" |
| Finance & Social | "community savings innovation rotating fund village", "mobile money workaround rural community" |

**Output:** Up to 5 raw candidate descriptions with associated source URLs, returned as a JSON array.

---

### 🧠 Layer 2 — Extraction

**What:** Each raw candidate text is passed through Gemini's NLP extraction layer, which populates a structured JSON record with 30+ fields.

**Validation gate (Pass 1):** Before extraction, each candidate is first validated:
- Does it represent a real-world innovation? (`is_innovation: true/false`)
- Confidence score ≥ 0.60 required to proceed

Candidates that fail this gate are discarded silently. This prevents fictional, speculative, or non-technical content from entering the database.

**Key fields extracted:** title, summary, category tags (multi-label), innovation level, country, region, process description, materials list, step-by-step instructions, impact scale, cost level, and replicability difficulty.

---

### ⚠️ Layer 3 — Risk Assessment

**What:** The candidate text is re-analysed specifically for hazards, using a **conservative rubric** (when in doubt, score higher). Gemini assigns:
- `risk_score`: integer 1–10
- `risk_type[]`: array of hazard categories (fire, toxic, explosion, chemical, structural, electrical, environmental)
- `needs_intervention`: boolean — true if risk ≥ 6 with no documented safety protocols
- `explanation`: plain-language justification for the assigned score

**Risk score reference:**

| Score | Band | Criteria |
|---|---|---|
| 1 | Negligible | No physical hazard. Purely organisational/informational. |
| 2–3 | Low | Standard household tools, no hazardous materials. |
| 4–5 | Moderate | Open fire, sharp tools, minor chemical exposure. |
| 6 | Moderate-High | Electrical work, pressurised systems, undocumented toxic handling. |
| 7–8 | High | Explosive/flammable materials, high-voltage, toxic chemicals. |
| 9–10 | Critical | Imminent lethal risk without professional supervision. Triggers `critical_flag`. |

> **Design principle:** Risk scores reflect *inherent hazard*, not observed outcomes. An innovation with a score of 8 may have caused zero injuries — the score reflects potential, not history. This is intentional: GSI Radar is a preventive tool.

---

### 🌿 Layer 4 — Knowledge Lineage

**What:** The origin of the technical knowledge behind the innovation is traced and classified. This is about *where the idea came from*, not where the innovator lives.

| Lineage Type | Definition | Policy Implication |
|---|---|---|
| **Traditional** | Ancestral knowledge, oral tradition, cultural memory — often centuries old | Triggers IP caution: indigenous knowledge rights, FPIC frameworks |
| **Self-taught** | Pure empiricism — individual trial-and-error with no reference materials | Highest authenticity signal for development researchers |
| **Internet** | Sourced from YouTube, forums, or social media and locally implemented | Indicates functioning digital knowledge pathways |
| **Adapted** | Deliberate modification of a known technology for local constraints | Fastest path to scaling — core tech already validated |
| **Formal education** | Trained technician applying professional knowledge outside institutional settings | Often classified semi-formal at level field, but formal at lineage |

---

### 📊 Layer 5 — Synthesis & Deduplication

**What:** The Priority Scoring Engine (PSE) calculates a 0–100 index. Then a deduplication check runs before the record is appended to the database.

**Deduplication process:**
1. Title is Unicode-NFKC normalised → lowercased → whitespace stripped
2. Normalised title + country are concatenated and MD5-hashed → becomes the `id` field
3. If that `id` already exists in `data.json` → candidate is discarded
4. If new → record is appended

This means `"DIY Water Filter"`, `"diy water filter"`, and `"DIY Water Filter "` all produce the same ID and only the first is kept.

> **Known gap:** Semantically identical innovations with different titles (e.g. "SODIS" vs "Solar Water Disinfection") are not caught by this approach. Embedding-based deduplication is planned.

---

## 🎯 Priority Scoring Engine (PSE)

The PSE Index is the single number (0–100) that ranks every entry in the database. It answers: **"Which innovations most deserve attention for safe, large-scale replication?"**

### Formula

```
PSE Index = [ (I × 0.4) + (R × 0.2) + ((10 − S) × 0.4) ] × 10
```

| Variable | Weight | Parametric Value Mapping |
|---|---|---|
| **I** — Impact Score | 40% | High scale → 10 · Medium → 6 · Low → 2 |
| **R** — Replicability Score | 20% | Easy + cheap → 10 · Medium → 5 · Hard/expensive → 2 |
| **(10 − S)** — Safety Coefficient | 40% | Inverse of Risk Score. Low risk (S=1) → coeff 9. Critical (S=9) → coeff 1. |

### Why These Weights?

- **Impact and Safety are equally weighted at 40%** — this is the core design decision. A high-impact innovation that could kill practitioners cannot be responsibly promoted without safety documentation. The equal weighting ensures neither concern dominates the other.
- **Replicability at 20%** — present but secondary. An innovation unavailable to the communities it's designed for has limited practical value, but replicability alone shouldn't determine priority.
- **The (10−S) inversion** — this is the "algorithmic brake." A high risk score *mathematically prevents* an innovation from achieving Top Priority status, regardless of its impact. A risk score of 9 yields a safety coefficient of just 1, collapsing its contribution to 0.4/4.0 possible points from that variable.

### Worked Examples

**Example A — Biosand Water Filter (I=10, R=10, S=2)**
```
(10 × 0.4) + (10 × 0.2) + ((10−2) × 0.4) = 4.0 + 2.0 + 3.2 = 9.2 × 10 = 92/100
```
→ High impact + easy to replicate + very safe = Top Priority ✅

**Example B — Improvised Biogas Digester (I=10, R=5, S=7)**
```
(10 × 0.4) + (5 × 0.2) + ((10−7) × 0.4) = 4.0 + 1.0 + 1.2 = 6.2 × 10 = 62/100
```
→ Despite high impact, S=7 yields coefficient of only 3. The brake activates. Needs safety docs before scaling. ⚠️

**Example C — Improvised Pesticide from Industrial Waste (I=6, R=5, S=9)**
```
(6 × 0.4) + (5 × 0.2) + ((10−9) × 0.4) = 2.4 + 1.0 + 0.4 = 3.8 × 10 = 38/100
```
→ S=9 produces coefficient of 1. Quarantined from scaling. `critical_flag = true`. 🚫

### Score Interpretation

| Range | Band | Meaning |
|---|---|---|
| 80–100 | **Top Priority** | Ideal for institutional adoption, funding, technology transfer |
| 60–79 | **Strong Candidate** | Recommend field validation and safety documentation before scaling |
| 40–59 | **Conditional** | Requires significant risk mitigation. Useful as research reference |
| 0–39 | **Flagged / Archive** | Documented for awareness. Not recommended for replication |

---

## 🔘 Boolean Classification Triggers

Two binary flags operate **independently** of the PSE score. An entry can carry a flag even if its PSE is middling, and vice versa.

### 💎 Hidden Gem
```python
if (innovation_level == "grassroots") 
   and (cost_level == "low") 
   and (impact_score >= 6):
    hidden_gem = True
```
All three conditions must pass simultaneously. "Grassroots" confirms no institutional amplification. "Low cost" confirms accessibility. "Impact ≥ 6" confirms non-trivial value. Together they identify innovations that are effective, affordable, and invisible.

### ⚠️ Critical Flag
```python
if (risk_score >= 8) 
   and any(k in risk_types for k in ["fire", "chemical", "explosion", "energy", "toxic"]):
    critical_flag = True
```
The dual gate distinguishes acute hazards (chemical/explosive — could cause immediate mass harm) from severe structural or electrical risks. Both must be present to trigger an emergency intervention flag.

---

## 🗄️ Data Intelligence Model — Full Schema

Each innovation is stored as a JSON object with the following structure:

```json
{
  "id": "md5-hash-of-normalised-title-plus-country",
  "timestamp": "2026-03-23T10:00:00.000000",
  "title": "string — canonical English name",
  "summary": "string — 2–4 sentence plain-language description",
  "sources": ["https://direct-source-url.com"],

  "innovation_level": "grassroots | semi-formal | institutional",

  "category": ["Water & Sanitation", "Construction"],

  "location": {
    "country": "string",
    "region": "string",
    "lat": 0.0,
    "lon": 0.0
  },

  "process": {
    "how_it_works": "string",
    "materials_used": ["material_1", "material_2"],
    "step_by_step": ["step_1", "step_2", "step_3"]
  },

  "impact": {
    "problem_solved": "string",
    "scale": "low | medium | high"
  },

  "replicability": {
    "cost_level": "low | medium | high",
    "difficulty": "easy | medium | hard"
  },

  "origin": {
    "knowledge_source": ["traditional", "self-taught", "internet", "adapted", "formal"]
  },

  "risk_assessment": {
    "risk_score": 4,
    "risk_type": ["fire_hazard", "structural"],
    "safety_level": "medium",
    "needs_intervention": false,
    "explanation": "string"
  },

  "priority_score": 72,
  "hidden_gem": false,
  "critical_flag": false
}
```

### Field Reference

| Field | Type | Description |
|---|---|---|
| `id` | string | MD5 hash of `normalize(title) + "-" + country`. Deduplication key. |
| `timestamp` | ISO 8601 | UTC datetime when entry was added to the database. |
| `innovation_level` | enum | `grassroots` / `semi-formal` / `institutional` |
| `category[]` | string[] | Multi-label thematic tags. Used for network graph edges and chart aggregation. |
| `impact.scale` | enum | `low` (household) / `medium` (village cluster) / `high` (community/regional) |
| `replicability.cost_level` | enum | `low` (<$20) / `medium` ($20–200) / `high` (>$200) |
| `replicability.difficulty` | enum | `easy` (no tools/skills) / `medium` (basic craft) / `hard` (specialist knowledge) |
| `risk_score` | int 1–10 | Inherent hazard. Conservative: when in doubt, score higher. |
| `needs_intervention` | bool | True if risk ≥ 6 AND no documented safety protocols. |
| `priority_score` | int 0–100 | PSE Index. See formula above. |
| `hidden_gem` | bool | Grassroots + low cost + impact ≥ 6. |
| `critical_flag` | bool | Risk ≥ 8 + chemical/explosive hazard keywords detected. |

---

## 🕐 Schedule & Automation

The system runs entirely via **GitHub Actions**. No server required.

| Job | Trigger | Default Interval | Env Variable |
|---|---|---|---|
| Data Crawl | Scheduled cron | Every 2 days | `DATA_INTERVAL_DAYS` |
| Resume / Synthesis | Scheduled cron | Every 90 days | `RESUME_INTERVAL_DAYS` |
| Items per crawl | — | 3 innovations max | `MAX_ITEMS_PER_RUN` |
| Force data only | Manual trigger | — | `RUN_TYPE=force_data` |
| Force report only | Manual trigger | — | `RUN_TYPE=force_resume` |
| Force both | Manual trigger | — | `RUN_TYPE=force_both` |

The scraper checks timestamps in `history.json` before running. If the scheduled interval has not elapsed, it exits without making any API calls (zero cost, zero noise).

The **quarterly synthesis** re-analyses the entire `data.json` contents with Gemini to produce a structured intelligence report covering: executive summary, category trends, geographic clusters, risk patterns, innovation themes, hidden gems, intervention opportunities, knowledge lineage insights, and 5–8 actionable recommendations.

---

## 📁 Project Structure

```
gsi-radar/
│
├── scraper.py                          # Core AI pipeline (all 5 layers)
│
├── data.json                           # Append-only innovation database
├── resume.json                         # Quarterly intelligence reports (rotated)
├── history.json                        # Timestamps for schedule management
├── report.md                           # Auto-generated Markdown preview of latest report
│
├── dashboard_plus_map_prototype.html   # Radar Dashboard (analyst interface)
├── journal_copy.html                   # GII Bulletin (academic journal interface)
│
├── .github/
│   └── workflows/
│       └── radar.yml                   # GitHub Actions automation config
│
└── README.md
```

---

## 🚀 Setup & Deployment

### Prerequisites

- Python 3.9+
- A [Google AI Studio](https://aistudio.google.com) API key (free tier sufficient)
- A GitHub repository with GitHub Pages enabled

### 1. Fork or Clone

```bash
git clone https://github.com/your-username/gsi-radar.git
cd gsi-radar
```

### 2. Install Dependencies

```bash
pip install requests
```

The scraper uses only `requests` and Python standard library modules (`os`, `json`, `logging`, `random`, `hashlib`, `time`, `unicodedata`, `datetime`).

### 3. Set GitHub Secrets

In your repository: **Settings → Secrets and variables → Actions → New repository secret**

| Secret Name | Value |
|---|---|
| `GEMINI_API_KEY` | Your Google AI Studio API key |

### 4. Enable GitHub Actions

Ensure your `.github/workflows/radar.yml` is committed. The workflow will:
1. Run on schedule (every 2 days for data, every 90 days for reports)
2. Execute `scraper.py`
3. Commit updated `data.json` / `resume.json` back to the repository
4. GitHub Pages auto-deploys the updated dashboards

### 5. Enable GitHub Pages

In your repository: **Settings → Pages → Source: Deploy from branch → `main` → `/ (root)`**

Your dashboards will be live at `https://your-username.github.io/gsi-radar/`

### 6. First Run

To populate the database immediately without waiting for the schedule:

```bash
# Locally
export GEMINI_API_KEY="your-key-here"
export RUN_TYPE="force_both"
python scraper.py
```

Or trigger manually via GitHub Actions: **Actions → [workflow name] → Run workflow → `RUN_TYPE=force_both`**

---

## ⚙️ Environment Variables

All variables have safe defaults and can be set as GitHub Actions environment variables or local shell exports.

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | *(required)* | Google AI Studio API key. No default — scraper exits if missing. |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model name. Update here without touching code when new models release. |
| `RUN_TYPE` | `auto` | Execution mode: `auto` / `force_data` / `force_resume` / `force_both` |
| `DATA_INTERVAL_DAYS` | `2` | Days between data crawl runs in auto mode. |
| `RESUME_INTERVAL_DAYS` | `90` | Days between synthesis report runs in auto mode. |
| `MAX_ITEMS_PER_RUN` | `3` | Maximum new innovations added per crawl run. |

---

## 🎯 Use Cases

### 🏛️ Governments & Policy Bodies
- Identify local innovations at scale without deploying field teams
- Detect and monitor unsafe practices *before* they cause casualties
- Map innovation deserts — regions where documented solutions are sparse

### 🌍 Donors & NGOs
- Find high-impact + high-risk cases needing urgent expert intervention
- Discover low-cost, high-replicability solutions ready for programme integration
- Prioritise funding using an objective, formula-based index rather than anecdote

### 🔬 Researchers & Academics
- Study innovation diffusion across knowledge lineage types
- Analyse which platforms (YouTube, forums, NGO reports) are most effective for grassroots tech transfer
- Generate longitudinal datasets of community-level innovation across regions

### 🏗️ Development Engineers
- Find field-validated materials lists and step-by-step process descriptions
- Identify appropriate-technology candidates for adaptation to new contexts
- Benchmark local solutions against international equivalents

---

## ⚠️ Limitations & Known Blind Spots

| Limitation | Description | Planned Mitigation |
|---|---|---|
| **Digital Shadow** | Communities with no internet presence are invisible to web-crawling. The most marginalised populations this radar aims to serve are systematically underrepresented. | Field partner data submission portal; NGO direct pipeline |
| **Semantic Duplicate Gap** | Same practice under two names (e.g. "SODIS" vs "Solar Water Disinfection") = two entries. SHA/MD5 only catches title-level duplicates. | Embedding-based cosine similarity deduplication (L1.5) |
| **AI Score Variance** | Impact (I) and Replicability (R) scores are assigned by Gemini using a rubric, but rubric application is not perfectly consistent across runs. | Few-shot anchoring in prompts; confidence intervals in PSE |
| **Geocoding Errors** | Nominatim resolves country names to coordinates. Ambiguous names ("Congo", "Korea") may resolve incorrectly. Rural village names often return null. | Country-level fallback coordinates; user-submitted corrections |
| **English Language Bias** | All 60 keywords are written in English. Innovations documented only in Swahili, Bengali, Tagalog, or other languages are underrepresented. | Multilingual keyword sets; Gemini's multilingual extraction for non-English sources |
| **Temporal Latency** | 2-day interval means rapid-onset events (disaster response innovations) may not be indexed for weeks. | Webhook-triggered emergency crawls; `force_data` manual override |
| **3 items/run ceiling** | `MAX_ITEMS_PER_RUN=3` is conservative by design (API cost control). Database grows slowly. | Adjustable via env var; separate high-volume crawl job planned |

---

## 🗺️ Roadmap

- [ ] **Multilingual keyword library** — Swahili, Bengali, Tagalog, Arabic, Portuguese
- [ ] **Embedding-based deduplication** — cosine similarity on title vectors to catch semantic duplicates
- [ ] **Field partner submission API** — allow NGOs and researchers to submit innovations directly
- [ ] **PSE confidence intervals** — quantify scoring uncertainty from AI rubric variance
- [ ] **Time-series trend tracking** — compare innovation output across quarters by region/domain
- [ ] **Intervention tracking** — mark when a flagged innovation has received expert safety review
- [ ] **Webhook crawl trigger** — emergency crawl via external HTTP event (e.g. disaster response alert)
- [ ] **OAI-PMH metadata endpoint** — standard protocol for institutional repository harvesting

---

## ⚖️ Disclaimer

This tool is intended for **research, innovation mapping, and risk awareness purposes only**.

All data is sourced from publicly available information and structured using AI. Source URLs are preserved for verification.

Some innovations detected by this system involve **unsafe, experimental, or potentially dangerous practices**. GSI Radar does not endorse their replication. Flagged innovations are documented specifically to support:

- **Awareness** — so communities and practitioners know the risks
- **Analysis** — so researchers can understand the landscape of informal experimentation
- **Intervention** — so experts can reach high-risk innovations before harm occurs

Priority scores and risk assessments are AI-generated heuristics, not certified safety evaluations. Always consult qualified professionals before replicating any innovation flagged as high-risk.

---

## 📄 License

AGPL License — see [LICENSE](LICENSE) for full terms.

---

<div align="center">

**GSI Radar** · Built by [Angga Conni Saputra](mailto:conniezz.cool@gmail.com) · Jakarta, Indonesia

*An observatory of human ingenuity — where innovation is judged by relevance, impact, and context.*

</div>
