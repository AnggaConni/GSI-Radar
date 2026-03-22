"""
=======================================================================
  INNOVATION RADAR v1.1 — Global Intelligence Engine
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
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]}
        "generationConfig": {
            "temperature": 0.5, # Lower temperature for strictly formatted output
            "maxOutputTokens": 8192
        }
    }
    # API Key dimasukkan dengan aman melalui Header
    headers = {
        'Content-Type': 'application/json',
        'x-goog-api-key': api_key
    }
    
    if expect_json:
        payload["generationConfig"] = {"responseMimeType": "application/json"}
    if use_search:
        payload["tools"] = [{"googleSearch": {}}]
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        data = response.json()
        raw_text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        if expect_json:
            return extract_json_safe(raw_text)
        return raw_text
    except Exception as e:
        log.error(f"Gemini API Error: {e}")
        return None

# ✅ NEW: Retry wrapper around call_gemini.
# If Gemini fails (network glitch, timeout, empty response),
# it will automatically try again up to `retries` times.
# Each retry waits longer: 1s, 2s, 4s (exponential backoff).
def call_gemini_with_retry(api_key, prompt, system_instruction, retries=3, **kwargs):
    """
    Calls call_gemini() and retries on failure with exponential backoff.
    retries=3 means: attempt 1 → wait 1s → attempt 2 → wait 2s → attempt 3 → give up.
    """
    for attempt in range(retries):
        result = call_gemini(api_key, prompt, system_instruction, **kwargs)
        if result:
            return result
        wait_time = 2 ** attempt   # 1s, 2s, 4s
        log.warning(f"Gemini call failed (attempt {attempt + 1}/{retries}). Retrying in {wait_time}s...")
        time.sleep(wait_time)
    log.error("All Gemini retry attempts exhausted. Returning None.")
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
    sys_prompt = """Extract structured data about this innovation. Return EXACTLY this JSON structure:
{"title": "", "summary": "", "category": [], "innovation_level": "grassroots | semi-formal | institutional", "location": {"country": "", "region": ""}, "process": {"how_it_works": "", "materials_used": [], "step_by_step": []}, "impact": {"problem_solved": "", "scale": "low | medium | high"}, "replicability": {"cost_level": "low | medium | high", "difficulty": "easy | medium | hard"}}"""
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
# CORE TASKS: DATA CRAWL & RESUME GENERATION
# =====================================================================

def run_discovery_pipeline(api_key, database, max_items=3):
    """Mencari data baru dan menambahkannya ke database."""
    keyword = random.choice(KEYWORDS)
    log.info(f"Initiating radar ping with keyword: '{keyword}'")

    seed_prompt = f"Search the web for 5 distinct, real-world examples of: {keyword}. Provide a detailed paragraph describing what the innovation is, who made it, where it is, and how it works. Return a JSON object with an array 'innovations' containing strings of these raw descriptions."
    seed_sys = "You are an OSINT web scraper. Use google search. Return pure JSON. Do not hallucinate."

    seed_data = call_gemini_with_retry(api_key, seed_prompt, seed_sys, use_search=True)  # ✅ changed
    if not seed_data or "innovations" not in seed_data:
        log.warning("No raw material found on this run.")
        return 0

    raw_descriptions = seed_data["innovations"]
    success_count = 0

    for idx, raw_text in enumerate(raw_descriptions):
        if success_count >= max_items:
            log.info(f"Reached maximum limit of {max_items} items. Stopping.")
            break

        log.info(f"Processing candidate {idx+1}/{len(raw_descriptions)}...")

        validation = pass_1_validate(api_key, raw_text)
        if not validation.get("is_innovation") or validation.get("confidence", 0) < 0.6:
            continue

        base_data = pass_2_extract(api_key, raw_text)
        if not base_data or not base_data.get("title"):
            continue

        # ✅ CHANGED: Use normalize_title() before hashing to prevent
        # duplicates caused by different capitalization or spacing.
        title_hash = hashlib.md5(normalize_title(base_data["title"]).encode('utf-8')).hexdigest()
        if any(item.get("id") == title_hash for item in database):
            log.info("Item is a duplicate. Skipping.")
            continue

        risk_data = pass_3_risk(api_key, raw_text)
        lineage_data = pass_4_lineage(api_key, raw_text)

        final_item = {
            "id": title_hash, "timestamp": datetime.now().isoformat(),
            **base_data,
            "origin": lineage_data if lineage_data else {"knowledge_source": []},
            "risk_assessment": risk_data if risk_data else {}
        }

        country = final_item.get("location", {}).get("country", "")
        region = final_item.get("location", {}).get("region", "")
        lat, lon = get_coordinates(f"{region}, {country}".strip(", "))
        final_item["location"]["lat"] = lat
        final_item["location"]["lon"] = lon

        final_item = calculate_advanced_metrics(final_item)
        database.append(final_item)
        success_count += 1
        log.info(f"🔥 Successfully processed: {final_item['title']} (Score: {final_item.get('priority_score')})")

    return success_count

def generate_intelligence_report(api_key, database):
    """Membaca database dan menambahkan resume baru ke resume.json."""
    if not database:
        log.warning("Database is empty. Skipping report generation.")
        return

    log.info("📊 Generating Periodic Intelligence Resume...")
    quarter = get_current_quarter()

    db_string = json.dumps(database, ensure_ascii=False)

    sys_prompt = """You are an elite AI Intelligence Analyst generating a quarterly global report on grassroots and institutional innovation.
                You will be given a JSON array containing raw innovation records.
                OUTPUT EXACTLY THIS JSON FORMAT:
                {
                "report_metadata": { "report_id": "gsi-current", "generated_at": "YYYY-MM-DD", "period": "Q_ YYYY", "total_records_analyzed": 0 },
                "global_summary": { "total_innovations": 0, "grassroots_percentage": 0, "institutional_percentage": 0, "semi_formal_percentage": 0 },
                "top_categories": [ { "category": "", "count": 0, "trend": "" } ],
                "geographic_insights": [ { "region": "", "key_pattern": "", "risk_level": "" } ],
                "risk_analysis": { "high_risk_cases": 0, "critical_cases": 0, "top_risk_types": [], "emerging_risks": [] },
                "innovation_patterns": [ { "pattern_name": "", "description": "", "regions": [], "risk_level": "" } ],
                "hidden_gems": [ { "title": "", "country": "", "reason": "" } ],
                "intervention_opportunities": [ { "type": "", "target": "", "priority_level": "" } ],
                "knowledge_insights": { "most_common_source": "", "trend": "", "observation": "" },
                "recommendations": [],
                "charts": { "innovation_by_region": [{"region": "", "count": 0}], "risk_distribution": [{"level": "", "count": 0}], "knowledge_source_trend": [{"source": "", "count": 0}] }
                }"""

    prompt = f"Analyze the following innovation dataset and generate the report.\n\nDATASET:\n{db_string}"

    new_report = call_gemini_with_retry(api_key, prompt, sys_prompt, expect_json=True)  # ✅ changed

    if new_report:
        new_report["report_metadata"]["generated_at"] = datetime.now().isoformat()
        new_report["report_metadata"]["period"] = quarter

        resume_db = load_json_file(RESUME_FILE, [])
        if not isinstance(resume_db, list):
            resume_db = []

        resume_db.append(new_report)
        save_json_file(RESUME_FILE, resume_db)

        md_content = convert_report_to_markdown(new_report)
        save_text_file(REPORT_MD_FILE, md_content)

        log.info("✅ Intelligence Resume successfully appended to resume.json.")
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
            if found > 0:
                save_json_file(DATA_FILE, db)
            history["last_data_crawl"] = now.isoformat()
            log.info(f"🟢 DATA PIPELINE COMPLETE. Added {found} new items. Total: {len(db)}")

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
