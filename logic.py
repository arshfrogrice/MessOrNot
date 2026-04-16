import re


taste_ratings = {
    "paneer": 9,
    "rajma": 8,
    "chole": 8,
    "chola": 8,
    "dal": 6,
    "roti": 6,
    "rice": 6,
    "lauki": 5,
    "bengan": 4,
    "tinda": 3,
    "bhindi": 7,
    "aloo": 7,
    "poha": 7,
    "maggi": 9,
    "dalia": 7,
    "sprouts": 8,
    "chole bhature": 9,
    "chicken": 10,
    "soya-been curry": 8,
    "tori": 6,
    "gobhi": 6,
    "chilla": 7,
    "kulcha": 8,
    "vada sambhar": 9,
    "chocos": 8,
    "milk": 6,
    "tea": 5,
    "coffee": 5,
    "bread": 5,
    "bournvita": 5,
    "salad": 7,
    "onion": 4,
    "hari mirch": 3,
    "lemon": 4,
    "saunf": 3,
    "achar": 4,
    "butter": 6,
    "egg": 7,
    "peanut butter": 8,
    "dal makhani": 9,
    "malai kofta": 9,
    "egg curry": 8,
    "garlic rice": 7,
    "papdi chat": 8,
    "fruit custard": 8,
    "kheer": 8,
    "jalebi rabdi": 9,
    "rabdi": 8,
    "ice cream": 8,
    "sandwich": 7,
    "burger": 7,
    "roll": 8,
    "omelette": 8,
    "momos": 7,
    "chowmein": 7,
    "macroni": 6,
    "pakoda": 6,
    "pav bhaji": 8,
    "peanut chaat": 7,
    "bread omelette": 8,
    "egg roll": 8,
    "paneer roll": 9,
}


nutrition = {
    "paneer": 10,
    "rajma": 9,
    "chole": 8,
    "chola": 8,
    "dal": 7,
    "egg": 8,
    "roti": 5,
    "rice": 5,
    "poha": 5,
    "milk": 8,
    "dalia": 4,
    "sprouts": 8,
    "salad": 4,
    "chicken": 10,
    "peanut butter": 9,
    "lauki": 3,
    "bengan": 3,
    "tinda": 3,
    "bhindi": 4,
    "aloo": 4,
    "maggi": 2,
    "chole bhature": 7,
    "soya-been curry": 9,
    "tori": 3,
    "gobhi": 4,
    "chilla": 6,
    "kulcha": 4,
    "vada sambhar": 7,
    "chocos": 3,
    "tea": 1,
    "coffee": 1,
    "bread": 3,
    "bournvita": 2,
    "onion": 1,
    "hari mirch": 1,
    "lemon": 1,
    "saunf": 1,
    "achar": 1,
    "butter": 1,
    "dal makhani": 8,
    "malai kofta": 6,
    "egg curry": 8,
    "garlic rice": 5,
    "papdi chat": 3,
    "fruit custard": 3,
    "kheer": 4,
    "jalebi rabdi": 4,
    "rabdi": 4,
    "ice cream": 2,
    "sandwich": 5,
    "burger": 5,
    "roll": 5,
    "omelette": 8,
    "momos": 5,
    "chowmein": 4,
    "macroni": 4,
    "pakoda": 2,
    "pav bhaji": 5,
    "peanut chaat": 7,
    "bread omelette": 8,
    "egg roll": 8,
    "paneer roll": 9,
}


DEFAULT_MEAL_ITEMS = {
    "Breakfast": [
        "Milk 250 Ml.",
        "Tea",
        "Coffee",
        "Bread White & Brown",
        "Dalia",
        "Sprouts",
        "Bournvita",
    ],
    "Lunch": [
        "Salad / Onion",
        "Hari Mirch",
        "Lemon",
        "Butter Roti",
        "Rice",
        "Saunf",
        "Achar",
    ],
    "Dinner": [
        "Salad / Onion",
        "Butter Roti",
        "Hari Mirch",
        "Lemon",
        "Rice",
        "Saunf",
        "Achar",
    ],
}


