RECORDS = {
    "yes": "Record 1: User confirmed YES",
    "no": "Record 2: User confirmed NO",

    "dog": "Record 3: Animal category — dog",
    "cat": "Record 4: Animal category — cat",
    "bird": "Record 5: Animal category — bird",

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
    "rice": "Record 20: Food category — rice"
}

def get_record(user_text: str) -> str:
    key = (user_text or "").strip().lower()

    if key in RECORDS:
        return RECORDS[key]

    return f"No match found for '{user_text}'."