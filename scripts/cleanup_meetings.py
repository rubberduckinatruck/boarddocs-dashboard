import os
import glob
import json

# --------- SETTINGS ----------
BASE_PATH = r'C:\Users\gturnbull\Desktop\AGENDA_BoardDocs\RawData'
OUTPUT_DIR = r'C:\Users\gturnbull\Desktop\AGENDA_BoardDocs'
YEAR_RANGE = range(2013, 2026)  # inclusive: 2013 to 2025
CATEGORY_MAP = [
    ("call to order", "Call to Order"),
    ("pledge of allegiance", "Pledge of Allegiance"),
    ("information", "Information"),
    ("discussion", "Information"),
    ("presentation", "Presentation"),
    ("recognition", "Recognition/Celebration"),
    ("public hearing", "Public Hearing"),
    ("approval of minutes", "Approval of Minutes"),
    ("action items", "Action Items"),
    ("consent agenda", "Consent Agenda Items"),
    ("future agenda", "Future Agenda Items"),
    ("adjourn", "Adjournment"),
    ("executive session", "Executive Session"),
    ("oath of office", "Oath of Office/Election of Governing Board Officers"),
    ("advisory committee", "Board Advisory Committee"),
]
NON_VOTING_TYPES = {"Procedural", "Presentation", "Information", "Discussion"}
NON_VOTING_TITLE_KEYWORDS = [
    "call to order", "pledge of allegiance", "recognition", "summary", "work study",
    "future agenda", "welcome", "hearing", "adjourn", "presentation"
]
TAG_KEYWORDS = {
    "union": ["union", "association", "afdea", "teachers union", "aea"],
    "equity": ["equity", "equal opportunity", "inclusion"],
    "grievance": ["grievance", "grievances"],
    "compensation": ["salary", "wage", "compensation", "stipend", "pay scale"],
    "overtime": ["overtime"],
    "benefits": ["benefits", "insurance", "medical", "health care"],
    "meet and confer": ["meet and confer", "negotiation", "bargain", "bargaining"],
    "privatization": ["privatization", "outsourcing", "contracted services"],
    "calendar": ["calendar", "school year", "start date", "end date"],
    "discipline": ["discipline", "suspension", "expulsion", "student conduct"],
    "class size": ["class size", "pupil-teacher ratio"],
    "override": ["override", "budget override"],
    "termination": ["termination", "dismissal", "rif", "reduction in force"],
    "safety": ["safety", "security", "covid", "emergency", "health"],
}

def normalize_category(cat):
    if not cat: return "Other"
    cat_l = cat.lower()
    for patt, norm in CATEGORY_MAP:
        if patt in cat_l:
            return norm
    return cat.strip()

def is_voting_item(item):
    type_ = (item.get('type') or '').strip()
    if type_ in NON_VOTING_TYPES:
        return False
    title = (item.get('title') or '').lower()
    cat = (item.get('category') or '').lower()
    for word in NON_VOTING_TITLE_KEYWORDS:
        if word in title or word in cat:
            return False
    votes = item.get('motion_and_voting', {}).get('votes', [])
    if not votes or len(votes) == 0:
        return False
    return True

def find_tags(item):
    tags = set()
    text_fields = [
        str(item.get('title', '')), str(item.get('category', '')), str(item.get('recommendedAction', '')),
        *(item.get('narratives',{}) or {}).values()
    ]
    fulltext = " ".join(text_fields).lower()
    for tag, words in TAG_KEYWORDS.items():
        for word in words:
            if word in fulltext:
                tags.add(tag)
    return sorted(tags)

def dedupe_agenda_items(items):
    item_map = {}
    for item in items:
        key = (item.get('number','').strip(), item.get('title','').strip())
        if key not in item_map:
            item_map[key] = item
    return list(item_map.values())

def load_meeting_file(filepath):
    with open(filepath, encoding='utf-8-sig') as f:
        return json.load(f)

def save_json(obj, outpath):
    with open(outpath, 'w', encoding='utf-8') as outf:
        json.dump(obj, outf, indent=2, ensure_ascii=False)

def clean_meeting(meeting):
    # Dedupe and clean all agenda items in a single meeting
    agenda_items = dedupe_agenda_items(meeting.get('agenda_items', []))
    cleaned_items = []
    for item in agenda_items:
        item['clean_category'] = normalize_category(item.get('category', ''))
        item['is_voting_item'] = is_voting_item(item)
        item['tags'] = find_tags(item)
        cleaned_items.append(item)
    meeting['agenda_items'] = cleaned_items
    return meeting

def main():
    for year in YEAR_RANGE:
        year_folder = os.path.join(BASE_PATH, str(year))
        if not os.path.isdir(year_folder):
            print(f"Skipping missing folder: {year_folder}")
            continue
        json_files = sorted(glob.glob(os.path.join(year_folder, '*.json')))
        if not json_files:
            print(f"⚠️  No JSON files found in {year_folder}. Skipping.")
            continue
        print(f"📅 YEAR {year}: Found {len(json_files)} files. Processing...")

        seen_meetings = set()
        cleaned_meetings = []
        for file in json_files:
            try:
                meeting = load_meeting_file(file)
            except Exception as e:
                print(f"Error loading {file}: {e}")
                continue
            m_id = meeting.get('meeting_id') or (meeting.get('meeting_date','') + "|" + meeting.get('meeting_title',''))
            if m_id in seen_meetings:
                continue
            seen_meetings.add(m_id)
            cleaned_meeting = clean_meeting(meeting)
            cleaned_meetings.append(cleaned_meeting)

        # Output one file per year
        out_file = os.path.join(OUTPUT_DIR, f"{year}.json")
        save_json(cleaned_meetings, out_file)
        print(f"✅ Saved {len(cleaned_meetings)} cleaned meetings to {out_file}")

if __name__ == "__main__":
    main()