ALIASES = {
    "paneer": [
        "paneer",
        "kadai paneer",
        "shahi paneer",
        "matar paneer",
        "paneer butter masala",
    ],
    "rajma": ["rajma", "rajmah", "rajma masala"],
    "chole": ["chole", "chola", "chhole", "chana", "chana masala"],
    "chola": ["chole", "chola", "chhole", "chana", "chana masala"],
    "dal": [
        "dal",
        "dal mix",
        "dalmix",
        "mix dal",
        "dal tadka",
        "dal fry",
        "dal makhani",
        "dal muradabadi",
        "dal navratan",
        "dal punjabi",
        "dal urad",
        "dal chana",
        "dal moong",
        "dal lasun",
    ],
    "roti": ["roti", "chapati", "phulka", "butter roti", "tandoori roti"],
    "rice": [
        "rice",
        "jeera rice",
        "mint rice",
        "tamarind rice",
        "tamrind rice",
        "garlic rice",
        "onion rice",
        "tahri",
        "masala rice",
        "khichdi",
    ],
    "lauki": ["lauki", "bottle gourd"],
    "bengan": ["bengan", "baingan", "brinjal", "eggplant"],
    "tinda": ["tinda", "apple gourd"],
    "bhindi": ["bhindi", "okra"],
    "aloo": ["aloo", "alu", "potato"],
    "poha": ["poha"],
    "maggi": ["maggi", "maggie", "dry maggi"],
    "dalia": ["dalia", "daliya", "porridge"],
    "sprouts": ["sprouts", "special sprouts", "sprouted moong"],
    "chole bhature": ["chole bhature", "chola bhature", "bhature"],
    "chicken": ["chicken", "chicken curry", "chicken kadahi", "chicken kadhai"],
    "soya-been curry": [
        "soya bean curry",
        "soya-been curry",
        "soyabean curry",
        "soy bean curry",
    ],
    "tori": ["tori", "tori masala", "turai", "ridge gourd"],
    "gobhi": ["gobhi", "gobi", "cauliflower"],
    "chilla": ["chilla", "cheela", "besan chilla"],
    "kulcha": ["kulcha", "kulch", "kulcha matar"],
    "vada sambhar": ["vada sambhar", "vada sambar", "medu vada sambar"],
    "chocos": ["chocos", "choco", "cornflakes", "cereal"],
    "milk": ["milk", "milk 250 ml"],
    "tea": ["tea", "chai"],
    "coffee": ["coffee"],
    "bread": ["bread", "brown bread", "white bread"],
    "bournvita": ["bournvita", "bourn vita"],
    "salad": ["salad", "green salad"],
    "onion": ["onion", "pyaz"],
    "hari mirch": ["hari mirch", "green chilli", "green chili", "mirchi"],
    "lemon": ["lemon", "nimbu"],
    "saunf": ["saunf", "fennel"],
    "achar": ["achar", "pickle"],
    "butter": ["butter", "makhan"],
    "egg": ["egg", "boiled egg", "egg curry", "anda", "anda curry"],
    "peanut butter": ["peanut butter"],
    "dal makhani": ["dal makhani", "makhani dal"],
    "malai kofta": ["malai kofta", "kofta"],
    "egg curry": ["egg curry", "anda curry"],
    "garlic rice": ["garlic rice"],
    "papdi chat": ["papdi chat", "papri chat"],
    "fruit custard": ["fruit custard", "custard"],
    "kheer": ["kheer", "sawai kheer", "sevai kheer", "sawal kheer"],
    "jalebi rabdi": ["jalebi rabdi", "jalebi with rabdi"],
    "rabdi": ["rabdi"],
    "ice cream": ["ice cream", "icecream"],
    "sandwich": ["sandwich", "grilled sandwich"],
    "burger": ["burger"],
    "roll": ["roll", "wrap"],
    "omelette": ["omelette", "omlette", "omelet"],
    "momos": ["momos", "momo"],
    "chowmein": ["chowmein", "chowmin", "chowmeen", "noodles"],
    "macroni": ["macroni", "macaroni"],
    "pakoda": ["pakoda", "pakora"],
    "pav bhaji": ["pav bhaji", "vada pav", "vada pay"],
    "peanut chaat": ["peanut chaat", "peanut chat"],
    "bread omelette": ["bread omelette", "bread omlette", "bread omelet"],
    "egg roll": ["egg roll", "double egg roll"],
    "paneer roll": ["paneer roll", "paneer cheese roll"],
}


