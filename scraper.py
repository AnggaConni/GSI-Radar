"""
=======================================================================
  ICH SHARED HERITAGE RADAR v6.1 — Global Intelligence Engine
  AI Engine : Google Gemini 2.5 Flash (Google Search Grounding)
  Mode      : 2-Phase (Enrichment of Incomplete Data -> Discovery)
  Feature   : Quality over Quantity (Iterative Looping), Anti-Redundancy, Wikimedia Fallback
=======================================================================
"""

import os
import json
import hashlib
import logging
import random
import re
import time
from datetime import datetime
import requests

# ── Logging Configuration ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger("ICH_Radar")

# ── File Paths ──
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")
DATA_FILE    = os.path.join(BASE_DIR, "data.json")
RESUME_FILE  = os.path.join(BASE_DIR, "resume.json")

# ======================================================================
# GLOBAL KEYWORD DATABASE FOR DISCOVERY (Multi-Language)
# ======================================================================
KEYWORDS = [
    # ─────────────────────────────────────────────
    # UNREGISTERED / LOCAL FOLKLORE / COMMUNITY PRACTICES
    # (Keywords targeting blogs, social media, local news, non-UNESCO)
    # ─────────────────────────────────────────────
    "unregistered local heritage traditions",
    "endangered local folklore practices",
    "everyday community cultural practices",
    "forgotten village traditions",
    "ancestral customs still practiced today",
    "oral traditions passed down generations",
    "traditional knowledge from elders",
    "community rituals preserved by villagers",
    "local craft traditions handmade methods",
    "ancient village ceremonies still practiced",
    "traditional farming knowledge ancestors",
    "indigenous healing rituals traditional medicine",
    "traditional food preparation ancestral recipe",

    "tradisi lokal masyarakat adat kampung",
    "kebiasaan turun temurun warga",
    "resep rahasia leluhur masakan daerah",
    "ritual adat lokal yang hampir punah",
    "cerita rakyat dan mitos lokal",
    "upacara adat desa yang jarang diketahui",
    "pengetahuan tradisional masyarakat adat",
    "kerajinan tangan tradisional desa",
    "cara memasak tradisional warisan nenek moyang",
    "ritual panen tradisional masyarakat lokal",

    "prácticas culturales comunitarias no registradas",
    "tradiciones de pueblos originarios blog",
    "rituales tradicionales de comunidades indígenas",
    "recetas ancestrales tradicionales de pueblo",
    "costumbres heredadas de generaciones",

    "coutumes locales et traditions de village",
    "rituels traditionnels des communautés locales",
    "savoir-faire artisanal traditionnel village",
    "traditions orales transmises par les anciens",

    "民间未注册的传统习俗",
    "地方传统文化习俗",
    "民间手工艺传统技艺",
    "乡村传统节庆习俗",
    "祖传食谱与传统做法",

    "지역 숨겨진 전통 문화",
    "마을 전통 의식과 풍습",
    "전통 수공예 기술 장인",
    "세대에서 세대로 전해지는 문화",

    "local tribal rituals undocumented",
    "hidden cultural traditions village",
    "traditional ceremonies rarely documented",
    "oral folklore traditions community elders",
    "traditional crafts handmade ancestral techniques",
    "forgotten cultural rituals rural communities",
    "traditional storytelling folklore village",
    "indigenous cultural practices still alive",
    "festival desa tahunan",
    "upacara adat panen",
    "ritual pernikahan tradisional desa",
    "cara membuat kerajinan tradisional",
    "traditional harvest ceremony village",
    "ancient ritual still practiced village",
    "how villagers make traditional craft",
    "ancestral cooking method traditional dish",

    # ─────────────────────────────────────────────
    # ENGLISH (Global / General)
    # ─────────────────────────────────────────────
    "Intangible Cultural Heritage examples",
    "UNESCO 2003 Convention elements",
    "Living Heritage practices",
    "Traditional craftsmanship UNESCO",
    "Oral traditions and expressions heritage",
    "Performing arts intangible heritage",
    "ICH inventory documentation",
    "UNESCO Representative List ICH",
    "Urgent Safeguarding List ICH",
    "Traditional knowledge indigenous communities",
    "Ritual practices cultural heritage",
    "Festive events cultural heritage",
    "Traditional music instruments heritage",
    "Ancestral knowledge safeguarding",
    "Community-based heritage preservation",
    "Intangible heritage digital inventory",
    "Folk arts and traditions documentation",
    "Customary practices cultural safeguarding",
    "Social practices rituals UNESCO",
    "Nature knowledge universe heritage",
    "Traditional food preparation heritage",
    "Healing practices traditional medicine heritage",
    "Storytelling oral heritage",
    "Traditional dance heritage documentation",

    # ─────────────────────────────────────────────
    # INDONESIAN / MALAY
    # ─────────────────────────────────────────────
    "Warisan Budaya Takbenda",
    "Warisan Kebudayaan Tak Ketara",
    "Inventaris Warisan Budaya",
    "Pelestarian tradisi lisan",
    "Kesenian tradisional warisan budaya",
    "Pengetahuan tradisional masyarakat adat",
    "Upacara adat warisan budaya",
    "Keterampilan kerajinan tradisional",
    "Seni pertunjukan warisan budaya takbenda",
    "Praktik sosial budaya takbenda UNESCO",

    # ─────────────────────────────────────────────
    # SPANISH (Latin America & Spain)
    # ─────────────────────────────────────────────
    "Patrimonio Cultural Inmaterial UNESCO",
    "Patrimonio vivo tradiciones",
    "Prácticas y saberes tradicionales",
    "Inventario patrimonio inmaterial",
    "Expresiones culturales tradicionales",
    "Conocimientos ancestrales indígenas",
    "Artesanía tradicional patrimonio vivo",
    "Rituales y fiestas patrimonio UNESCO",
    "Salvaguardia patrimonio cultural inmaterial",
    "Tradiciones orales patrimonio vivo",
    "Música y danza tradicional patrimonio",
    "Medicina tradicional saberes ancestrales",

    # ─────────────────────────────────────────────
    # FRENCH (Francophone Africa, France, Canada)
    # ─────────────────────────────────────────────
    "Patrimoine culturel immatériel",
    "Traditions et expressions orales UNESCO",
    "Pratiques sociales rituels et événements festifs",
    "Inventaire patrimoine immatériel",
    "Savoir-faire artisanal traditionnel",
    "Connaissances sur la nature et l'univers",
    "Sauvegarde du patrimoine vivant",
    "Arts du spectacle patrimoine immatériel",
    "Pratiques culturelles communautaires UNESCO",
    "Expressions culturelles traditionnelles",

    # ─────────────────────────────────────────────
    # CHINESE — MANDARIN (China, Taiwan, Diaspora)
    # ─────────────────────────────────────────────
    "非物质文化遗产",          # Fēi wùzhí wénhuà yíchǎn
    "联合国教科文组织 传统手工艺",
    "口头传统和表现形式",       # Oral traditions and expressions
    "表演艺术非遗",            # Performing arts ICH
    "社会实践仪式节庆活动",     # Social practices, rituals, festive events
    "传统知识与实践",           # Traditional knowledge and practices
    "无形文化遗产保护",         # ICH safeguarding
    "民间艺术传统技艺",         # Folk art and traditional skills
    "非遗数字化记录",           # Digital documentation of ICH

    # ─────────────────────────────────────────────
    # CHINESE — CANTONESE
    # ─────────────────────────────────────────────
    "非物質文化遺產",          # Traditional Chinese (Cantonese/Hong Kong/Taiwan)
    "口頭傳統及表達方式",
    "傳統工藝技術",
    "表演藝術非遺",

    # ─────────────────────────────────────────────
    # JAPANESE
    # ─────────────────────────────────────────────
    "無形文化遺産",            # Mukei bunka isan
    "伝統的工芸技術 ユネスコ",
    "口承による伝統及び表現",   # Oral traditions and expressions
    "社会的慣習 儀式 祭礼行事",
    "自然及び万物に関する知識と慣習",
    "伝統芸能 無形文化遺産",
    "民俗芸能 無形文化",
    "無形文化遺産 保護条約",
    "伝統文化 デジタルアーカイブ",

    # ─────────────────────────────────────────────
    # KOREAN
    # ─────────────────────────────────────────────
    "무형문화유산",            # Muhyeong munhwa yusan
    "전통 지식과 관습",
    "구전 전통 및 표현",
    "공연예술 무형유산",
    "전통 공예 기술 유네스코",
    "사회적 관행 의식 및 축제",
    "무형문화재 보호",
    "전통 생활 문화 기록",

    # ─────────────────────────────────────────────
    # ARABIC (Middle East & North Africa)
    # ─────────────────────────────────────────────
    "التراث الثقافي غير المادي",       # Al-turath al-thaqafi ghayr al-madi
    "التقاليد وأشكال التعبير الشفهي",
    "الممارسات الاجتماعية والطقوس",
    "الحرف التقليدية اليدوية اليونسكو",
    "الموسيقى التقليدية التراث",
    "المعارف التقليدية والممارسات",
    "صون التراث الثقافي غير المادي",
    "فنون الأداء التراثية",
    "التراث الشفهي والموروث الثقافي",
    "قوائم جرد التراث غير المادي",

    # ─────────────────────────────────────────────
    # PORTUGUESE (Brazil, Portugal, Lusophone Africa)
    # ─────────────────────────────────────────────
    "Patrimônio Cultural Imaterial",
    "Saberes e práticas tradicionais",
    "Inventário patrimônio imaterial",
    "Expressões culturais tradicionais",
    "Conhecimentos ancestrais indígenas",
    "Artesanato tradicional patrimônio",
    "Rituais e festas patrimônio UNESCO",
    "Tradições orais patrimônio imaterial",
    "Salvaguarda patrimônio cultural vivo",
    "Artes do espetáculo patrimônio imaterial",

    # ─────────────────────────────────────────────
    # RUSSIAN (Eastern Europe & Central Asia)
    # ─────────────────────────────────────────────
    "Нематериальное культурное наследие",
    "Традиционные ремесла ЮНЕСКО",
    "Устные традиции и формы выражения",
    "Исполнительские искусства наследие",
    "Обычаи обряды и праздники UNESCO",
    "Традиционные знания и практики",
    "Охрана нематериального наследия",
    "Народное искусство традиции",
    "Цифровой реестр культурного наследия",

    # ─────────────────────────────────────────────
    # HINDI (South Asia — India)
    # ─────────────────────────────────────────────
    "अमूर्त सांस्कृतिक विरासत",
    "पारंपरिक शिल्प कौशल",
    "मौखिक परंपराएं और अभिव्यक्तियां",
    "लोक कला और परंपरा",
    "सामाजिक प्रथाएं और अनुष्ठान",
    "पारंपरिक ज्ञान संरक्षण",
    "युनेस्को अमूर्त धरोहर सूची",
    "सांस्कृतिक विरासत डिजिटल संग्रह",

    # ─────────────────────────────────────────────
    # URDU (Pakistan & South Asia)
    # ─────────────────────────────────────────────
    "غیر محسوس ثقافتی ورثہ",
    "روایتی دستکاری یونیسکو",
    "زبانی روایات اور اظہار",
    "ثقافتی ورثہ تحفظ",
    "لوک فنون اور روایات",

    # ─────────────────────────────────────────────
    # BENGALI (Bangladesh & West Bengal)
    # ─────────────────────────────────────────────
    "অস্পষ্ট সাংস্কৃতিক ঐতিহ্য",
    "ঐতিহ্যবাহী শিল্পকলা সংরক্ষণ",
    "মৌখিক ঐতিহ্য এবং প্রকাশনা",
    "লোকশিল্প ও ঐতিহ্য ইউনেস্কো",
    "সামাজিক রীতি আচার অনুষ্ঠান",

    # ─────────────────────────────────────────────
    # TAMIL (South India & Sri Lanka)
    # ─────────────────────────────────────────────
    "அருவமான கலாச்சார பாரம்பரியம்",
    "பாரம்பரிய கைவினை யுனெஸ்கோ",
    "வாய்மொழி மரபுகள் மற்றும் வெளிப்பாடுகள்",
    "நாட்டுப்புறக் கலைகள் பாரம்பரியம்",

    # ─────────────────────────────────────────────
    # TURKISH
    # ─────────────────────────────────────────────
    "Somut Olmayan Kültürel Miras",
    "Geleneksel el sanatları UNESCO",
    "Sözlü gelenekler ve anlatımlar",
    "Toplumsal uygulamalar ritüeller",
    "Geleneksel bilgi ve uygulamalar",
    "Yaşayan miras belgeleme",
    "UNESCO kültürel miras envanteri",

    # ─────────────────────────────────────────────
    # PERSIAN / FARSI (Iran, Afghanistan, Tajikistan)
    # ─────────────────────────────────────────────
    "میراث فرهنگی ناملموس",
    "سنت‌های شفاهی و بیان",
    "صنایع دستی سنتی یونسکو",
    "دانش و عملکردهای سنتی",
    "میراث زنده فرهنگی",
    "آداب و رسوم فرهنگی میراث",

    # ─────────────────────────────────────────────
    # SWAHILI (East Africa)
    # ─────────────────────────────────────────────
    "Urithi wa utamaduni usiohamishika",
    "Mila na desturi za jadi UNESCO",
    "Sanaa za jadi urithi wa utamaduni",
    "Maarifa ya jadi na mazoea",
    "Hifadhi ya urithi wa utamaduni",
    "Tamaduni simulizi Afrika Mashariki",

    # ─────────────────────────────────────────────
    # HAUSA (West Africa — Nigeria, Niger, Ghana)
    # ─────────────────────────────────────────────
    "Al'adun gargajiya UNESCO",
    "Tarihin al'adu marasa abu",
    "Kiyaye al'adun gargajiya",

    # ─────────────────────────────────────────────
    # YORUBA (Nigeria & West Africa)
    # ─────────────────────────────────────────────
    "Aṣà ìjìnlẹ̀ àti ohun-ìní àṣà",
    "Ìmọ̀ àṣà àti àṣà ìbílẹ̀",
    "Ìtọ́jú ohun-ìní àṣà tí kò ní ara",

    # ─────────────────────────────────────────────
    # AMHARIC (Ethiopia)
    # ─────────────────────────────────────────────
    "ቅርስ ሥነ ጥበብ ባህል",
    "ቁሳዊ ያልሆነ ባህላዊ ቅርስ",
    "ባህላዊ ዕደ ጥበብ ዩኔስኮ",
    "የቃል ወጎች እና አገላለጽ",

    # ─────────────────────────────────────────────
    # VIETNAMESE
    # ─────────────────────────────────────────────
    "Di sản văn hóa phi vật thể",
    "Nghề thủ công truyền thống UNESCO",
    "Truyền thống truyền miệng và biểu đạt",
    "Thực hành xã hội lễ hội văn hóa",
    "Bảo tồn di sản sống",
    "Kiến thức truyền thống bản địa",

    # ─────────────────────────────────────────────
    # THAI
    # ─────────────────────────────────────────────
    "มรดกภูมิปัญญาทางวัฒนธรรม",
    "หัตถกรรมพื้นบ้าน ยูเนสโก",
    "ประเพณีและนิทานพื้นบ้าน",
    "ภูมิปัญญาท้องถิ่น การอนุรักษ์",
    "ศิลปะการแสดงพื้นบ้าน มรดก",

    # ─────────────────────────────────────────────
    # TAGALOG / FILIPINO
    # ─────────────────────────────────────────────
    "Di-materyal na pamana ng kultura",
    "Tradisyonal na kaalaman at kasanayan",
    "Katutubong sining at kultura UNESCO",
    "Pagsasalin ng oral na tradisyon",
    "Pangangalaga ng pamana ng kultura",

    # ─────────────────────────────────────────────
    # GERMAN (Germany, Austria, Switzerland)
    # ─────────────────────────────────────────────
    "Immaterielles Kulturerbe UNESCO",
    "Mündliche Überlieferungen und Ausdrucksformen",
    "Traditionelles Handwerk Kulturerbe",
    "Soziale Praktiken und Rituale UNESCO",
    "Lebendiges Erbe Dokumentation",
    "Traditionelles Wissen indigene Gemeinschaften",
    "Immaterielles Erbe Inventar",

    # ─────────────────────────────────────────────
    # ITALIAN
    # ─────────────────────────────────────────────
    "Patrimonio culturale immateriale UNESCO",
    "Tradizioni e espressioni orali",
    "Artigianato tradizionale patrimonio",
    "Pratiche sociali rituali eventi festivi",
    "Salvaguardia patrimonio vivente",
    "Conoscenze tradizionali comunità locali",

    # ─────────────────────────────────────────────
    # DUTCH (Netherlands, Belgium, Suriname)
    # ─────────────────────────────────────────────
    "Immaterieel cultureel erfgoed UNESCO",
    "Mondelinge tradities en uitdrukkingen",
    "Traditioneel ambachtelijk erfgoed",
    "Sociale praktijken rituelen en feesten",
    "Levend erfgoed documentatie",

    # ─────────────────────────────────────────────
    # POLISH
    # ─────────────────────────────────────────────
    "Niematerialne dziedzictwo kulturowe",
    "Tradycyjne rzemiosło UNESCO",
    "Ustne tradycje i wyrazy kultury",
    "Praktyki społeczne obrzędy i uroczystości",
    "Ochrona żywego dziedzictwa",

    # ─────────────────────────────────────────────
    # UKRAINIAN
    # ─────────────────────────────────────────────
    "Нематеріальна культурна спадщина",
    "Традиційні ремесла ЮНЕСКО",
    "Усні традиції та форми вираження",
    "Охорона живої культурної спадщини",

    # ─────────────────────────────────────────────
    # ROMANIAN
    # ─────────────────────────────────────────────
    "Patrimoniu cultural imaterial UNESCO",
    "Tradiții și expresii orale",
    "Meșteșuguri tradiționale patrimoniu",
    "Practici sociale ritualuri sărbători",

    # ─────────────────────────────────────────────
    # GREEK
    # ─────────────────────────────────────────────
    "Άυλη πολιτιστική κληρονομιά UNESCO",
    "Προφορικές παραδόσεις και εκφράσεις",
    "Παραδοσιακές τέχνες και χειροτεχνία",
    "Κοινωνικές πρακτικές τελετουργίες",

    # ─────────────────────────────────────────────
    # CZECH
    # ─────────────────────────────────────────────
    "Nehmotné kulturní dědictví UNESCO",
    "Ústní tradice a výrazové formy",
    "Tradiční řemesla kulturní dědictví",

    # ─────────────────────────────────────────────
    # HUNGARIAN
    # ─────────────────────────────────────────────
    "Szellemi kulturális örökség UNESCO",
    "Hagyományos kézműves tudás",
    "Szóbeli hagyományok és kifejezések",

    # ─────────────────────────────────────────────
    # HEBREW (Israel)
    # ─────────────────────────────────────────────
    "מורשת תרבותית בלתי מוחשית",
    "מסורות בעל פה ואמנויות ביצוע",
    "מלאכת יד מסורתית אונסקו",

    # ─────────────────────────────────────────────
    # BURMESE / MYANMAR
    # ─────────────────────────────────────────────
    "အကာအကွယ်မဲ့ ယဉ်ကျေးမှုအမွေ",
    "ရိုးရာလက်မှုပညာ ယူနက်စကို",
    "နှုတ်ဆိုဆင်ခြင် ရိုးရာထုံးစံ",

    # ─────────────────────────────────────────────
    # KHMER (Cambodia)
    # ─────────────────────────────────────────────
    "បេតិកភណ្ឌវប្បធម៌អរូបី",
    "សិល្បៈប្រពៃណី និងចំណេះដឹងខ្មែរ",

    # ─────────────────────────────────────────────
    # MONGOLIAN
    # ─────────────────────────────────────────────
    "Биет бус соёлын өв",
    "Уламжлалт гар урлал ЮНЕСКО",
    "Аман уламжлал болон илэрхийлэл",

    # ─────────────────────────────────────────────
    # KAZAKH / CENTRAL ASIAN (Uzbek, Kyrgyz)
    # ─────────────────────────────────────────────
    "Материалдық емес мәдени мұра",
    "Дәстүрлі қолөнер ЮНЕСКО",
    "Nomoddiy madaniy meros UNESCO",       # Uzbek
    "Материалдык эмес маданий мурас",     # Kyrgyz

    # ─────────────────────────────────────────────
    # GEORGIAN
    # ─────────────────────────────────────────────
    "არამატერიალური კულტურული მემკვიდრეობა",
    "ტრადიციული ხელოსნობა UNESCO",

    # ─────────────────────────────────────────────
    # ARMENIAN
    # ─────────────────────────────────────────────
    "Անշոշափելի մշակութային ժառանգություն",
    "Ավանդական արհեստներ ՅՈՒՆԵՍԿՕ",

    # ─────────────────────────────────────────────
    # AZERBAIJANI
    # ─────────────────────────────────────────────
    "Qeyri-maddi mədəni irs UNESCO",
    "Ənənəvi sənətkarlıq mədəni irs",

    # ─────────────────────────────────────────────
    # NEPALI
    # ─────────────────────────────────────────────
    "अमूर्त सांस्कृतिक सम्पदा",
    "पारम्परिक शिल्पकला यूनेस्को",
    "मौखिक परम्परा र अभिव्यक्ति",

    # ─────────────────────────────────────────────
    # SINHALA (Sri Lanka)
    # ─────────────────────────────────────────────
    "අස්පෘශ්‍ය සංස්කෘතික උරුමය",
    "සාම්ප්‍රදායික ශිල්ප UNESCO",

    # ─────────────────────────────────────────────
    # WOLOF / FRENCH CREOLE (Senegal & West Africa)
    # ─────────────────────────────────────────────
    "Patrimoine culturel immatériel Sénégal",
    "Traditions orales Afrique de l'Ouest",
    "Savoir-faire artisanal Afrique",

    # ─────────────────────────────────────────────
    # QUECHUA / AYMARA (Andean — Peru, Bolivia, Ecuador)
    # ─────────────────────────────────────────────
    "Patrimonio cultural andino inmaterial",
    "Saberes ancestrales quechua aymara",
    "Rituales y ceremonias indígenas andinas",

    # ─────────────────────────────────────────────
    # NAHUATL / MAYA (Mesoamerica — Mexico, Guatemala)
    # ─────────────────────────────────────────────
    "Patrimonio cultural indígena mesoamericano",
    "Tradiciones orales mayas guatemaltecas",
    "Saberes ancestrales nahuatl Mexico",

    # ─────────────────────────────────────────────
    # GUARANÍ (Paraguay & South America)
    # ─────────────────────────────────────────────
    "Teko porã rembiapokue UNESCO",
    "Patrimonio cultural inmaterial guaraní",

    # ─────────────────────────────────────────────
    # MĀORI / PACIFIC ISLANDER (New Zealand, Pacific)
    # ─────────────────────────────────────────────
    "Māori cultural heritage taonga",
    "Pacific intangible cultural heritage",
    "Traditional Pacific navigation knowledge",
    "Indigenous Pacific oral traditions",

    # ─────────────────────────────────────────────
    # ABORIGINAL / TORRES STRAIT ISLANDER (Australia)
    # ─────────────────────────────────────────────
    "Aboriginal intangible cultural heritage Australia",
    "Indigenous Australian oral traditions",
    "Dreamtime stories cultural heritage",
    "First Nations traditional knowledge Australia",

    # ─────────────────────────────────────────────
    # DIASPORA, MIGRATION & SHARED HERITAGE
    # (Triggering the AI to find cross-border cultural diffusion)
    # ─────────────────────────────────────────────
    "traditional practices in diaspora communities",
    "immigrant heritage food preserved across generations",
    "cross-border cultural traditions shared by multiple countries",
    "syncretic cultural rituals and assimilated heritage",
    "tradisi perantau yang masih dipertahankan di luar negeri",
    "budaya campuran hasil asimilasi masyarakat",
    "prácticas culturales de la diáspora",
    "traditions partagées au-delà des frontières",

    # ─────────────────────────────────────────────
    # TRADITIONAL SPORTS & MARTIAL ARTS
    # (High-engagement community practices)
    # ─────────────────────────────────────────────
    "traditional martial arts heritage",
    "indigenous sports and community games",
    "bela diri tradisional warisan leluhur",
    "permainan tradisional anak desa yang terlupakan",
    "artes marciales tradicionales patrimonio vivo",
    "jeux traditionnels et sports autochtones",
    "传统武术 非物质文化遗产",

    # ─────────────────────────────────────────────
    # MARITIME, NAVIGATION & VERNACULAR ARCHITECTURE
    # (Often shared across coastal networks/islands)
    # ─────────────────────────────────────────────
    "traditional boat building heritage",
    "indigenous navigation techniques ocean seafaring",
    "traditional ecological architecture and building techniques",
    "teknik pembuatan perahu tradisional nelayan",
    "arsitektur vernakular cara membangun rumah adat",
    "pengetahuan navigasi laut tradisional",
    "arquitectura vernácula y saberes constructivos",

    # ─────────────────────────────────────────────
    # DOMAIN-SPECIFIC CROSS-LANGUAGE SEARCHES
    # ─────────────────────────────────────────────
    # Music & Performing Arts
    "traditional music UNESCO heritage",
    "folk dance intangible heritage",
    "chanting ritual heritage documentation",
    "traditional theater heritage",

    # Food & Gastronomy
    "traditional cuisine UNESCO heritage",
    "gastronomía tradicional patrimonio inmaterial",
    "cuisine traditionnelle patrimoine UNESCO",
    "传统饮食文化 非遗",

    # Medicine & Healing
    "traditional medicine knowledge heritage",
    "medicina tradicional patrimonio inmaterial",
    "médecine traditionnelle patrimoine",
    "традиционная медицина наследие",

    # Agricultural / Ecological Knowledge
    "traditional ecological knowledge heritage",
    "indigenous farming practices heritage UNESCO",
    "知識伝統農業 文化遺産",

    # Textile & Weaving
    "traditional weaving textile heritage",
    "tissage artisanal patrimoine UNESCO",
    "tejido tradicional patrimonio",
    "伝統的織物 無形文化遺産",

    # Festivals & Ceremonies
    "traditional festival ceremony heritage",
    "fiesta tradicional patrimonio vivo",
    "fête traditionnelle patrimoine immatériel",
    "伝統的祭り 文化遺産"
]

