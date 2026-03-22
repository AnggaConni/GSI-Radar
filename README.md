# 🌏 ICH Shared Heritage Radar
### Global Intangible Cultural Heritage Intelligence Engine

> An AI-powered system that autonomously discovers, enriches, and maps living cultural heritage traditions from communities worldwide — including those not yet formally documented.

[![GitHub Actions](https://img.shields.io/badge/Automated-GitHub_Actions-2088FF?style=flat-square&logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Powered by Gemini](https://img.shields.io/badge/AI-Gemini_2.5_Flash-4285F4?style=flat-square&logo=google&logoColor=white)](https://aistudio.google.com)
[![Live on GitHub Pages](https://img.shields.io/badge/Dashboard-GitHub_Pages-222222?style=flat-square&logo=github&logoColor=white)](https://pages.github.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Data Updated](https://img.shields.io/badge/Data_Interval-Every_2_Days-00ffcc?style=flat-square)](#schedule)

---

## 📖 Table of Contents

- [What is ICH Radar?](#-what-is-ich-radar)
- [Live Demo](#-live-demo)
- [How It Works](#-how-it-works)
- [Architecture](#-architecture)
- [Data Schema](#-output-datajson)
- [Dashboard Features](#-dashboard-features)
- [Setup & Deployment](#-setup--deployment)
- [Configuration](#-configuration)
- [Adding Keywords](#-adding-more-keywords)
- [Schedule & Automation](#-schedule--automation)
- [Tech Stack](#-tech-stack)
- [Purpose & Alignment](#-purpose--alignment)
- [Disclaimer](#️-disclaimer)

---

## 🔍 What is ICH Radar?

**Intangible Cultural Heritage (ICH)** encompasses the living traditions, expressions, knowledge, and practices that communities recognize as part of their cultural identity — including oral traditions, performing arts, traditional craftsmanship, social rituals, and culinary heritage.

ICH Radar is an automated intelligence engine that **continuously discovers and documents these practices from open online sources**, including:

- Local community blogs and village websites
- Regional news archives
- Wikipedia and Wikimedia Commons
- Social media and cultural forums
- Academic and institutional repositories

Unlike static databases that rely on formal institutional submissions, ICH Radar actively **hunts for undocumented and at-risk traditions** — practices that communities still live by but that have never appeared in any official heritage inventory.

### What makes it different?

| Traditional Databases | ICH Radar |
|---|---|
| Requires formal nomination | Autonomous discovery |
| Only registered UNESCO elements | Includes unregistered local traditions |
| Updated manually | Updated automatically every 2 days |
| English-only sources | 40+ language keyword database |
| Static records | AI-enriched with steps, materials, connections |
| No cross-cultural linking | Shared heritage detection across regions |

---

## 🌐 Live Demo

The interactive dashboard is deployed on **GitHub Pages** and updates automatically with every crawler run.

**→ [View Live Dashboard](https://your-username.github.io/ich-radar)**

The dashboard includes:
- An interactive world map with pulsing heritage nodes and animated shared-heritage connection lines
- Filterable directory of all discovered elements
- Full AI-enriched detail view per element including step-by-step processes
- Dublin Core XML export for archival use
- Print-to-PDF export per element

---

## ⚙️ How It Works

The system operates in **two automatic phases** per scheduled run:

### Phase 0 — Data Audit
Before doing anything new, the engine scans existing records for data quality issues — specifically missing or broken thumbnail images. Any `COMPLETE` record with an invalid image is downgraded to `INCOMPLETE` and queued for re-enrichment.

### Phase 1 — Enrichment
The engine selects up to **3 incomplete records** from the previous run and re-queries Gemini with a targeted prompt to find the missing data — a step-by-step crafting process, a recipe, or a valid source URL with an image. If the missing data is found, the record is upgraded to `COMPLETE`.

### Phase 2 — Discovery
The engine randomly selects keywords from a multilingual database of 200+ search patterns and instructs Gemini to discover **2–4 brand-new heritage elements** not already in the inventory. Each new element is geocoded, assigned a thumbnail, and stored.

```
Scheduled Trigger (every 2 days)
         │
         ▼
   Phase 0: Audit
   Scan for broken images → downgrade to INCOMPLETE
         │
         ▼
   Phase 1: Enrichment
   Fix up to 3 INCOMPLETE records → upgrade to COMPLETE
         │
         ▼
   Phase 2: Discovery
   Find 2–4 new heritage elements via multilingual keywords
         │
         ▼
   Geocode coordinates (Nominatim / OpenStreetMap)
   Fetch thumbnails (Microlink → Wikimedia fallback)
         │
         ▼
   Commit data.json to repository
         │
         ▼
   GitHub Pages re-deploys dashboard automatically
```

---

## 🏗️ Architecture

Unlike traditional web scrapers that crawl URLs directly and are often blocked by rate limits or bot detection, ICH Radar **delegates discovery to Google's infrastructure** via AI Search Grounding. Gemini queries the web on behalf of the system and returns structured results — reaching blogs, local archives, and regional news that conventional scrapers cannot access reliably.

```
GitHub Actions (Scheduled Automation)
        │
        ▼
   scraper.py (AI Discovery Engine)
        │
        ├──► Gemini 2.5 Flash + Google Search Grounding
        │      ├── Discovers cultural practices via multilingual keywords
        │      ├── Extracts structured heritage data (description, significance, process)
        │      ├── Detects shared heritage relationships across regions
        │      └── Assigns ICH categories and gemini_tags
        │
        ├──► OpenStreetMap Nominatim API
        │      └── Geocodes country/province names → lat/lng coordinates
        │
        ├──► Microlink.io API
        │      └── Generates screenshot thumbnails from source page URLs
        │
        ├──► Wikimedia Commons API (fallback)
        │      └── Fetches alternative thumbnails when Microlink fails
        │
        ▼
  data.json (ICH Inventory Database)
        │
        ▼
  Git Commit & Push (automated)
        │
        ▼
  GitHub Pages → Interactive Cultural Heritage Dashboard
```

---

## 📦 Output: `data.json`

The crawler produces and maintains a single `data.json` file that serves as the live database for the dashboard.

### Summary block

```json
{
  "summary": {
    "generated_at": "2026-03-13T02:43:12Z",
    "total_ich_elements": 248,
    "complete_records": 180,
    "incomplete_records": 68,
    "categories_breakdown": {
      "Culinary Traditions": 65,
      "Traditional Craftsmanship": 54,
      "Performing Arts": 42,
      "Oral Traditions": 36,
      "Social Practices & Rituals": 51
    }
  }
}
```

### Inventory record (full example)

```json
{
  "id": "ich-4b1f9c3a",
  "element_name": "Traditional Bamboo Fish Trap Weaving",
  "category": "Traditional Craftsmanship",
  "thumbnail_url": "https://...",
  "source_urls": ["https://en.wikipedia.org/wiki/..."],
  "scraped_at": "2026-03-13T02:43:12Z",
  "completion_status": "COMPLETE",

  "location": {
    "country": "Indonesia",
    "provinces": ["West Java"],
    "lat": -6.9147,
    "lng": 107.6098
  },

  "resume_analisa": {
    "description": "A traditional fishing trap weaving technique using bamboo strips practiced by rural fishing communities.",
    "cultural_significance": "Represents local ecological knowledge and sustainable fishing practices passed through generations.",
    "gemini_tags": ["bamboo", "fishing", "weaving"]
  },

  "resume_tata_cara": {
    "type": "crafting_process",
    "materials_and_tools": ["Bamboo", "Knife", "Binding fiber"],
    "step_by_step": [
      "Split bamboo into thin strips",
      "Weave circular base frame",
      "Construct funnel entrance",
      "Secure trap with binding fiber"
    ]
  },

  "shared_heritage_detection": {
    "is_shared": true,
    "confidence_score": 0.84,
    "related_elements": [
      {
        "country": "Vietnam",
        "element_name": "Traditional Bamboo Fish Trap",
        "relationship_reason": "Similar weaving structure used in river fishing communities across Southeast Asia."
      }
    ]
  }
}
```

### Field reference

| Field | Type | Description |
|---|---|---|
| `id` | `string` | MD5-based unique identifier (`ich-` prefix) |
| `element_name` | `string` | Name of the heritage element |
| `category` | `string` | ICH category (see below) |
| `thumbnail_url` | `string` | Image URL — Microlink screenshot, direct image, or Wikimedia fallback |
| `source_urls` | `string[]` | Direct URLs to source pages used by the AI |
| `scraped_at` | `ISO 8601` | Discovery timestamp |
| `completion_status` | `COMPLETE` \| `INCOMPLETE` | Whether step-by-step process data was found |
| `location.lat` / `.lng` | `float` | Geocoded coordinates via Nominatim |
| `resume_analisa` | `object` | AI-generated description, significance, and tags |
| `resume_tata_cara` | `object` \| `null` | Process/recipe/ritual steps and materials. `null` if not found |
| `shared_heritage_detection` | `object` | Cross-cultural connection analysis with confidence score |

### ICH Categories

The AI assigns each element to one of five standard UNESCO-aligned categories:

- `Culinary Traditions`
- `Traditional Craftsmanship`
- `Performing Arts`
- `Oral Traditions`
- `Social Practices & Rituals`

---

## 🖥️ Dashboard Features

The `index.html` dashboard is a fully self-contained single-file web application. It reads `data.json` at load time and requires no backend.

### Heritage Network Map
An interactive Leaflet.js map with a dark CartoDB base layer.

- **Green pulsing nodes** — origin locations of ICH elements. Badge shows count when multiple elements share a location.
- **Yellow nodes** — related heritage elements in other countries detected by the shared heritage AI.
- **Animated dashed lines** — visual connections between cultures with a shared heritage relationship.
- Markers cluster automatically at lower zoom levels to prevent overplotting.
- Map filters in real-time to match the active directory filters.

### Directory & Filters
- Filter by **country of origin**
- Filter by **completion status** (Complete / Incomplete / Shared Heritage only)
- Sort by **newest or oldest** discovery date
- Configurable **items per page** (9 / 18 / 36 / 72)
- Full **pagination** with smart ellipsis for large datasets

### Element Detail Modal
Clicking any card opens a full detail panel with:
- Cover image and mini-map showing the element and its shared heritage connections
- Cultural significance, description, and AI tags
- Tools/materials list and numbered step-by-step process
- Shared heritage panel with confidence score and relationship reasons
- YouTube video carousel (auto-detected from source URLs)
- Direct links to all source pages

### Export: PDF
The printer icon inside any detail modal opens a **print-ready document in a new tab** containing the full record, a static light-mode map, YouTube thumbnails, and all sources. The browser print dialog opens automatically after ~1.5 seconds to allow map tile rendering.

> **Note on popup blockers:** The PDF export opens a new browser tab. If nothing happens when you click the printer icon, your browser's popup blocker is preventing it. Look for the blocked popup icon in your address bar and allow popups for this site, then click the icon again.

### Export: Dublin Core XML
The **Export XML** button in the header downloads the full inventory as an **OAI-DC (Dublin Core) XML** file — a standard metadata format compatible with digital library systems (DSpace, Omeka, Fedora), OAI-PMH harvesters, and academic citation tools.

### Language Toggle
The interface supports **English** and **Bahasa Indonesia**, switchable at any time without losing filter or pagination state.

---

## 🚀 Setup & Deployment

### Prerequisites
- A GitHub account
- A free Google Gemini API key from [aistudio.google.com](https://aistudio.google.com)
- GitHub Pages enabled on your repository

### Step 1 — Fork or clone this repository

```bash
git clone https://github.com/your-username/ich-radar.git
cd ich-radar
```

### Step 2 — Add your Gemini API key as a repository secret

Go to your repository → **Settings → Secrets and variables → Actions → New repository secret**:

| Secret name | Value |
|---|---|
| `GEMINI_API_KEY` | Your Google Gemini API key |

### Step 3 — Verify file structure

```
your-repo/
├── .github/
│   └── workflows/
│       └── crawler.yml       # GitHub Actions workflow definition
├── scraper.py                # AI Discovery Engine (main crawler)
├── index.html                # Dashboard UI (self-contained)
├── data.json                 # Auto-generated inventory (committed by bot)
├── history.json              # Crawl state tracker (committed by bot)
└── README.md
```

### Step 4 — Enable GitHub Pages

Go to **Settings → Pages → Source** and set it to **Deploy from a branch**, selecting the `main` branch and `/ (root)` folder. Your dashboard will be live at `https://your-username.github.io/ich-radar`.

### Step 5 — Run your first crawl

Go to **Actions → ICH Radar Auto-Crawler → Run workflow**.

Set `Force crawl now` to `true` to bypass the 2-day guard and run immediately. This will populate `data.json` for the first time and commit it to your repository, which will trigger a GitHub Pages redeploy.

---

## 🔧 Configuration

Key constants in `scraper.py`:

| Variable | Default | Description |
|---|---|---|
| `CRAWL_INTERVAL_DAYS` | `2` | Minimum days between automatic crawler runs |
| `max_discoveries_per_run` | `3` | Number of new elements to discover per run |
| `incomplete_items[:3]` | `3` | Maximum incomplete records to enrich per run |

To increase discovery throughput, raise `max_discoveries_per_run`. Keep in mind that each discovery requires one Gemini API call, and the free tier has daily quota limits.

### GitHub Actions workflow (`crawler.yml`)

The workflow is scheduled via cron. The default runs every 2 days at 02:00 UTC:

```yaml
on:
  schedule:
    - cron: '0 2 */2 * *'
  workflow_dispatch:
    inputs:
      force_run:
        description: 'Force crawl now'
        required: false
        default: 'false'
```

---

Understanding the Workflow Design:
Cron Schedule Breakdown (0 0 */2 * *): * 0 ➔ Minute 0

0 ➔ Hour 0 (Midnight UTC)

*/2 ➔ Every 2 days

* ➔ Every month

* ➔ Every day of the week

Manual Trigger (workflow_dispatch): Allows you to manually trigger the scraper at any time directly from the GitHub Actions UI.

Infinite Loop Protection ([skip ci]): The [skip ci] tag acts as a crucial safeguard during the automated git commit, preventing the bot from triggering subsequent workflow runs infinitely.

## 🔑 Adding More Keywords

The discovery engine uses a rotating multilingual keyword database. Each run, a keyword is selected at random to seed a new Gemini search query. Add your own targeted patterns to `KEYWORDS` in `scraper.py`:

```python
KEYWORDS = [
    # English — general
    "unregistered local heritage traditions",
    "forgotten village traditions",
    "traditional food preparation ancestral recipe",

    # Indonesian / Malay
    "tradisi lokal masyarakat adat kampung",
    "ritual adat lokal yang hampir punah",

    # Spanish — Latin America
    "prácticas culturales comunitarias no registradas",
    "rituales tradicionales de comunidades indígenas",

    # Add your own patterns below:
    # "your keyword in any language",
]
```

The current database spans **40+ languages** including Arabic, Chinese (Simplified and Traditional), Japanese, Korean, Hindi, Swahili, Yoruba, Amharic, Vietnamese, Thai, Tagalog, and many more. The multilingual coverage is intentional — many undocumented traditions are only discussed in their local language online.

---

## 📅 Schedule & Automation

The crawler is managed entirely by GitHub Actions at no cost within the free tier limits.

| Event | Behaviour |
|---|---|
| Scheduled (every 2 days) | Full audit → enrichment → discovery run |
| Manual trigger (`workflow_dispatch`) | Same run, with optional force flag to bypass the 2-day guard |
| Push to `main` | Does **not** trigger a crawl (guard prevents redundant runs) |

The 2-day guard is implemented in `scraper.py` by reading the `generated_at` timestamp from the last `data.json` and comparing it to the current time. This prevents unnecessary API usage if the workflow is triggered by other repository events.

To change the crawl interval:
1. Edit `CRAWL_INTERVAL_DAYS` in `scraper.py`
2. Update the cron expression in `crawler.yml` to match

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| AI Discovery | Google Gemini 2.5 Flash (Search Grounding) |
| Geocoding | OpenStreetMap Nominatim API |
| Thumbnails | Microlink.io API + Wikimedia Commons fallback |
| Automation | GitHub Actions |
| Dashboard | Vanilla HTML/JS + Leaflet.js + Tailwind CSS |
| Map tiles | CartoDB Dark Matter (via Leaflet) |
| Marker clustering | Leaflet.markercluster |
| Icons | Phosphor Icons |
| Hosting | GitHub Pages |
| Data format | JSON (inventory) + OAI-DC XML (export) |

---

## 🎯 Purpose & Alignment

ICH Radar aims to support:

- **Cultural heritage research** — structured, machine-readable records of living traditions
- **Early detection of endangered practices** — finding traditions before they disappear from online sources entirely
- **Shared heritage mapping** — identifying cross-regional cultural relationships that formal institutions often miss
- **Digital documentation** — creating reusable records compatible with archival standards

The system focuses especially on **locally practised traditions not present in official inventories** — the gap between what communities actually practice and what institutions have formally documented.

This project aligns with the principles of the **UNESCO Convention for the Safeguarding of the Intangible Cultural Heritage (2003)**, particularly Article 13 (national measures for safeguarding) and Article 14 (education, awareness, and capacity-building).

---

## ⚖️ Disclaimer

This tool is intended solely for **cultural heritage research, documentation, and safeguarding support**. All data is sourced from publicly available online information. The AI enrichment layer summarises and structures existing public knowledge — it does not generate or fabricate cultural information.

Source URLs for every record are stored and displayed in the dashboard, allowing full traceability back to original sources.

Heritage communities and researchers who identify inaccuracies in any record are encouraged to open an issue or pull request.

**License: MIT**

---

<div align="center">

Built with ❤️ for the preservation of living human culture.

*"Culture is the widening of the mind and of the spirit."* — Jawaharlal Nehru

</div>