def _normalize_text(text):
    cleaned = str(text).strip().lower()
    cleaned = cleaned.replace("&", " and ")
    cleaned = cleaned.replace("/", " ")
    cleaned = cleaned.replace("-", " ")
    cleaned = re.sub(r"[^a-z0-9\s]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _normalize_items(items):
    normalized = []
    for item in items:
        if not item:
            continue
        normalized.append(_normalize_text(item))
    return normalized


def _normalize_mapping_keys(mapping):
    return {_normalize_text(key): value for key, value in mapping.items()}


NORMALIZED_TASTE_RATINGS = _normalize_mapping_keys(taste_ratings)
NORMALIZED_NUTRITION = _normalize_mapping_keys(nutrition)
NORMALIZED_ALIASES = {
    _normalize_text(keyword): [_normalize_text(alias) for alias in aliases]
    for keyword, aliases in ALIASES.items()
}
PREMIUM_DINNER_KEYWORDS = [
    "paneer",
    "kadai paneer",
    "chicken",
    "chicken curry",
    "chicken kadahi",
    "dal makhani",
    "dal muradabadi",
    "malai kofta",
    "egg curry",
    "egg curry malai kofta",
    "rajma",
    "chole bhature",
]
MEAL_PREFERENCE_KEYWORDS = {
    "Breakfast": {
        "poha": 2.2,
        "omelette": 2.0,
        "egg": 1.8,
        "bread omelette": 2.2,
        "peanut chaat": 0.8,
        "milk": 1.0,
        "tea": 0.5,
        "coffee": 0.4,
        "sandwich": 1.0,
        "maggi": 0.8,
    },
    "Lunch": {
        "chole": 1.8,
        "kulcha": 1.4,
        "chole bhature": 1.6,
        "egg": 1.8,
        "peanut chaat": 1.8,
        "sandwich": 1.4,
        "burger": 1.0,
        "momos": 1.0,
        "chowmein": 1.0,
        "macroni": 0.8,
        "pav bhaji": 1.4,
    },
    "Dinner": {
        "maggi": 2.2,
        "paneer": 2.6,
        "paneer roll": 3.0,
        "egg": 2.0,
        "egg roll": 2.6,
        "bread omelette": 2.4,
        "omelette": 2.0,
        "sandwich": 1.2,
        "momos": 1.0,
        "chowmein": 1.2,
        "macroni": 1.0,
        "pav bhaji": 1.3,
    },
}
ALLOWED_CANTEEN_CATEGORIES = {
    "Breakfast": {"Beverages", "Snacks", "Eggs", "Breads", "Sandwich", "Maggi"},
    "Lunch": {"Snacks", "Sandwich", "Burger", "Continental", "Eggs", "Momos", "Maggi"},
    "Dinner": {"Roll", "Eggs", "Continental", "Burger", "Sandwich", "Momos", "Maggi"},
}


def _expand_items(items, meal_name=None):
    actual_items = list(items)
    default_items = DEFAULT_MEAL_ITEMS.get(meal_name, [])
    return actual_items, default_items


def _matches_keyword(item, keyword):
    normalized_keyword = _normalize_text(keyword)
    if normalized_keyword in item:
        return True

    for alias in NORMALIZED_ALIASES.get(normalized_keyword, []):
        if alias in item:
            return True

    return False


def _match_item_values(normalized_items, normalized_mapping):
    matched_values = []
    for item in normalized_items:
        matches = [
            value
            for keyword, value in normalized_mapping.items()
            if _matches_keyword(item, keyword)
        ]
        if matches:
            matched_values.append(max(matches))
    return matched_values


def _premium_dinner_count(actual_items):
    normalized_items = _normalize_items(actual_items)
    matched_keywords = set()

    for item in normalized_items:
        for keyword in PREMIUM_DINNER_KEYWORDS:
            if _matches_keyword(item, keyword):
                matched_keywords.add(keyword)

    return len(matched_keywords)


def taste_score(items, meal_name=None):
    actual_items, default_items = _expand_items(items, meal_name)
    actual_scores = _match_item_values(
        _normalize_items(actual_items),
        NORMALIZED_TASTE_RATINGS,
    )
    default_scores = _match_item_values(
        _normalize_items(default_items),
        NORMALIZED_TASTE_RATINGS,
    )

    if not actual_scores and not default_scores:
        return 5.0

    weighted_total = (sum(actual_scores) * 2.0) + (sum(default_scores) * 0.75)
    weight = (len(actual_scores) * 2.0) + (len(default_scores) * 0.75)
    score = weighted_total / weight

    if meal_name == "Dinner":
        premium_count = _premium_dinner_count(actual_items)
        if premium_count >= 3:
            score += 1.8
        elif premium_count >= 2:
            score += 1.0

    return round(min(score, 10), 2)


def nutrition_score(items, meal_name=None):
    actual_items, default_items = _expand_items(items, meal_name)
    actual_values = _match_item_values(
        _normalize_items(actual_items),
        NORMALIZED_NUTRITION,
    )
    default_values = _match_item_values(
        _normalize_items(default_items),
        NORMALIZED_NUTRITION,
    )

    if not actual_values and not default_values:
        return 4.0

    weighted_total = sum(actual_values) + (sum(default_values) * 0.6)
    weighted_count = len(actual_values) + (len(default_values) * 0.6)
    avg_protein = weighted_total / weighted_count

    density_component = min(avg_protein / 10 * 6.5, 6.5)
    volume_component = min(weighted_total / 32 * 3.5, 3.5)
    score = density_component + volume_component

    if meal_name == "Dinner":
        premium_count = _premium_dinner_count(actual_items)
        if premium_count >= 3:
            score += 1.6
        elif premium_count >= 2:
            score += 0.8

    return round(min(score, 10), 2)


def final_score(items, meal_name=None):
    taste = taste_score(items, meal_name=meal_name)
    nutrition_value = nutrition_score(items, meal_name=meal_name)
    final = round((taste * 0.6) + (nutrition_value * 0.4), 2)
    return final, taste, nutrition_value


def verdict(score):
    if score >= 8:
        return "🔥🔥 GOATED MEAL - ABSOLUTELY EAT IN MESS"
    if score >= 6:
        return "👍 Decent meal, can consider eating in mess"
    return "💀 Skip this meal - look for a better option outside"


def canteen_recommendations(menu_items, meal_name, limit=5, max_price=60):
    ranked = []

    for item in menu_items:
        name = item["item"]
        price = item["price"]
        category = item.get("category", "")
        if price > max_price:
            continue
        if meal_name in ALLOWED_CANTEEN_CATEGORIES:
            if category not in ALLOWED_CANTEEN_CATEGORIES[meal_name]:
                continue

        final, taste, nutrition_value = final_score([name])
        normalized_name = _normalize_text(name)
        preference_bonus = 0
        for keyword, bonus in MEAL_PREFERENCE_KEYWORDS.get(meal_name, {}).items():
            if _matches_keyword(normalized_name, keyword):
                preference_bonus += bonus

        affordability = max(0, (60 - price) / 12)
        recommendation_score = round(
            (final * 0.55) + (taste * 0.15) + (nutrition_value * 0.15) + affordability + preference_bonus,
            2,
        )
        ranked.append(
            {
                "item": name,
                "price": price,
                "taste": taste,
                "nutrition": nutrition_value,
                "final": final,
                "recommendation_score": recommendation_score,
            }
        )

    ranked.sort(
        key=lambda item: (
            -item["recommendation_score"],
            item["price"],
            -item["nutrition"],
        )
    )
    return ranked[:limit]
