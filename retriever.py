import re

RECORDS = {
    "yes": "Record 1: User confirmed YES",
    "no": "Record 2: User confirmed NO",

    "dog": "Record 3: Animal category — dog",
    "cat": "Record 4: Animal category — cat",
    "rat": "Record 5: Animal category — rat",

    "car": "Record 6: Vehicle category — car",
    "bus": "Record 7: Vehicle category — bus",
    "train": "Record 8: Vehicle category — train",

    "red": "Record 9: Color category — red",
    "blue": "Record 10: Color category — blue",
    "green": "Record 11: Color category — green",

    "tree": "Record 12: Nature category — tree",
    "river": "Record 13: Nature category — river",
    "mountain": "Record 14: Nature category — mountain",

    "math": "Record 15: Subject category — math",
    "science": "Record 16: Subject category — science",
    "history": "Record 17: Subject category — history",

    "pizza": "Record 18: Food category — pizza",
    "burger": "Record 19: Food category — burger",
    "rice": "Record 20: Food category — rice",
}

def _tokenize(text: str) -> list[str]:
    # lowercase and extract words (letters/numbers only)
    words = re.findall(r"[a-z0-9]+", (text or "").lower())
    return words

def _normalize(word: str) -> str:
    # very simple plural handling: dogs->dog, cats->cat, trees->tree
    if word.endswith("s") and len(word) > 3:
        return word[:-1]
    return word

def get_record(user_text: str) -> str:
    raw = (user_text or "").strip()

    # Commands
    if raw.lower() in ("/help", "help", "/list", "list", "/words", "words"):
        return "Try one of these keywords: " + ", ".join(sorted(RECORDS.keys()))

    # Exact match first
    key = raw.lower()
    if key in RECORDS:
        return RECORDS[key]

    # Keyword search inside sentences + plural normalization
    tokens = [_normalize(w) for w in _tokenize(raw)]
    matches = []
    for t in tokens:
        if t in RECORDS and t not in matches:
            matches.append(t)

    if matches:
        # Return multiple records if multiple matches
        lines = [RECORDS[m] for m in matches]
        return "Matches:\n" + "\n".join(lines)

    return f"No match found for '{user_text}'. Type 'list' to see all keywords."