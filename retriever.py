import re
import csv
import datetime
import shutil
from pathlib import Path
import io

DEFAULT_RECORDS = {
    # Simple yes/no records
    "yes": "Record 1: Look up for YES",
    "no": "Record 2: Look up for NO",

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


def _load_records() -> dict[str, str]:
    """Load records from a CSV file named 'records.csv' located next to this module.

    CSV format: key,value (no header required). If the file is missing or cannot be
    read, the `DEFAULT_RECORDS` will be used as a fallback.
    """
    csv_path = Path(__file__).with_name("records.csv")
    if not csv_path.exists():
        return DEFAULT_RECORDS.copy()

    records: dict[str, str] = {}
    try:
        with csv_path.open(newline='', encoding='utf-8') as fh:
            reader = csv.reader(fh)
            for row in reader:
                if not row:
                    continue
                key = str(row[0]).strip().lower()
                if not key:
                    continue
                value = str(row[1]).strip() if len(row) > 1 else ""
                records[key] = value
    except Exception:
        # On any error, fall back to the default hard-coded records
        return DEFAULT_RECORDS.copy()

    # If CSV was empty, fall back to defaults
    if not records:
        return DEFAULT_RECORDS.copy()

    return records


RECORDS = _load_records()


def reload_records() -> dict[str, str]:
    """Reload records from the CSV file and update the module-level RECORDS.

    Returns the updated records mapping.
    """
    # Mutate the existing RECORDS dict so other modules holding a reference
    # to it (for example `from retriever import RECORDS`) will observe updates.
    new = _load_records()
    RECORDS.clear()
    RECORDS.update(new)
    return RECORDS


def validate_csv_content(content: str) -> tuple[dict[str, str] | None, str | None]:
    """Validate CSV content conforms to expected 'key,value' rows.

    Rules:
    - Optional header row 'key,value' (case-insensitive) is allowed.
    - Each data row must have a non-empty `key` and may have an empty `value`.
    - Keys are normalized to lowercase and must match [a-z0-9]+ (no spaces or punctuation).
    - At least one valid record is required.

    Returns (records_dict, None) on success or (None, error_message) on failure.
    """
    reader = csv.reader(io.StringIO(content))
    records: dict[str, str] = {}
    seen_any = False
    for row_index, row in enumerate(reader, start=1):
        if not row or all(not cell.strip() for cell in row):
            continue
        # Allow header row `key,value`
        if not seen_any:
            first = str(row[0]).strip().lower()
            second = str(row[1]).strip().lower() if len(row) > 1 else ""
            if first == "key" and second == "value":
                # skip header
                continue
        # Require at least two columns per data row
        if len(row) < 2:
            return None, f"CSV row {row_index} must contain exactly 2 comma-separated values"
        key = str(row[0]).strip().lower()
        if not key:
            return None, f"Empty key on CSV row {row_index}"
        if not re.match(r"^[a-z0-9]+$", key):
            return None, f"Invalid key '{key}' on CSV row {row_index}; keys must be letters/numbers only"
        value = str(row[1]).strip()
        records[key] = value
        seen_any = True

    if not seen_any:
        return None, "CSV contains no records"

    return records, None


def write_records_csv(content: str) -> None:
    """Write raw CSV content to the module's `records.csv` file.

    This will overwrite the file. Caller should call `reload_records()` after writing.
    """
    csv_path = Path(__file__).with_name("records.csv")
    tmp_path = csv_path.with_suffix(".tmp")
    # Write to a temporary file first to ensure we don't lose the original on error
    try:
        tmp_path.write_text(content, encoding="utf-8")
        # If there is an existing CSV, copy it to a timestamped backup in backups/
        if csv_path.exists():
            ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            backups_dir = csv_path.parent / "backups"
            backups_dir.mkdir(parents=True, exist_ok=True)
            backup = backups_dir / f"records.csv.bak.{ts}"
            shutil.copy2(csv_path, backup)
        # Atomically replace (or create) the target file
        tmp_path.replace(csv_path)
    finally:
        # Ensure temporary file is removed if it still exists
        try:
            if tmp_path.exists():
                tmp_path.unlink()
        except Exception:
            pass

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