# ======================================================================
# DATA PERSISTENCE & MIGRATION
# ======================================================================

def load_db():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "listings" in data:
                    log.info("Migrating old database schema to ICH format...")
                    return {"summary": {}, "inventory": []}
                if "inventory" not in data:
                    data["inventory"] = []
                return data
        except Exception as e:
            log.warning(f"Database corrupted, starting fresh: {e}")
            
    return {"summary": {}, "inventory": []}

def save_db(db):
    db["summary"] = calculate_summary(db["inventory"])
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

def calculate_summary(inventory):
    complete = len([x for x in inventory if x.get("completion_status") == "COMPLETE"])
    incomplete = len(inventory) - complete
    
    categories = {}
    for item in inventory:
        cat = item.get("category", "Unknown")
        categories[cat] = categories.get(cat, 0) + 1
        
    return {
        "generated_at": datetime.now().isoformat() + "Z",
        "total_ich_elements": len(inventory),
        "complete_records": complete,
        "incomplete_records": incomplete,
        "categories_breakdown": categories
    }

def get_wikimedia_image(query):
    """
    Fallback function: Fetches a thumbnail from Wikimedia Commons based on the query.
    """
    try:
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "prop": "pageimages",
            "generator": "search",
            "gsrsearch": f"filetype:bitmap {query}",
            "gsrlimit": 1,
            "pithumbsize": 800
        }
        
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        
        if "query" in data and "pages" in data["query"]:
            pages = data["query"]["pages"]
            first_page = list(pages.values())[0]
            if "thumbnail" in first_page:
                log.info(f"Wikimedia fallback success for query: '{query}'")
                return first_page["thumbnail"]["source"]
    except Exception as e:
        log.warning(f"Wikimedia fallback failed for '{query}': {e}")
        
    return None

