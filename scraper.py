"""
=======================================================================
  INNOVATION RADAR v1.3 — Global Intelligence Engine
  AI Engine : Google Gemini 2.5 Flash
  Mode      : Multi-Schedule Tracker (Data = 2 Days, Resume = 3 Months)
  Feature   : Append-Only DB, Smart Execution, Independent Force Crawl
  Updated   : + Retry Logic, + Env Config, + Title Normalization,
              + Expanded Keywords
=======================================================================
"""

import os
import json
import logging
import random
import hashlib
import time
import unicodedata                         # ✅ NEW: for title normalization
from datetime import datetime, timedelta
import requests

# ── Logging Configuration ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger("InnovationRadar")

# ── File Paths ──
BASE_DIR         = os.path.dirname(os.path.abspath(__file__))
DATA_FILE        = os.path.join(BASE_DIR, "data.json")
RESUME_FILE      = os.path.join(BASE_DIR, "resume.json")
HISTORY_FILE     = os.path.join(BASE_DIR, "history.json")
REPORT_MD_FILE   = os.path.join(BASE_DIR, "report.md")
PATHWAY_FILE      = os.path.join(BASE_DIR, "pathways.json")

# ✅ NEW: Configurable schedule intervals via environment variables.
# You can set these in your system/CI without touching the code.
# Defaults: data every 2 days, resume every 90 days, max 3 items per run.
DATA_INTERVAL_DAYS   = int(os.environ.get("DATA_INTERVAL_DAYS", 2))
RESUME_INTERVAL_DAYS = int(os.environ.get("RESUME_INTERVAL_DAYS", 90))
MAX_ITEMS_PER_RUN    = int(os.environ.get("MAX_ITEMS_PER_RUN", 3))

# ── Keywords for Search Grounding ──
# ✅ EXPANDED: From 7 → 60 keywords across 10 thematic categories
KEYWORDS = [

    # --- Agriculture & Food Security ---
    "grassroots innovation developing country",
    "DIY farming tools self-taught farmer",
    "improvised irrigation system smallholder",
    "low cost drip irrigation rural farmer",
    "homemade pesticide organic village",
    "traditional seed preservation technique",
    "community grain storage innovation Africa",
    "fish farming backyard low cost method",
    "vertical garden urban poor neighborhood",
    "soil improvement technique indigenous farmer",
    "DIY greenhouse plastic bottle rural",
    "hand-powered thresher local invention",

    # --- Water & Sanitation ---
    "improvised water filter rural village",
    "homemade biosand water filter community",
    "rainwater harvesting DIY rooftop system",
    "clay pot water purification traditional",
    "low cost latrine sanitation rural innovation",
    "solar water disinfection SODIS village",
    "community-built well innovation developing world",
    "greywater recycling homemade system",

    # --- Energy & Electricity ---
    "homemade energy generator rural village",
    "DIY micro hydro turbine local inventor",
    "homemade biogas digester cow dung",
    "improvised solar panel cheap rural electrification",
    "wind turbine scrap metal village maker",
    "charcoal briquette homemade waste",
    "rocket stove low cost fuel efficient cooking",
    "pedal powered electricity generator community",

    # --- Health & Medicine ---
    "low cost medical device rural clinic innovation",
    "traditional herbal remedy documented local knowledge",
    "improvised stretcher ambulance rural community",
    "homemade incubator premature baby low income",
    "DIY wheelchair developing country local materials",
    "community health innovation grassroots Africa Asia",
    "low cost prosthetic limb local maker",
    "village midwife tool improvised birth kit",

    # --- Construction & Shelter ---
    "low cost housing innovation local material",
    "earthbag construction community self-built",
    "bamboo reinforced concrete rural building",
    "plastic bottle brick house slum innovation",
    "rammed earth construction self-taught builder",
    "DIY composting toilet rural sanitation",
    "recycled material roof waterproofing village",

    # --- Education & Communication ---
    "local community tech adaptation",
    "offline education tool rural school DIY",
    "repurposed device learning tool developing country",
    "community radio homemade transmitter village",
    "DIY projector school rural innovation",
    "solar powered tablet charging station village",

    # --- Tools & Manufacturing ---
    "traditional knowledge modified modern tools",
    "blacksmith innovation local tool adaptation Africa",
    "repurposed engine machine local inventor",
    "scrap metal workshop village innovation",
    "3D printing low cost prosthetic developing country",
    "local foundry casting innovation informal sector",

    # --- Environment & Waste ---
    "slum innovation low cost solution recycling",
    "plastic waste upcycling community enterprise",
    "informal waste picker innovation tool",
    "homemade oil press seed local village",
    "community composting system urban poor",
    "river cleanup tool homemade community",

    # --- Transportation & Mobility ---
    "improvised transport solution rural community",
    "cargo bicycle modification local welder",
    "low cost boat motor adaptation fisher community",
    "donkey cart innovation rural logistics",

    # --- Finance & Social Innovation ---
    "community savings innovation rotating fund village",
    "local barter system informal economy adaptation",
    "grassroots cooperative innovation developing world",
    "mobile money workaround rural community unbanked",
]

# =====================================================================
# HELPER FUNCTIONS
# =====================================================================

def load_json_file(filepath, default_val):
    if not os.path.exists(filepath):
        return default_val
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log.error(f"Error loading {filepath}: {e}")
        return default_val

def save_json_file(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def save_text_file(filepath, text):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)

def extract_json_safe(text):
    try:
        text = text.strip()
        tick3 = '`' * 3
        if text.startswith(tick3 + 'json'): text = text[7:]
        if text.startswith(tick3): text = text[3:]
        if text.endswith(tick3): text = text[:-3]
        text = text.strip()
        start_idx = text.find('{') if '{' in text else text.find('[')
        end_idx = text.rfind('}') if '}' in text else text.rfind(']')
        if start_idx != -1 and end_idx != -1:
            return json.loads(text[start_idx:end_idx+1])
        return json.loads(text)
    except Exception as e:
        log.error(f"JSON Parse Error: {e}")
        return None

