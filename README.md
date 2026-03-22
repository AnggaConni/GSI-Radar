# 🌍 GSI Radar
### Grassroots Science & Innovation Intelligence Engine

> An AI-powered system that autonomously discovers, analyzes, and maps human innovation — from high-level institutional projects to undocumented grassroots solutions — including risk detection and intervention insights.

[![GitHub Actions](https://img.shields.io/badge/Automated-GitHub_Actions-2088FF?style=flat-square&logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Powered by Gemini](https://img.shields.io/badge/AI-Gemini_2.5_Flash-4285F4?style=flat-square&logo=google&logoColor=white)](https://aistudio.google.com)
[![Live on GitHub Pages](https://img.shields.io/badge/Dashboard-GitHub_Pages-222222?style=flat-square&logo=github&logoColor=white)](https://pages.github.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Data Updated](https://img.shields.io/badge/Data_Interval-Every_2_Days-00ffcc?style=flat-square)](#schedule)

---

## 🔍 What is GSI Radar?

**Grassroots Science & Innovation (GSI)** refers to practical problem-solving knowledge developed by individuals, communities, and institutions — often outside formal research systems.

GSI Radar is an automated intelligence engine that **continuously discovers, structures, and evaluates innovations across the full spectrum**, including:

- High-level institutional innovation programs
- NGO and pilot projects
- Community-led solutions
- DIY / low-cost / improvised technologies
- Traditional and hybrid knowledge systems

Unlike traditional innovation databases that prioritize validated or funded projects, GSI Radar actively **captures invisible innovation** — including solutions that are:

- Undocumented
- Informal
- Experimental
- Potentially risky

---

## ⚖️ What makes it different?

| Traditional Innovation Systems | GSI Radar |
|---|---|
| Focus on institutional innovation | Captures grassroots → institutional spectrum |
| Requires formal submission | Autonomous discovery |
| No risk visibility | Includes risk scoring (1–10) |
| Focus on success stories | Includes experimental & unsafe practices |
| No knowledge traceability | Tracks knowledge origin (traditional, internet, adapted) |
| Static datasets | Continuously evolving intelligence |

---

## 🌐 Core Intelligence Layers

GSI Radar does not just collect data — it builds **multi-layered intelligence**:

### 🌍 Innovation Spectrum
Classifies each record:
- `grassroots`
- `semi-formal`
- `institutional`

### ⚠️ Risk Intelligence (DRR-aligned)
Each innovation includes:
- Risk score (1–10)
- Risk type (fire, toxic, explosion, etc.)
- Intervention flag

👉 Example:
A village-built pyrolysis system → high impact, high risk → **priority for intervention**

### 🧠 Knowledge Lineage
Tracks how knowledge emerged:

- Traditional knowledge
- Self-taught / experimentation
- Internet-based learning
- Adaptation from existing systems
- Formal education

This enables analysis of:
> how innovation actually spreads in real life

---

## ⚙️ What It Discovers

The system actively scans for:

- “High innovation” (e.g. pilot projects, SDG initiatives)
- “Invisible innovation” (e.g. DIY tools, local practices)
- “Risk-prone innovation” (e.g. informal chemical, fuel, or energy systems)

Sources include:

- Local blogs & community pages  
- YouTube / social media  
- News archives  
- Academic & institutional repositories  

---

## 🧱 Data Intelligence Model (Core Fields)

Each discovered innovation is enriched into a structured record:

```json
{
  "id": "string",
  "title": "string",
  "summary": "string",

  "innovation_level": "grassroots | semi-formal | institutional",

  "location": {
    "country": "string",
    "region": "string",
    "lat": 0.0,
    "lon": 0.0
  },

  "origin": {
    "actor_type": "individual | community | NGO | government",
    "knowledge_source": [
      "traditional",
      "self-taught",
      "internet",
      "adapted",
      "formal"
    ]
  },

  "process": {
    "how_it_works": "string",
    "materials": [],
    "steps": []
  },

  "impact": {
    "problem_solved": "string",
    "scale": "household | village | regional | national"
  },

  "risk_assessment": {
    "risk_score": 1,
    "risk_type": ["fire", "toxic", "explosion"],
    "needs_intervention": true
  },

  "source": {
    "url": "string",
    "platform": "youtube | blog | report"
  }
}

```

# 🌱 Why It Matters

Most global systems — including those aligned with institutions like UNESCO — tend to highlight:

validated knowledge
funded innovation
formally recognized programs

But in reality:

innovation often starts in places that are never documented

## GSI Radar focuses on:

Science from below
Innovation before validation
Risk before disaster
Potential before recognition

## 🎯 Use Cases
🏛️ Governments
Identify local innovations without field deployment
Detect unsafe practices early
🌍 Donors & NGOs
Find high-impact + high-risk cases needing intervention
Discover scalable low-cost solutions
🔬 Researchers
Study innovation diffusion
Analyze knowledge transfer patterns
🌌 Vision

GSI Radar aims to become a global observatory of human ingenuity —
where innovation is not judged by visibility, but by:

relevance
impact
and context

# ⚖️ Disclaimer

This tool is intended for research, innovation mapping, and risk awareness.
All data is sourced from publicly available information and structured using AI.

Some detected innovations may involve unsafe or experimental practices.
The platform does not endorse their use and highlights them to support:

awareness
analysis
and potential intervention

<div align="center">

Built for those who innovate quietly — before the world notices.

</div>