def get_screenshot_url(url, element_name="Unknown Element"):
    """
    Tries to get a screenshot from Microlink. 
    If the URL is missing or invalid, it falls back to Wikimedia Commons.
    If the URL is ALREADY an image (e.g., .jpg), it returns the URL directly.
    """
    if not url or url.lower() == "n/a" or url.startswith("http://n/a"):
        log.info(f"Invalid URL for '{element_name}', triggering Wikimedia fallback...")
        wiki_img = get_wikimedia_image(element_name)
        return wiki_img if wiki_img else "N/A"
        
    # SMART CHECK: If it's already an image file, DO NOT use Microlink screenshot API.
    lower_url = url.lower()
    if lower_url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg')):
        log.info(f"Direct image URL detected for '{element_name}'. Skipping Microlink API.")
        return url
        
    encoded_url = requests.utils.quote(url)
    return f"https://api.microlink.io/?url={encoded_url}&screenshot=true&meta=false&embed=screenshot.url"

def generate_id(name):
    return "ich-" + hashlib.md5(name.lower().encode()).hexdigest()[:8]

def get_coordinates(location_name):
    """
    Mengambil latitude & longitude dari Nominatim API.
    Sama seperti versi JS, kita membersihkan nama jika ada tanda kurung.
    """
    if not location_name or location_name == "N/A":
        return None, None

    try:
        # Bersihkan nama (Contoh: "Canada (Quebec)" -> "Canada")
        clean_name = location_name.split('(')[0].strip()
        
        # Nominatim butuh User-Agent agar tidak diblokir
        headers = {'User-Agent': 'ICH-Shared-Heritage-Radar-Crawler'}
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={requests.utils.quote(clean_name)}&limit=1"
        
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if data and len(data) > 0:
            log.info(f"Geocoding Success: {clean_name} -> [{data[0]['lat']}, {data[0]['lon']}]")
            return float(data[0]['lat']), float(data[0]['lon'])
            
    except Exception as e:
        log.warning(f"Geocoding Failed for {location_name}: {e}")
    
    return None, None