# ✅ NEW: Normalize title text before hashing.
# This prevents duplicates caused by different capitalizations
# or Unicode quirks (e.g., "café" vs "cafe", "DIY Tool" vs "diy tool").
def normalize_title(title):
    """Lowercase + strip + Unicode normalize a title for consistent hashing."""
    return unicodedata.normalize("NFKC", title).strip().lower()

def get_coordinates(location_name):
    if not location_name or str(location_name).lower() == "unknown":
        return None, None
    url = f"https://nominatim.openstreetmap.org/search?q={location_name}&format=json&limit=1"
    headers = {"User-Agent": "InnovationRadarApp/9.1 (research-bot)"}
    try:
        time.sleep(1.5)
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        log.warning(f"Geocoding failed for {location_name}: {e}")
    return None, None

def get_current_quarter():
    now = datetime.now()
    quarter = (now.month - 1) // 3 + 1
    return f"Q{quarter} {now.year}"

# =====================================================================
# CORE AI ENGINE (GEMINI)
# =====================================================================

def call_gemini(api_key, prompt, system_instruction, use_search=False, expect_json=True):
    # Pastikan prompt adalah string. Jika berupa objek/dict, ubah jadi teks JSON.
    if not isinstance(prompt, str):
        prompt = json.dumps(prompt)
        
    # --- KODE BARU (Penerapan No. 6) ---
    # Mengambil nama model dari Environment Variable, default-nya tetap pakai 3-flash-preview
    # Jika besok Google rilis gemini-4, Anda tinggal set env var GEMINI_MODEL="gemini-4"
    model_name = os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
    
    # Konfigurasi payload
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "generationConfig": {
            "temperature": 0.5,
            "maxOutputTokens": 8192,
            # Menghasilkan output dalam format JSON jika diminta
            "responseMimeType": "application/json" if expect_json else "text/plain"
        }
    }
    
    if expect_json and not use_search:
        payload["generationConfig"]["responseMimeType"] = "application/json"
        
    if use_search:
        # --- KODE YANG DIPERBAIKI ---
        # Mengikuti format API terbaru Google
        payload["tools"] = [{"googleSearch": {}}]
        # ----------------------------
        
    headers = {
        'Content-Type': 'application/json',
        'x-goog-api-key': api_key
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        data = response.json()
        raw_text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        
        if expect_json:
            return extract_json_safe(raw_text)
        return raw_text
    except Exception as e:
        error_details = e.response.text if hasattr(e, 'response') and e.response is not None else str(e)
        log.error(f"Gemini API Error: {error_details}")
        return None

# ✅ NEW: Retry wrapper around call_gemini.
# If Gemini fails (network glitch, timeout, empty response),
# it will automatically try again up to `retries` times.
# Each retry waits longer: 1s, 2s, 4s (exponential backoff).
def call_gemini_with_retry(api_key, prompt, system_instruction, retries=3, **kwargs):
    for attempt in range(retries):
        try:
            result = call_gemini(api_key, prompt, system_instruction, **kwargs)
            if result:
                return result
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            if status_code in [400, 403, 404]: # Error fatal yang tidak akan sembuh dengan retry
                log.error(f"Fatal HTTP Error {status_code}. Aborting retry.")
                break
            elif status_code == 429: # Too many requests
                log.warning("Rate limit hit. Retrying...")
                
        wait_time = 2 ** attempt
        log.warning(f"Gemini call failed (attempt {attempt + 1}/{retries}). Retrying in {wait_time}s...")
        time.sleep(wait_time)
        
    return None

# =====================================================================
# 5-LAYER PIPELINE (DISCOVERY)
# ✅ All pass_* functions now use call_gemini_with_retry instead of call_gemini
# =====================================================================

def pass_1_validate(api_key, raw_content):
    sys_prompt = """Determine whether the following content represents a real-world grassroots or local innovation. Criteria: Must solve a clear problem, involve a tangible method/tool. Return exactly: {"is_innovation": true/false, "confidence": 0.0-1.0}"""
    res = call_gemini_with_retry(api_key, raw_content, sys_prompt)   # ✅ changed
    return res if res else {"is_innovation": False, "confidence": 0}

def pass_2_extract(api_key, raw_content):
    # Kita tambahkan instruksi "DIRECT, ORIGINAL links"
    sys_prompt = """Extract structured data about this innovation. 
    IMPORTANT: For 'sources', provide only DIRECT, ORIGINAL website links (e.g., youtube.com, bbc.com) and NOT the google search grounding redirect links.
    Return EXACTLY this JSON structure:
{"title": "", "sources": [], "summary": "", "category": [], "innovation_level": "grassroots | semi-formal | institutional", "location": {"country": "", "region": ""}, "process": {"how_it_works": "", "materials_used": [], "step_by_step": []}, "impact": {"problem_solved": "", "scale": "low | medium | high"}, "replicability": {"cost_level": "low | medium | high", "difficulty": "easy | medium | hard"}}"""
    return call_gemini_with_retry(api_key, raw_content, sys_prompt)   # ✅ changed

def pass_3_risk(api_key, raw_content):
    sys_prompt = """Analyze the innovation and assess potential risks (fire hazard, explosion, toxic, environment, safety gear). Rules: Be conservative. Grassroots + chemical/energy -> higher risk. Return EXACTLY this JSON:
{"risk_score": <int 1-10>, "risk_type": ["type1"], "safety_level": "low|medium|high", "needs_intervention": true/false, "explanation": ""}"""
    return call_gemini_with_retry(api_key, raw_content, sys_prompt)   # ✅ changed

def pass_4_lineage(api_key, raw_content):
    sys_prompt = """Determine the origin of knowledge behind this innovation. Options: [traditional, self-taught, internet, adapted_from_existing, formal_education]. Return EXACTLY this JSON: {"knowledge_source": ["source1"]}"""
    return call_gemini_with_retry(api_key, raw_content, sys_prompt)   # ✅ changed

def calculate_advanced_metrics(data):
    try:
        impact_map = {"high": 10, "medium": 6, "low": 2, "unknown": 0}
        repl_map = {"easy": 10, "medium": 5, "hard": 2, "unknown": 0}
        impact_val = impact_map.get(str(data.get("impact", {}).get("scale", "")).lower(), 0)
        repl_val = repl_map.get(str(data.get("replicability", {}).get("difficulty", "")).lower(), 0)
        risk_val = data.get("risk_assessment", {}).get("risk_score", 1)

        priority_score = int(((impact_val * 0.4) + (risk_val * 0.4) + (repl_val * 0.2)) * 10)
        data["priority_score"] = min(100, max(0, priority_score))

        is_grassroots = data.get("innovation_level", "").lower() == "grassroots"
        is_low_cost = data.get("replicability", {}).get("cost_level", "").lower() == "low"
        data["hidden_gem"] = bool(is_grassroots and is_low_cost and impact_val >= 6)

        risk_types = [str(x).lower() for x in data.get("risk_assessment", {}).get("risk_type", [])]
        has_critical = any(k in t for t in risk_types for k in ["fire", "chemical", "explosion", "energy", "toxic"])
        data["critical_flag"] = bool(risk_val >= 8 and has_critical)
        return data
    except Exception:
        return data


# =====================================================================
# IMPLEMENTATION PATHWAY CLASSIFICATION
# =====================================================================

def normalize_pathway_text(value):
    return " ".join(
        unicodedata.normalize("NFKC", str(value or "")).lower()
        .replace("&", " and ")
        .split()
    )

def classify_pathway_record(item, taxonomy):
    """Map an innovation record onto one or more predefined pathway nodes."""
    matches = []
    domains = taxonomy.get("domains", {}) if isinstance(taxonomy, dict) else {}

    corpus = " ".join([
        str(item.get("title", "")),
        str(item.get("summary", "")),
        str(item.get("impact", {}).get("problem_solved", "")),
        str(item.get("process", {}).get("how_it_works", "")),
        " ".join(item.get("process", {}).get("step_by_step", []) or []),
        " ".join(item.get("process", {}).get("materials_used", []) or [])
    ])
    corpus_n = normalize_pathway_text(corpus)
    title_n = normalize_pathway_text(item.get("title", ""))

    category_values = [normalize_pathway_text(x) for x in (item.get("category", []) or [])]

    for domain_id, domain in domains.items():
        for node in domain.get("nodes", []) or []:
            aliases = [normalize_pathway_text(x) for x in (node.get("aliases", []) or [])]
            keywords = [normalize_pathway_text(x) for x in (node.get("keywords", []) or [])]
            score = 0.0
            exact = False
            evidence = []

            for alias in aliases:
                if any(c == alias or c in alias or alias in c for c in category_values):
                    score = max(score, 1.0)
                    exact = True
                    evidence.append("category")

            if any(alias and alias in title_n for alias in aliases):
                score = max(score, 0.76)
                evidence.append("title")

            if any(k and k in corpus_n for k in aliases + keywords):
                score = max(score, 0.68)
                evidence.append("narrative")

            if any(k and k in normalize_pathway_text(item.get("process", {}).get("how_it_works", "")) for k in keywords):
                score = max(score, 0.72)
                evidence.append("process")

            if score >= 0.58:
                matches.append({
                    "domain_id": domain_id,
                    "node_id": node.get("id"),
                    "match": "exact" if exact else "heuristic",
                    "confidence": round(min(1.0, score), 2),
                    "evidence": sorted(set(evidence))
                })

    matches.sort(key=lambda x: (-x["confidence"], x["node_id"]))
    return matches

def enrich_pathway_matches(database, taxonomy):
    changed = False
    for item in database:
        new_matches = classify_pathway_record(item, taxonomy)
        old_matches = item.get("pathway_matches", [])
        if old_matches != new_matches:
            item["pathway_matches"] = new_matches
            changed = True
    return changed



# =====================================================================
# POLICY / ACTION -> IMPLEMENTATION INTELLIGENCE
# =====================================================================

def _stakeholder_group_from_context(context):
    mapping = {
        "community": "Communities & local organizations",
        "community_group": "Communities & local organizations",
        "municipality": "Local authorities & public services",
        "government": "Public authorities & policymakers",
        "school": "Schools, educators & youth",
        "training_center": "Training & capacity-building actors",
        "small_enterprise": "SMEs & local enterprises",
        "small_enterprise": "SMEs & local enterprises",
        "farm": "Farmers & producer groups",
        "smallholder_farm": "Farmers & producer groups",
        "cooperative": "Cooperatives & producer organizations",
        "clinic": "Health practitioners & facilities",
        "rural_clinic": "Health practitioners & facilities",
        "household": "Households & end users",
        "rural_household": "Households & end users",
        "coastal": "Coastal communities & marine practitioners",
        "fishing_community": "Fishing communities & marine practitioners",
        "protected_area": "Conservation actors & site managers",
        "cultural_group": "Cultural practitioners & custodians",
        "cultural_institution": "Cultural institutions & custodians",
        "research_site": "Researchers & scientific institutions",
        "digital_platform": "Digital service providers & platforms",
        "maker_space": "Makers, fabricators & technical practitioners",
        "local_workshop": "Local workshops & technical practitioners",
        "emergency_response": "Emergency, humanitarian & response actors",
        "online_offline_hybrid": "Educators, communities & digital platforms"
    }
    return mapping.get(str(context).strip().lower(), None)


def build_implementation_intelligence(database, report, taxonomy):
    """Build a traceable bridge from observed innovation evidence to policy/action and implementation.

    AI may enrich this structure in the report, but the evidence counts and pathway coverage
    are derived from the database/taxonomy so they remain auditable.
    """
    domains = taxonomy.get("domains", {}) if isinstance(taxonomy, dict) else {}
    node_index = {}
    node_stats = {}

    for domain_id, domain in domains.items():
        for node in domain.get("nodes", []) or []:
            node_id = node.get("id")
            node_index[node_id] = (domain_id, domain, node)
            node_stats[node_id] = {
                "domain_id": domain_id,
                "domain": domain.get("label", domain_id),
                "node_id": node_id,
                "label": node.get("label", node_id),
                "observed": [],
                "inferred": [],
                "records": set()
            }

    evidence_total = {"observed": 0, "inferred": 0}
    innovation_records = []

    for item in database:
        matches = item.get("pathway_matches", []) or []
        pathway_nodes = []
        for match in matches:
            node_id = match.get("node_id")
            if node_id not in node_stats:
                continue
            st = node_stats[node_id]
            st["records"].add(item.get("id"))
            pathway_nodes.append({
                "domain_id": st["domain_id"],
                "domain": st["domain"],
                "node_id": node_id,
                "node": st["label"],
                "match": match.get("match", "heuristic"),
                "confidence": match.get("confidence", 0),
                "evidence": match.get("evidence", [])
            })
            if match.get("match") == "exact":
                st["observed"].append(item.get("id"))
                evidence_total["observed"] += 1
            else:
                st["inferred"].append(item.get("id"))
                evidence_total["inferred"] += 1

        if pathway_nodes:
            innovation_records.append({
                "id": item.get("id"),
                "title": item.get("title", "Untitled"),
                "country": item.get("location", {}).get("country", "Unknown"),
                "priority_score": item.get("priority_score", 0),
                "pathways": pathway_nodes
            })

    top_innovations = sorted(
        innovation_records,
        key=lambda x: (x.get("priority_score", 0), x.get("title", "")),
        reverse=True
    )[:12]

    pathway_coverage = []
    for domain_id, domain in domains.items():
        domain_nodes = []
        domain_records = set()
        for node in domain.get("nodes", []) or []:
            st = node_stats.get(node.get("id"), {})
            records = st.get("records", set())
            domain_records.update(records)
            domain_nodes.append({
                "node_id": node.get("id"),
                "node": node.get("label", node.get("id")),
                "stage": node.get("stage", ""),
                "observed": len(set(st.get("observed", []))),
                "inferred": len(set(st.get("inferred", []))),
                "mapped_records": len(records)
            })

        domain_nodes.sort(key=lambda x: (-x["mapped_records"], x["node"]))
        gaps = [x for x in domain_nodes if x["mapped_records"] == 0][:8]
        pathway_coverage.append({
            "domain_id": domain_id,
            "domain": domain.get("label", domain_id),
            "mapped_records": len(domain_records),
            "nodes_with_evidence": sum(1 for x in domain_nodes if x["mapped_records"] > 0),
            "total_nodes": len(domain_nodes),
            "top_nodes": domain_nodes[:8],
            "evidence_gaps": gaps
        })

    pathway_coverage.sort(key=lambda x: (-x["mapped_records"], x["domain"]))

    stakeholders = {}
    for domain in domains.values():
        for node in domain.get("nodes", []) or []:
            for context in node.get("implementation_contexts", []) or []:
                group = _stakeholder_group_from_context(context)
                if group:
                    stakeholders.setdefault(group, {"group": group, "contexts": set(), "pathways": set()})
                    stakeholders[group]["contexts"].add(context)
                    stakeholders[group]["pathways"].add(node.get("label", ""))

    stakeholder_rows = []
    for row in stakeholders.values():
        stakeholder_rows.append({
            "group": row["group"],
            "role": "Potential implementation, validation or feedback partner based on pathway context.",
            "contexts": sorted(row["contexts"]),
            "relevant_pathways": sorted([x for x in row["pathways"] if x])[:12]
        })
    stakeholder_rows.sort(key=lambda x: x["group"])

    interventions = report.get("intervention_opportunities", []) or []
    policy_options = []
    for idx, option in enumerate(interventions, 1):
        ptype = option.get("type", "research")
        target = option.get("target", "Unnamed opportunity")
        level = option.get("priority_level", "medium")
        linked = []
        target_text = normalize_pathway_text(" ".join([
            str(target),
            str(option.get("justification", ""))
        ]))
        for node_id, st in node_stats.items():
            node_text = normalize_pathway_text(st["label"])
            if node_text and (node_text in target_text or any(
                k in target_text for k in (
                    node_index[node_id][2].get("keywords", []) or []
                )
            )):
                linked.append({
                    "domain": st["domain"],
                    "node": st["label"],
                    "node_id": node_id
                })
        policy_options.append({
            "option_id": f"PO-{idx:02d}",
            "instrument": ptype,
            "option": target,
            "rationale": option.get("justification", ""),
            "priority_level": level,
            "linked_pathways": linked[:8],
            "status": "evidence-informed opportunity; requires contextual validation before adoption"
        })

    implementation_actions = []
    for option in policy_options:
        horizon = "short" if option["instrument"] in ("training", "data") else ("medium" if option["instrument"] in ("research", "funding", "partnership") else "medium-long")
        implementation_actions.append({
            "option_id": option["option_id"],
            "action": f"Pilot and validate: {option['option']}",
            "lead_stakeholders": [x["group"] for x in stakeholder_rows[:6]],
            "dependencies": [
                "local contextual validation",
                "risk and feasibility assessment",
                "implementation partner"
            ],
            "time_horizon": horizon,
            "success_indicators": [
                "documented implementation evidence",
                "validated risk controls",
                "user or practitioner feedback",
                "evidence of pathway progression"
            ]
        })

    feedback_loop = [
        {
            "indicator": "New or changed evidence mapped to a pathway node",
            "source": "GSI-Radar observation layer",
            "trigger": "new exact match or high-confidence inferred match",
            "response": "review pathway coverage and policy relevance"
        },
        {
            "indicator": "Implementation result or safety evidence",
            "source": "future implementation monitoring / linked evidence",
            "trigger": "pilot outcome, risk event or documented field result",
            "response": "update policy option, implementation guidance and pathway maturity"
        },
        {
            "indicator": "Persistent evidence gap",
            "source": "pathway coverage analysis",
            "trigger": "node remains unobserved across reporting cycles",
            "response": "consider targeted scanning, research or stakeholder outreach"
        }
    ]

    pipeline = [
        {"stage":"Innovation","description":"What innovations are being observed?","record_count":len(database),"basis":"data.json"},
        {"stage":"Evidence","description":"What is directly observed versus inferred?","observed_matches":evidence_total["observed"],"inferred_matches":evidence_total["inferred"],"basis":"pathway_matches + source records"},
        {"stage":"System Pathway","description":"Where does the innovation sit in a thematic system?","domains_mapped":sum(1 for x in pathway_coverage if x["mapped_records"] > 0),"basis":"pathways.json"},
        {"stage":"Policy Relevance","description":"Why might the evidence matter for public policy, planning or institutional action?","items":len(interventions),"basis":"AI synthesis + intervention opportunities"},
        {"stage":"Stakeholders","description":"Who may implement, validate, govern or provide feedback?","groups":len(stakeholder_rows),"basis":"pathway implementation contexts"},
        {"stage":"Policy Options","description":"What types of policy or support instruments could respond?","options":len(policy_options),"basis":"intervention opportunities"},
        {"stage":"Implementation","description":"What practical steps could translate an option into action?","actions":len(implementation_actions),"basis":"derived implementation scaffold; validate locally"},
        {"stage":"Feedback","description":"How does implementation evidence return to the intelligence cycle?","feedback_loops":len(feedback_loop),"basis":"monitoring and future evidence"}
    ]

    return {
        "schema_version": "1.0",
        "pipeline": pipeline,
        "innovation": {"top_records": top_innovations, "total_with_pathway_evidence": len(innovation_records)},
        "evidence": {"observed_matches": evidence_total["observed"], "inferred_matches": evidence_total["inferred"]},
        "system_pathways": pathway_coverage,
        "policy_relevance": [],
        "stakeholders": stakeholder_rows,
        "policy_options": policy_options,
        "implementation": implementation_actions,
        "feedback": feedback_loop
    }

# =====================================================================
# CORE TASKS: DATA CRAWL & RESUME GENERATION
# =====================================================================

def run_discovery_pipeline(api_key, database, max_items=3):
    """Mencari data baru dan menambahkannya ke database."""
    keyword = random.choice(KEYWORDS)
    log.info(f"Initiating radar ping with keyword: '{keyword}'")

    seed_prompt = f"Search the web for 5 distinct, real-world examples of: {keyword}. Provide a detailed paragraph for each, AND include a list of all relevant source URLs found. Return a JSON object with an array 'innovations' containing these descriptions and their associated URLs."
    seed_sys = "You are an OSINT web scraper. Use google search. IMPORTANT: Always return the direct, original source URLs. Return pure JSON."

    seed_data = call_gemini_with_retry(api_key, seed_prompt, seed_sys, use_search=True)
    if not seed_data or "innovations" not in seed_data:
        log.warning("No raw material found on this run.")
        return 0

    raw_descriptions = seed_data["innovations"]
    success_count = 0

    for idx, item in enumerate(raw_descriptions):
        if success_count >= max_items: break

        if isinstance(item, dict):
            raw_text = item.get("description", str(item))
            discovered_urls = item.get("urls", [])
        else:
            raw_text = str(item)
            discovered_urls = []

        validation = pass_1_validate(api_key, raw_text)
        if not validation.get("is_innovation") or validation.get("confidence", 0) < 0.6:
            continue

        base_data = pass_2_extract(api_key, raw_text)
        if not base_data or not base_data.get("title"):
            continue

        # --- KODE BARU (Penerapan No. 5) ---
        normalized_title = normalize_title(base_data["title"])
        country = base_data.get("location", {}).get("country", "unknown").lower()
        
        # Gabungkan title dan negara agar ID unik per lokasi
        unique_string = f"{normalized_title}-{country}"
        title_hash = hashlib.md5(unique_string.encode('utf-8')).hexdigest()
        # -----------------------------------

        if any(db_item.get("id") == title_hash for db_item in database):
            continue

        risk_data = pass_3_risk(api_key, raw_text)
        lineage_data = pass_4_lineage(api_key, raw_text)

        final_item = {
            "id": title_hash, 
            "timestamp": datetime.now().isoformat(),
            **base_data,
            "origin": lineage_data if lineage_data else {"knowledge_source": []},
            "risk_assessment": risk_data if risk_data else {}
        }

        if "sources" not in final_item: final_item["sources"] = []
        final_item["sources"] = list(set(final_item.get("sources", []) + discovered_urls))

        country = final_item.get("location", {}).get("country", "")
        region = final_item.get("location", {}).get("region", "")
        lat, lon = get_coordinates(f"{region}, {country}".strip(", "))
        final_item["location"]["lat"], final_item["location"]["lon"] = lat, lon

        final_item = calculate_advanced_metrics(final_item)
        taxonomy = load_json_file(PATHWAY_FILE, {"domains": {}})
        final_item["pathway_matches"] = classify_pathway_record(final_item, taxonomy)
        database.append(final_item)
        success_count += 1
        log.info(f"🔥 Processed: {final_item['title']}")

    return success_count
    
def generate_intelligence_report(api_key, database):
    """Membaca database dan menambahkan resume baru dengan rotasi ID."""
    if not database:
        log.warning("Database is empty. Skipping report generation.")
        return

    log.info("📊 Generating Periodic Intelligence Resume...")
    quarter = get_current_quarter()
    db_string = json.dumps(database, ensure_ascii=False)

    sys_prompt = """
                You are an elite AI Intelligence Analyst generating a quarterly global report on grassroots and institutional innovation.

                You will be given a JSON array containing structured innovation records.

                YOUR OBJECTIVE:
                - Detect patterns (not just summarize)
                - Identify risks and emerging threats
                - Highlight high-impact innovations
                - Identify intervention opportunities
                - Analyze knowledge evolution

                CRITICAL THINKING RULES:
                - Do NOT summarize blindly
                - Aggregate across multiple records
                - Identify trends, anomalies, and clusters
                - If data is insufficient, return empty arrays or zero values (DO NOT hallucinate)

                ----------------------------------------
                OUTPUT FORMAT (STRICT JSON ONLY)
                ----------------------------------------

                {
                "report_metadata": {
                    "report_id": "gsi-current",
                    "generated_at": "YYYY-MM-DD",
                    "period": "Q_ YYYY",
                    "total_records_analyzed": 0
                },

                "global_summary": {
                    "total_innovations": 0,
                    "grassroots_percentage": 0,
                    "institutional_percentage": 0,
                    "semi_formal_percentage": 0
                },

                "top_categories": [
                    {
                    "category": "",
                    "count": 0,
                    "trend": "increasing | decreasing | stable"
                    }
                ],

                "geographic_insights": [
                    {
                    "region": "",
                    "key_pattern": "",
                    "risk_level": "low | medium | high"
                    }
                ],

                "risk_analysis": {
                    "high_risk_cases": 0,
                    "critical_cases": 0,
                    "top_risk_types": [],
                    "emerging_risks": []
                },

                "innovation_patterns": [
                    {
                    "pattern_name": "",
                    "description": "",
                    "regions": [],
                    "risk_level": "low | medium | high"
                    }
                ],

                "hidden_gems": [
                    {
                    "title": "",
                    "country": "",
                    "reason": ""
                    }
                ],

                "intervention_opportunities": [
                    {
                    "type": "training | funding | regulation | research",
                    "target": "",
                    "priority_level": "low | medium | high",
                    "justification": ""
                    }
                ],

                "knowledge_insights": {
                    "most_common_source": "",
                    "trend": "increasing | decreasing | shifting",
                    "observation": ""
                },

                "recommendations": [
                    ""
                ],

                "implementation_intelligence": {
                    "policy_relevance": [
                        {
                        "issue": "",
                        "evidence_basis": "",
                        "linked_pathways": [],
                        "policy_relevance": "",
                        "confidence": "low | medium | high"
                        }
                    ],
                    "policy_options": [
                        {
                        "option_id": "",
                        "instrument": "regulation | funding | training | research | data | partnership",
                        "option": "",
                        "rationale": "",
                        "linked_evidence": [],
                        "linked_pathways": [],
                        "readiness": "exploratory | emerging | ready_for_pilot"
                        }
                    ],
                    "implementation": [
                        {
                        "option_id": "",
                        "action": "",
                        "lead_stakeholders": [],
                        "dependencies": [],
                        "time_horizon": "short | medium | long",
                        "success_indicators": []
                        }
                    ],
                    "feedback": [
                        {
                        "indicator": "",
                        "source": "",
                        "trigger": "",
                        "response": ""
                        }
                    ]
                },

                "charts": {
                    "innovation_by_region": [
                    { "region": "", "count": 0 }
                    ],
                    "risk_distribution": [
                    { "level": "low | medium | high", "count": 0 }
                    ],
                    "knowledge_source_trend": [
                    { "source": "", "count": 0 }
                    ]
                }
                }

                ----------------------------------------
                ANALYSIS GUIDELINES
                ----------------------------------------

                1. GLOBAL SUMMARY
                - Calculate percentages from dataset
                - Ensure total ≈ 100%

                2. TOP CATEGORIES
                - Rank by frequency
                - Trend = based on relative dominance in dataset (not time series)

                3. GEOGRAPHIC INSIGHTS
                - Identify regional clusters
                - Highlight dominant innovation type or issue per region

                4. RISK ANALYSIS
                - High risk = risk_score >= 6
                - Critical = risk_score >= 8
                - Identify repeated dangerous patterns

                5. INNOVATION PATTERNS
                - Group similar innovations into themes
                - Example: "DIY energy systems", "low-cost medical tools"

                6. HIDDEN GEMS
                - Must meet ALL:
                - grassroots
                - low cost
                - high impact
                - Select top 5–10 only

                7. INTERVENTION OPPORTUNITIES
                - Focus on:
                - high risk + high impact
                - scalable innovations needing support

                8. KNOWLEDGE INSIGHTS
                - Analyze distribution of:
                - traditional
                - self-taught
                - internet
                - adapted
                - formal

                9. POLICY / ACTION -> IMPLEMENTATION
                - Treat pathways.json as the system structure; do not invent pathway nodes.
                - Use pathway evidence counts from the supplied pathway snapshot as the factual base.
                - Policy relevance must be explicitly tied to observed evidence, risk, pathway concentration or evidence gaps.
                - Stakeholders should be framed as potential actors/partners, not assumed commitments.
                - Policy options must be options, not decisions; distinguish evidence from interpretation.
                - Implementation actions should be framed as pilots, capacity support, research, governance or monitoring steps.
                - Feedback must describe how future implementation evidence could update the intelligence cycle.
                - Never claim that an implementation occurred unless supported by the supplied data.
                - Keep policy statements concise, contextual and evidence-linked.

                10. RECOMMENDATIONS
                - Must be actionable (not generic)
                - Max 5–8 items

                ----------------------------------------
                STRICT RULES
                ----------------------------------------

                - Output MUST be valid JSON (no markdown, no explanation)
                - Do NOT include text outside JSON
                - Do NOT hallucinate missing data
                - Keep text concise but meaningful
                """

    taxonomy = load_json_file(PATHWAY_FILE, {"domains": {}})
    pathway_snapshot = build_implementation_intelligence(database, {"intervention_opportunities": []}, taxonomy)
    compact_pathway_snapshot = {
        "domains": pathway_snapshot.get("system_pathways", []),
        "evidence": pathway_snapshot.get("evidence", {}),
        "top_innovations": pathway_snapshot.get("innovation", {}).get("top_records", [])[:12]
    }

    prompt = (
        "Analyze the following innovation dataset and generate the report.\n\n"
        "PATHWAY STRUCTURE (from pathways.json):\n"
        + json.dumps(compact_pathway_snapshot, ensure_ascii=False)
        + "\n\nDATASET:\n"
        + db_string
    )
    new_report = call_gemini_with_retry(api_key, prompt, sys_prompt, expect_json=True)

    if new_report:
        total_records = len(database)
        
        # 1. Hitung manual dengan Python agar 100% akurat
        grass_count = sum(1 for x in database if x.get("innovation_level") == "grassroots")
        semi_count = sum(1 for x in database if x.get("innovation_level") == "semi-formal")
        inst_count = sum(1 for x in database if x.get("innovation_level") == "institutional")

        # 2. Paksa (override) hasil halusinasi matematika AI
        new_report["report_metadata"]["total_records_analyzed"] = total_records
        
        if "global_summary" not in new_report:
            new_report["global_summary"] = {}
            
        new_report["global_summary"]["total_innovations"] = total_records
        new_report["global_summary"]["grassroots_percentage"] = round((grass_count / total_records) * 100, 2) if total_records > 0 else 0
        new_report["global_summary"]["semi_formal_percentage"] = round((semi_count / total_records) * 100, 2) if total_records > 0 else 0
        new_report["global_summary"]["institutional_percentage"] = round((inst_count / total_records) * 100, 2) if total_records > 0 else 0

        new_report["report_metadata"]["generated_at"] = datetime.now().isoformat()
        new_report["report_metadata"]["period"] = quarter

        # ==========================================
        # PERBAIKAN 2: PAKSA HITUNGAN RISK ANALYSIS
        # ==========================================
        high_risk_count = sum(1 for x in database if x.get("risk_assessment", {}).get("risk_score", 0) >= 8)
        medium_risk_count = sum(1 for x in database if 4 <= x.get("risk_assessment", {}).get("risk_score", 0) <= 7)
        low_risk_count = sum(1 for x in database if x.get("risk_assessment", {}).get("risk_score", 0) <= 3)
        critical_count = sum(1 for x in database if x.get("critical_flag") == True)

        # Timpa angka di panel atas Risk Analysis
        if "risk_analysis" not in new_report:
            new_report["risk_analysis"] = {}
        # Build an auditable implementation intelligence scaffold from database + taxonomy.
        taxonomy = load_json_file(PATHWAY_FILE, {"domains": {}})
        deterministic_ii = build_implementation_intelligence(database, new_report, taxonomy)
        ai_ii = new_report.get("implementation_intelligence", {}) or {}

        deterministic_ii["policy_relevance"] = ai_ii.get("policy_relevance", []) or []
        if ai_ii.get("policy_options"):
            deterministic_ii["policy_options"] = ai_ii.get("policy_options")
        if ai_ii.get("implementation"):
            deterministic_ii["implementation"] = ai_ii.get("implementation")
        if ai_ii.get("feedback"):
            deterministic_ii["feedback"] = ai_ii.get("feedback")
        new_report["implementation_intelligence"] = deterministic_ii
        new_report["report_metadata"]["schema_version"] = "2.0"

        new_report["risk_analysis"]["high_risk_cases"] = high_risk_count
        new_report["risk_analysis"]["critical_cases"] = critical_count

        # Timpa angka di diagram batang (Bar Chart)
        if "charts" not in new_report:
            new_report["charts"] = {}
        new_report["charts"]["risk_distribution"] =[
            {"level": "High", "count": high_risk_count},
            {"level": "Medium", "count": medium_risk_count},
            {"level": "Low", "count": low_risk_count}
        ]
        
        # Load data lama
        resume_db = load_json_file(RESUME_FILE, [])
        if not isinstance(resume_db, list): 
            resume_db = []

        # ✅ ROTASI ID: Ubah semua 'gsi-current' lama menjadi 'gsi-older'
        for report in resume_db:
            if isinstance(report, dict):
                if "report_metadata" not in report: report["report_metadata"] = {}
                report["report_metadata"]["report_id"] = "gsi-older"

        # Setup metadata laporan baru
        new_report["report_metadata"]["generated_at"] = datetime.now().isoformat()
        new_report["report_metadata"]["period"] = quarter
        new_report["report_metadata"]["report_id"] = "gsi-current"
        
        # ✅ SIMPAN HANYA SEKALI
        resume_db.append(new_report)
        save_json_file(RESUME_FILE, resume_db)
        
        # Update file Markdown untuk preview cepat
        md_content = convert_report_to_markdown(new_report)
        save_text_file(REPORT_MD_FILE, md_content)

        log.info(f"✅ Resume successfully generated and rotated. ID: gsi-current")
    else:
        log.error("Failed to generate intelligence report.")

def convert_report_to_markdown(report_data):
    meta = report_data.get("report_metadata", {})
    global_sum = report_data.get("global_summary", {})
    risk = report_data.get("risk_analysis", {})

    md = f"""# Global Innovation Intelligence Report
**Period:** {meta.get('period', 'N/A')} | **Generated:** {meta.get('generated_at', 'N/A')} | **Records Analyzed:** {meta.get('total_records_analyzed', 0)}

---
## 🌍 Executive Summary
Out of {global_sum.get('total_innovations', 0)} innovations tracked:
- **{global_sum.get('grassroots_percentage', 0)}%** Grassroots
- **{global_sum.get('semi_formal_percentage', 0)}%** Semi-Formal
- **{global_sum.get('institutional_percentage', 0)}%** Institutional

## ⚠️ Emerging Risks
- **High-Risk Cases:** {risk.get('high_risk_cases', 0)} | **Critical:** {risk.get('critical_cases', 0)}
- **Top Risks:** {', '.join(risk.get('top_risk_types', []))}

## 💎 Hidden Gems\n"""
    for gem in report_data.get("hidden_gems", []):
        md += f"- **{gem.get('title', 'Unknown')}** ({gem.get('country', 'Unknown')})\n"

    md += "\n---\n*Report auto-generated by Innovation Radar AI Framework v9.1.*\n"
    return md

# =====================================================================
# MAIN SCHEDULER & EXECUTION CONTROLLER
# =====================================================================

def main():
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    run_type = os.environ.get("RUN_TYPE", "auto").strip().lower()

    if not api_key:
        log.error("GEMINI_API_KEY not found or empty!")
        return

    try:
        db = load_json_file(DATA_FILE, [])
        # ✅ NEW: Auto-correction jika format data.json salah (misal: terbaca sisa ICH Radar)
        if not isinstance(db, list):
            log.warning("Format data.json bukan List! Melakukan auto-correction...")
            if isinstance(db, dict) and "inventory" in db:
                db = db["inventory"]  # Ekstrak list jika ini file bekas ICH Radar
            else:
                db = []  # Reset menjadi list kosong agar aman di-append
        pathway_taxonomy = load_json_file(PATHWAY_FILE, {"domains": {}})
        pathway_changed = False

        history = load_json_file(HISTORY_FILE, {
            "last_data_crawl": "2000-01-01T00:00:00",
            "last_resume_gen": "2000-01-01T00:00:00"
        })

        now = datetime.now()
        last_data_time = datetime.fromisoformat(history.get("last_data_crawl", "2000-01-01T00:00:00"))
        last_resume_time = datetime.fromisoformat(history.get("last_resume_gen", "2000-01-01T00:00:00"))

        do_data = False
        do_resume = False

        if run_type == "force_data":
            do_data = True
            log.info("🚀 TRIGGER: Force Crawl Data (Ignoring Schedule)")
        elif run_type == "force_resume":
            do_resume = True
            log.info("🚀 TRIGGER: Force Resume Generate (Ignoring Schedule)")
        elif run_type == "force_both":
            do_data = True
            do_resume = True
            log.info("🚀 TRIGGER: Force Both Data & Resume (Ignoring Schedule)")
        else:
            log.info("⏳ TRIGGER: Auto Schedule Mode. Checking Timestamps...")

            # ✅ CHANGED: Using env-var constants instead of hardcoded values
            if now - last_data_time >= timedelta(days=DATA_INTERVAL_DAYS):
                do_data = True
                log.info(f"-> Data schedule triggered (>= {DATA_INTERVAL_DAYS} days).")
            else:
                log.info(f"-> Data schedule skipped. Last run: {last_data_time.strftime('%Y-%m-%d')}.")

            if now - last_resume_time >= timedelta(days=RESUME_INTERVAL_DAYS):
                do_resume = True
                log.info(f"-> Resume schedule triggered (>= {RESUME_INTERVAL_DAYS} days).")
            else:
                log.info(f"-> Resume schedule skipped. Last run: {last_resume_time.strftime('%Y-%m-%d')}.")

        if do_data:
            log.info("--- 🟢 STARTING DATA PIPELINE ---")
            # ✅ CHANGED: Using MAX_ITEMS_PER_RUN env-var constant
            found = run_discovery_pipeline(api_key, db, max_items=MAX_ITEMS_PER_RUN)
            pathway_changed = enrich_pathway_matches(db, pathway_taxonomy)
            if found > 0 or pathway_changed:
                save_json_file(DATA_FILE, db)
            history["last_data_crawl"] = now.isoformat()
            log.info(f"🟢 DATA PIPELINE COMPLETE. Added {found} new items. Total: {len(db)}")

        # Enrich legacy records during resume-only runs as well.
        if not do_data:
            pathway_changed = enrich_pathway_matches(db, pathway_taxonomy)
            if pathway_changed:
                save_json_file(DATA_FILE, db)

        if do_resume:
            log.info("--- 🔵 STARTING RESUME PIPELINE ---")
            generate_intelligence_report(api_key, db)
            history["last_resume_gen"] = now.isoformat()
            log.info("🔵 RESUME PIPELINE COMPLETE.")

        save_json_file(HISTORY_FILE, history)
        log.info("✅ All requested tasks completed.")

    except Exception as e:
        log.error(f"Fatal Error during execution: {e}", exc_info=True)

if __name__ == "__main__":
    main()