# ======================================================================
# DATA AUDIT (Check for missing thumbnails)
# ======================================================================

def audit_inventory(inventory):
    """Scans inventory and marks items with missing images as INCOMPLETE."""
    audited_count = 0
    for item in inventory:
        thumb = item.get("thumbnail_url", "")
        # Jika gambar kosong, N/A, atau rusak, paksa turunkan statusnya
        if not thumb or thumb == "N/A" or "placeholder" in thumb.lower():
            if item.get("completion_status") == "COMPLETE":
                item["completion_status"] = "INCOMPLETE"
                log.info(f"Audit: Marked '{item.get('element_name')}' as INCOMPLETE due to missing thumbnail.")
                audited_count += 1
    return audited_count

# ======================================================================
# CORE: GEMINI AI INTERACTION
# ======================================================================

def call_gemini(api_key, prompt):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"googleSearch": {}}],
        "generationConfig": {
            "temperature": 0.4, # Lower temperature for strictly formatted output
            "maxOutputTokens": 8192
        }
    }

    # API Key dimasukkan dengan aman melalui Header
    headers = {
        'Content-Type': 'application/json',
        'x-goog-api-key': api_key
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            log.error(f"Google API Error: {response.text}")
            return None

        data = response.json()
        text = data['candidates'][0]['content']['parts'][0]['text']
        
        # Extract JSON from Markdown code blocks
        clean_text = text.replace('```json', '').replace('```', '')
        start_idx = clean_text.find('[') if '[' in clean_text else clean_text.find('{')
        end_idx = clean_text.rfind(']') if clean_text.rfind(']') > clean_text.rfind('}') else clean_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            return json.loads(clean_text[start_idx:end_idx+1])
        return None
    except Exception as e:
        log.error(f"Gemini API failure: {e}")
        return None

# ======================================================================
# PHASE 1: ENRICHMENT (Fixing Incomplete Data)
# ======================================================================

def enrich_incomplete_items(api_key, inventory):
    incomplete_items = [item for item in inventory if item.get("completion_status") != "COMPLETE"]
    if not incomplete_items:
        log.info("No incomplete items found. Enrichment phase skipped.")
        return 0
    
    log.info(f"Found {len(incomplete_items)} incomplete items. Starting enrichment...")
    enriched_count = 0
    
    for item in incomplete_items[:3]:
        element_name = item.get("element_name")
        current_sources = item.get("source_urls", [])
        
        # Deteksi apakah item ini masuk antrean karena gambarnya hilang
        needs_image = not item.get("thumbnail_url") or item.get("thumbnail_url") == "N/A"
        image_instruction = "Crucially, this record lacks a valid image. You MUST find a new source URL (like a news article, official site, or Wikipedia) that contains a clear, high-quality image of this heritage." if needs_image else ""
        
        log.info(f"Enriching: {element_name}")
        
        prompt = f"""
        You are a Cultural Heritage expert. I have an incomplete record for the Cultural Heritage practice/tradition: "{element_name}".
        Current known sources: {current_sources}.
        
        Please use Google Search to find the missing information (e.g., specific step-by-step crafting process, authentic recipe, or detailed history). 
        You can search through local news, community blogs, and social media.
        Find AT LEAST ONE NEW source URL to add to the existing ones.
        {image_instruction}
        
        IMPORTANT: DO NOT output any links containing 'vertexaisearch.cloud.google.com' or 'grounding-api-redirect'. Output the direct, true website URL.
        
        Respond ONLY with a JSON object representing the UPDATED element.
        Ensure ALL output data values and keys are strictly in ENGLISH.
        If you find the missing data, change "completion_status" to "COMPLETE".
        
        Required JSON Structure:
        {{
            "id": "{item.get('id')}",
            "element_name": "{element_name}",
            "category": "{item.get('category', 'Traditional Craftsmanship')}",
            "thumbnail_url": "{item.get('thumbnail_url')}",
            "source_urls": ["<old_url>", "<new_found_url>"],
            "scraped_at": "{datetime.now().isoformat()}Z",
            "location": {{ 
                        "country": "...", 
                        "provinces": ["..."],
                        "lat": null, 
                        "lng": null 
        }},
            "resume_analisa": {{ "description": "...", "cultural_significance": "...", "gemini_tags": ["..."] }},
            "resume_tata_cara": {{ "type": "crafting_process/culinary_recipe/ritual_sequence", "materials_and_tools": ["..."], "step_by_step": ["..."] }},
            "shared_heritage_detection": {{ "is_shared": true, "confidence_score": 0.95, "related_elements": [{{ "country": "...", "element_name": "...", "relationship_reason": "..." }}] }},
            "completion_status": "COMPLETE"
        }}
        """
        
# BARIS DI BAWAH INI SEKARANG SUDAH MASUK KE DALAM LOOP (Indentasi Benar)
        updated_item = call_gemini(api_key, prompt)
        if updated_item and isinstance(updated_item, dict):
            # --- LOGIKA KOORDINAT ---
            country = updated_item.get("location", {}).get("country", "")
            lat, lng = get_coordinates(country)
            
            # Perbaikan: Inisialisasi key "location" untuk mencegah KeyError
            updated_item.setdefault("location", {})
            updated_item["location"]["lat"] = lat
            updated_item["location"]["lng"] = lng
            
            index = inventory.index(item)
            inventory[index] = updated_item
            enriched_count += 1
            log.info(f"Successfully enriched {element_name} (Coords: {lat}, {lng})")
        
        time.sleep(5) 
        
    return enriched_count

# ======================================================================
# PHASE 2: DISCOVERY (Finding New Data)
# ======================================================================

def discover_new_items(api_key, inventory):
    discovered_count = 0
    max_discoveries_per_run = 3 
    
    for i in range(max_discoveries_per_run):
        existing_names = [item.get("element_name", "").lower() for item in inventory]
        target = random.choice(KEYWORDS)
        log.info(f"Discovery Phase [{i+1}/{max_discoveries_per_run}] Targeting: {target}")
        prompt = f"""
        Use Google Search to find detailed information about ONE specific Cultural Heritage, local folklore, or traditional community practice using this keyword/concept: "{target}".
        Ignore these already known elements: {existing_names[:15]}...
        
        IMPORTANT INSTRUCTIONS:
        1. The element DOES NOT need to be officially recognized by UNESCO. It can be a local tradition, unregistered heritage, rare recipe, or community practice found on local blogs or regional news.
        2. DO NOT output any links containing 'vertexaisearch.cloud.google.com' or 'grounding-api-redirect'. Output the direct, true website URL (e.g. wikipedia.org, localnews.com, etc).
        3. Analyze the element, its location, its shared heritage connections with other countries/regions, and its process/recipe.
        4. Output ALL data values strictly in ENGLISH, and keep all JSON keys strictly in English.
        5. If you CANNOT find a detailed step-by-step process/recipe, set "resume_tata_cara" to null and "completion_status" to "INCOMPLETE".
        6. If you find all information, set "completion_status" to "COMPLETE".
        
        Output strictly as a JSON ARRAY containing ONE highly detailed object with this structure:
        [
          {{
            "id": "will_be_generated",
            "element_name": "...",
            "category": "Culinary Traditions | Traditional Craftsmanship | Performing Arts | Oral Traditions | Social Practices & Rituals",
            "thumbnail_url": "",
            "source_urls": ["url1"],
            "scraped_at": "{datetime.now().isoformat()}Z",
            "location": {{ 
                        "country": "...", 
                        "provinces": ["..."],
                        "lat": null, 
                        "lng": null 
        }},
            "resume_analisa": {{ "description": "...", "cultural_significance": "...", "gemini_tags": ["..."] }},
            "resume_tata_cara": {{ "type": "...", "materials_and_tools": ["..."], "step_by_step": ["..."] }},
            "shared_heritage_detection": {{ "is_shared": true/false, "confidence_score": 0.0-1.0, "related_elements": [{{ "country": "...", "element_name": "...", "relationship_reason": "..." }}] }},
            "completion_status": "COMPLETE or INCOMPLETE"
          }}
        ]
        """
        
        new_items = call_gemini(api_key, prompt)
        
       # PERBAIKAN: Jarak spasi di bawah ini sudah sejajar dengan 'new_items'
        if isinstance(new_items, list):
            for item in new_items:
                name = item.get("element_name", "Unknown")
                if name.lower() not in existing_names:
                    item["id"] = generate_id(name)
                    
                    # --- LOGIKA KOORDINAT ---
                    loc = item.get("location", {})
                    country = loc.get("country", "")
                    provinces = loc.get("provinces", [])
                    search_query = f"{provinces[0]}, {country}" if provinces else country
                    
                    lat, lng = get_coordinates(search_query)
                    if lat is None:
                        lat, lng = get_coordinates(country)
                    
                    item["location"]["lat"] = lat
                    item["location"]["lng"] = lng
                    
                    # Logika thumbnail
                    url_to_screenshot = item.get("source_urls", [""])[0] if item.get("source_urls") else ""
                    if not item.get("thumbnail_url"):
                        item["thumbnail_url"] = get_screenshot_url(url_to_screenshot, name)
                    
                    inventory.append(item)
                    discovered_count += 1
                    log.info(f"Discovered: {name} (Coords: {lat}, {lng})")
        
        time.sleep(5) 
                
    return discovered_count

# ======================================================================
# QUARTERLY JOURNAL / RESUME GENERATOR (JSON ONLY - ENGLISH)
# ======================================================================
def generate_quarterly_resume(api_key, inventory):
    # Tentukan Kuartal Saat Ini
    now = datetime.now()
    quarter_str = f"{now.year}-Q{(now.month - 1) // 3 + 1}"
    
    resume_db = {}
    
    # Load resume.json jika sudah ada
    if os.path.exists(RESUME_FILE):
        try:
            with open(RESUME_FILE, 'r', encoding='utf-8') as f:
                resume_db = json.load(f)
        except Exception:
            pass
            
    # Inisialisasi struktur untuk kuartal ini
    if quarter_str not in resume_db:
        resume_db[quarter_str] = {
            "status": "incomplete",
            "statistics": {},
            "content": {}
        }
        
    # Jika sudah complete, lewati proses
    if resume_db[quarter_str]["status"] == "complete":
        log.info(f"⏭️ Resume Jurnal untuk {quarter_str} sudah COMPLETE. Skip generasi.")
        return
        
    log.info(f"📝 Memulai penyusunan data Resume/Jurnal (Bahasa Inggris) untuk {quarter_str}...")
    
    # 1. Siapkan Statistik Data
    total_items = len(inventory)
    categories = {}
    for item in inventory:
        cat = item.get("category", "Unknown")
        categories[cat] = categories.get(cat, 0) + 1
        
    resume_db[quarter_str]["statistics"] = {
        "total_items": total_items,
        "categories_distribution": categories,
        "generated_at": now.strftime("%Y-%m-%d %H:%M:%S")
    }

    # Cek komparasi tren (English Version)
    previous_quarters = [q for q in resume_db.keys() if q != quarter_str]
    tren_prompt = "Focus on narrating the current cultural data collection."
    if previous_quarters:
        last_q = sorted(previous_quarters)[-1]
        tren_prompt = f"Compare with the previous quarter ({last_q}). Describe the data growth trend, focusing on developing categories and differences."

    # 2. PROMPT AI (Full English)
    prompt = f"""
    You are a Digital Anthropologist tasked with writing the Intangible Cultural Heritage Visual Journal for Quarter {quarter_str}.
    Current Statistics: Total of {total_items} cultural entities. Category distribution: {json.dumps(categories)}.
    {tren_prompt}
    
    Your task is to generate a structured narrative. You MUST include a "UNESCO Periodic Report" section that fictitiously discusses institutional capacity and legislative frameworks based on the data.
    
    The structure MUST exactly match this JSON format:
    {{
        "title": "Invisible Footprints: Visual Narrative of Cultural Heritage Quarter {quarter_str}",
        "abstract": "Abstract paragraph summarizing the findings...",
        "sections": {{
            "prologue": {{
                "title": "1. Prologue: The Common Thread of Civilization",
                "dropcap": "The first single letter of the prologue paragraph (e.g., 'W')",
                "text": "The rest of the prologue paragraph text..."
            }},
            "anatomy": {{
                "title": "2. Anatomy of Tradition: Creativity, Craft, and Spirit",
                "text": "Narrative regarding category dominance and data statistics..."
            }},
            "shared_heritage": {{
                "title": "3. Echoes Across Borders: Shared Heritage Network",
                "text": "Narrative about relationships between countries (e.g., silk, indigo dyeing, migration routes)..."
            }},
            "periodic_report": {{
                "title": "4. Status of Convention Implementation (Periodic Report)",
                "text": "Official report style similar to UNESCO Periodic Report regarding safeguarding, legislation, etc..."
            }},
            "epilogue": {{
                "title": "5. Epilogue",
                "text": "Philosophical concluding thoughts..."
            }}
        }}
    }}
    """
    
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    headers = {'Content-Type': 'application/json', 'x-goog-api-key': api_key}
    
    # Payload yang diperkuat (menggunakan responseMimeType untuk mencegah API bingung)
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.5, 
            "maxOutputTokens": 8192,
            "responseMimeType": "application/json"
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        raw_text = result['candidates'][0]['content']['parts'][0]['text']
        
        # Karena menggunakan responseMimeType, AI sudah terjamin mengirim JSON bersih
        ai_content = json.loads(raw_text)
        
        # Simpan ke dalam Database Resume
        resume_db[quarter_str]["status"] = "complete"
        resume_db[quarter_str]["content"] = ai_content
        
        with open(RESUME_FILE, 'w', encoding='utf-8') as f:
            json.dump(resume_db, f, indent=4, ensure_ascii=False)
            
        log.info(f"✅ Data Jurnal {quarter_str} berhasil digenerate dan disimpan ke resume.json!")
        
    except requests.exceptions.HTTPError as http_err:
        log.error(f"❌ API Error HTTP: {http_err}")
        # Menangkap alasan spesifik dari Google jika gagal lagi
        log.error(f"Detail Penolakan Google Gemini: {response.text}") 
        with open(RESUME_FILE, 'w', encoding='utf-8') as f:
            json.dump(resume_db, f, indent=4, ensure_ascii=False)
            
    except Exception as e:
        log.error(f"❌ Gagal men-generate konten jurnal: {e}")
        with open(RESUME_FILE, 'w', encoding='utf-8') as f:
            json.dump(resume_db, f, indent=4, ensure_ascii=False)

# ======================================================================
# MAIN EXECUTION
# ======================================================================

def main():
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        log.error("GEMINI_API_KEY not found or empty!")
        return 

    try:
        db = load_db()
        inventory = db.get("inventory", [])
        
        # PHASE 0: Audit Data (Downgrade status if image is missing)
        audited = audit_inventory(inventory)
        
        # PHASE 1: Enrich Incomplete Data First
        enriched = enrich_incomplete_items(api_key, inventory)
        
        # PHASE 2: Discover New Data
        discovered = discover_new_items(api_key, inventory)
        
        db["inventory"] = inventory
        
        # PHASE 3: Generate Quarterly Resume / Journal
        generate_quarterly_resume(api_key, inventory)
        
        # Save if there's any modification
        if audited > 0 or enriched > 0 or discovered > 0:
            save_db(db)
            log.info(f"✅ Run Complete. Audited: {audited}, Enriched: {enriched}, Discovered: {discovered}. Total DB: {len(inventory)}")
        else:
            log.info("Run Complete. No new data added or enriched.")

    except Exception as e:
        log.error(f"Fatal Error during main execution: {e}")

if __name__ == "__main__":
    main()
