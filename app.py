import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from logic import canteen_recommendations, final_score, verdict
from mess_data import (
    get_day_canteen_data,
    get_night_canteen_data,
    get_sarojini_canteen_data,
    get_vigyan_canteen_data,
    parse_menu,
)


DATA_DIR = Path("data")
MENU_JSON_PATH = DATA_DIR / "mess_menu.json"
DEFAULT_IMAGE_PATH = Path("menu.jpg")
UPLOADED_IMAGE_PATH = DATA_DIR / "uploaded_menu_image.jpg"
DAY_CANTEEN_IMAGE_PATH = Path("day_canteen.jpeg")
NIGHT_CANTEEN_IMAGE_PATHS = [Path("night_canteen_1.jpeg"), Path("night_canteen_2.jpeg")]
SAROJINI_CANTEEN_IMAGE_PATH = Path("sarojini_canteen.jpeg")
VIGYAN_CANTEEN_IMAGE_PATH = Path("vigyan_canteen.jpeg")
MEAL_COLUMNS = ["Breakfast", "Lunch", "Dinner"]


def split_items(items_text):
    if not items_text:
        return []
    return [item.strip() for item in items_text.split("|") if item.strip()]


def load_menu_from_parser(image_path: Path):
    day_table, date_range, bhawan_name = parse_menu(image_path)
    menu = {}

    for record in day_table.to_dict(orient="records"):
        day = record["Day"]
        menu[day] = {
            "Date": record["Date"],
            "Breakfast": split_items(record["Breakfast"]),
            "Lunch": split_items(record["Lunch"]),
            "Dinner": split_items(record["Dinner"]),
        }

    return menu, date_range, bhawan_name


def load_menu():
    if MENU_JSON_PATH.exists():
        with open(MENU_JSON_PATH, "r", encoding="utf-8") as file:
            menu = json.load(file)

        metadata_path = UPLOADED_IMAGE_PATH if UPLOADED_IMAGE_PATH.exists() else DEFAULT_IMAGE_PATH
        if metadata_path.exists():
            _, date_range, bhawan_name = load_menu_from_parser(metadata_path)
            return menu, date_range, bhawan_name
        return menu, "", ""

    if DEFAULT_IMAGE_PATH.exists():
        return load_menu_from_parser(DEFAULT_IMAGE_PATH)

    return {}, "", ""


def save_menu(menu):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(MENU_JSON_PATH, "w", encoding="utf-8") as file:
        json.dump(menu, file, indent=4)


def show_score_card(day, meals, show_canteen_actions=True):
    st.subheader(day)
    for meal in MEAL_COLUMNS:
        items = meals.get(meal, [])
        score, taste, nutrition = final_score(items, meal_name=meal)

        st.markdown(f"**{meal}**")
        metric_columns = st.columns(3)
        metric_columns[0].metric("Final Score", f"{score}/10")
        metric_columns[1].metric("Taste Score", f"{taste}/10")
        metric_columns[2].metric("Nutrition Score", f"{nutrition}/10")
        st.write(verdict(score))
        st.progress(min(score / 10, 1.0))
        if show_canteen_actions:
            show_canteen_button(day, meal)
    st.divider()


def show_menu_preview(day, meals):
    st.subheader(f"🍽️ Today's Menu: {day}")
    for meal in MEAL_COLUMNS:
        items = meals.get(meal, [])
        rendered_items = ", ".join(items) if items else "No items available"
        st.markdown(f"**{meal}:** {rendered_items}")
    st.divider()


def populate_editor_state(menu):
    for day, meals in menu.items():
        st.session_state[f"date_{day}"] = meals.get("Date", "")
        for meal in MEAL_COLUMNS:
            st.session_state[f"{meal}_{day}"] = ", ".join(meals.get(meal, []))


def ensure_editor_state(menu):
    for day, meals in menu.items():
        date_key = f"date_{day}"
        if date_key not in st.session_state or not st.session_state[date_key]:
            st.session_state[date_key] = meals.get("Date", "")

        for meal in MEAL_COLUMNS:
            meal_key = f"{meal}_{day}"
            if meal_key not in st.session_state or not st.session_state[meal_key]:
                st.session_state[meal_key] = ", ".join(meals.get(meal, []))


def toggle_menu_editor():
    next_state = not st.session_state.show_menu_editor
    st.session_state.show_menu_editor = next_state
    if next_state:
        populate_editor_state(st.session_state.menu)


def toggle_today_menu():
    st.session_state.show_today_menu = not st.session_state.show_today_menu


def render_editor(menu):
    updated_menu = {}

    for day, meals in menu.items():
        st.subheader(day)
        date_key = f"date_{day}"
        date_value = st.text_input(
            f"Date ({day})",
            value=st.session_state.get(date_key, meals.get("Date", "")),
            key=date_key,
        )

        updated_menu[day] = {"Date": date_value}

        for meal in MEAL_COLUMNS:
            meal_key = f"{meal}_{day}"
            edited = st.text_input(
                f"{meal} ({day})",
                value=st.session_state.get(meal_key, ", ".join(meals.get(meal, []))),
                key=meal_key,
            )
            updated_menu[day][meal] = [item.strip() for item in edited.split(",") if item.strip()]

    return updated_menu


def get_uploaded_file_signature(uploaded_file):
    return f"{uploaded_file.name}:{uploaded_file.size}"


def get_canteen_for_meal(meal):
    if meal == "Dinner":
        return st.session_state.day_canteen, "day"
    return st.session_state.night_canteen, "night"


def toggle_canteen_options(section_key):
    st.session_state[section_key] = not st.session_state.get(section_key, False)


def show_canteen_button(day, meal):
    if meal == "Lunch":
        col1, col2, col3, col4 = st.columns(4)

        day_button_key = f"show_day_canteen_{day}_{meal}"
        night_button_key = f"show_night_canteen_{day}_{meal}"
        sarojini_button_key = f"show_sarojini_canteen_{day}_{meal}"
        vigyan_button_key = f"show_vigyan_canteen_{day}_{meal}"

        col1.button(
            "🍜 Show Day Canteen Options",
            key=f"button_day_{day}_{meal}",
            use_container_width=True,
            on_click=toggle_canteen_options,
            args=(day_button_key,),
        )
        col2.button(
            "☕ Show Night Canteen Options",
            key=f"button_night_{day}_{meal}",
            use_container_width=True,
            on_click=toggle_canteen_options,
            args=(night_button_key,),
        )
        col3.button(
            "🥘 Show Sarojini Bhawan Day Canteen Options",
            key=f"button_sarojini_{day}_{meal}",
            use_container_width=True,
            on_click=toggle_canteen_options,
            args=(sarojini_button_key,),
        )
        col4.button(
            "🍲 Show Vigyan Kunj Day Canteen Options",
            key=f"button_vigyan_{day}_{meal}",
            use_container_width=True,
            on_click=toggle_canteen_options,
            args=(vigyan_button_key,),
        )

        if st.session_state.get(day_button_key, False):
            show_canteen_options(st.session_state.day_canteen, meal)
        if st.session_state.get(night_button_key, False):
            show_canteen_options(st.session_state.night_canteen, meal)
        if st.session_state.get(sarojini_button_key, False):
            show_canteen_options(st.session_state.sarojini_canteen, meal)
        if st.session_state.get(vigyan_button_key, False):
            show_canteen_options(st.session_state.vigyan_canteen, meal)
        return

    if meal == "Dinner":
        col1, col2, col3 = st.columns(3)
        day_button_key = f"show_day_canteen_{day}_{meal}"
        sarojini_button_key = f"show_sarojini_canteen_{day}_{meal}"
        vigyan_button_key = f"show_vigyan_canteen_{day}_{meal}"

        col1.button(
            "🍜 Show Day Canteen Options",
            key=f"button_day_{day}_{meal}",
            use_container_width=True,
            on_click=toggle_canteen_options,
            args=(day_button_key,),
        )
        col2.button(
            "🥘 Show Sarojini Bhawan Day Canteen Options",
            key=f"button_sarojini_{day}_{meal}",
            use_container_width=True,
            on_click=toggle_canteen_options,
            args=(sarojini_button_key,),
        )
        col3.button(
            "🍲 Show Vigyan Kunj Day Canteen Options",
            key=f"button_vigyan_{day}_{meal}",
            use_container_width=True,
            on_click=toggle_canteen_options,
            args=(vigyan_button_key,),
        )

        if st.session_state.get(day_button_key, False):
            show_canteen_options(st.session_state.day_canteen, meal)
        if st.session_state.get(sarojini_button_key, False):
            show_canteen_options(st.session_state.sarojini_canteen, meal)
        if st.session_state.get(vigyan_button_key, False):
            show_canteen_options(st.session_state.vigyan_canteen, meal)
        return

    canteen_data, canteen_key = get_canteen_for_meal(meal)
    button_key = f"show_{canteen_key}_canteen_{day}_{meal}"
    label = (
        "🍜 Show Day Canteen Options"
        if meal == "Dinner"
        else "☕ Show Night Canteen Options"
    )
    st.button(
        label,
        key=f"button_{canteen_key}_{day}_{meal}",
        use_container_width=True,
        on_click=toggle_canteen_options,
        args=(button_key,),
    )
    if st.session_state.get(button_key, False):
        show_canteen_options(canteen_data, meal)


def recommendation_reason(item_name, price, taste, nutrition):
    reasons = []
    if price <= 30:
        reasons.append("very cheap")
    elif price <= 40:
        reasons.append("budget-friendly")
    if nutrition >= 7:
        reasons.append("good protein")
    elif nutrition >= 5.5:
        reasons.append("decent nutrition")
    if taste >= 8:
        reasons.append("tasty pick")
    elif taste >= 6.5:
        reasons.append("solid taste")
    return ", ".join(reasons) if reasons else "balanced option"


def show_canteen_options(canteen_data, meal):
    st.markdown(f"**{canteen_data['name']}**")
    st.caption(f"Open: {canteen_data['hours']}")
    st.markdown("**Recommended cheap alternatives**")
    recommendations = canteen_recommendations(canteen_data["menu"], meal_name=meal, limit=5)
    for item in recommendations:
        reason = recommendation_reason(
            item["item"],
            item["price"],
            item["taste"],
            item["nutrition"],
        )
        st.markdown(
            f"- `{item['item']}` - Rs {item['price']} "
            f"(taste {item['taste']}/10, nutrition {item['nutrition']}/10, {reason})"
        )

    st.markdown("**Full canteen menu**")
    menu_frame = pd.DataFrame(canteen_data["menu"])
    st.dataframe(
        menu_frame[["item", "price", "category"]].rename(
            columns={"item": "Item", "price": "Price (Rs)", "category": "Category"}
        ),
        use_container_width=True,
        hide_index=True,
    )


st.set_page_config(page_title="Mess Menu", layout="wide")
st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(214, 118, 67, 0.18), transparent 26%),
            radial-gradient(circle at top right, rgba(82, 123, 179, 0.16), transparent 24%),
            linear-gradient(135deg, #0f1117 0%, #151a23 45%, #1b2028 100%);
        color: #f3ede7;
    }

    .block-container {
        padding-top: 2.6rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: #f7efe6;
        letter-spacing: -0.02em;
    }

    .stCaption {
        color: #bbaea3;
    }

    [data-testid="stMetric"] {
        background: rgba(27, 31, 40, 0.82);
        border: 1px solid rgba(219, 161, 120, 0.12);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        box-shadow: 0 14px 30px rgba(0, 0, 0, 0.24);
    }

    .stButton > button, .stFormSubmitButton > button {
        background: linear-gradient(135deg, #c96f3b 0%, #a64b2a 100%);
        color: #fff8f1;
        border: none;
        border-radius: 999px;
        font-weight: 700;
        box-shadow: 0 10px 18px rgba(166, 75, 42, 0.18);
        transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.2s ease;
    }

    .stButton > button:hover, .stFormSubmitButton > button:hover {
        background: linear-gradient(135deg, #d77a44 0%, #b45430 100%);
        transform: translateY(-1px);
        box-shadow: 0 14px 24px rgba(166, 75, 42, 0.22);
    }

    .stTextInput > div > div > input {
        background: rgba(26, 30, 39, 0.92);
        color: #f6efe8;
        border-radius: 14px;
        border: 1px solid rgba(219, 161, 120, 0.14);
    }

    [data-testid="stFileUploader"] {
        background: rgba(24, 29, 38, 0.82);
        border: 1px solid rgba(219, 161, 120, 0.14);
        border-radius: 20px;
        padding: 0.8rem;
    }

    [data-testid="stDataFrame"] {
        background: rgba(24, 29, 38, 0.82);
        border-radius: 18px;
        padding: 0.4rem;
    }

    [data-testid="stMarkdownContainer"] p {
        color: #ddd1c6;
    }

    [data-testid="stProgressBar"] > div > div {
        background: linear-gradient(90deg, #d8753f 0%, #ebb15d 100%);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "menu" not in st.session_state or "date_range" not in st.session_state:
    menu, date_range, bhawan_name = load_menu()
    st.session_state.menu = menu
    st.session_state.date_range = date_range
    st.session_state.bhawan_name = bhawan_name
    st.session_state.day_canteen = get_day_canteen_data(DAY_CANTEEN_IMAGE_PATH)
    st.session_state.night_canteen = get_night_canteen_data(NIGHT_CANTEEN_IMAGE_PATHS)
    st.session_state.sarojini_canteen = get_sarojini_canteen_data(SAROJINI_CANTEEN_IMAGE_PATH)
    st.session_state.vigyan_canteen = get_vigyan_canteen_data(VIGYAN_CANTEEN_IMAGE_PATH)
    populate_editor_state(menu)
    st.session_state.last_uploaded_signature = None
    st.session_state.show_menu_editor = False
    st.session_state.show_weekly_analysis = False
    st.session_state.show_today_menu = False

if "day_canteen" not in st.session_state:
    st.session_state.day_canteen = get_day_canteen_data(DAY_CANTEEN_IMAGE_PATH)

if "night_canteen" not in st.session_state:
    st.session_state.night_canteen = get_night_canteen_data(NIGHT_CANTEEN_IMAGE_PATHS)

if "sarojini_canteen" not in st.session_state:
    st.session_state.sarojini_canteen = get_sarojini_canteen_data(SAROJINI_CANTEEN_IMAGE_PATH)

if "vigyan_canteen" not in st.session_state:
    st.session_state.vigyan_canteen = get_vigyan_canteen_data(VIGYAN_CANTEEN_IMAGE_PATH)


if st.session_state.get("bhawan_name"):
    st.markdown(
        f"<div style='font-size: 2.6rem; font-weight: 800; line-height: 1.2; padding-top: 0.35rem;'>{st.session_state.bhawan_name}</div>",
        unsafe_allow_html=True,
    )

if st.session_state.get("date_range"):
    st.caption(f"📅 Week: {st.session_state.date_range}")

if not st.session_state.menu:
    st.warning("⚠️ No menu data found. Add `menu.jpg` or upload an image to begin.")
else:
    st.header("🤔 Should you eat in mess today or not?")
    today = datetime.now().strftime("%A")
    if today in st.session_state.menu:
        st.subheader(f"📊 Today's Analysis: {today}")
        show_score_card(today, st.session_state.menu[today])
        st.button(
            "🍛 Open Today's Menu",
            use_container_width=True,
            on_click=toggle_today_menu,
        )
        if st.session_state.show_today_menu:
            st.caption('You can edit this menu for any mistakes in the "📝 Open Daily Menu" section.')
            show_menu_preview(today, st.session_state.menu[today])
    else:
        st.info("ℹ️ Today's menu is not available in the current schedule.")

    st.button("📝 Open Daily Menu", use_container_width=True, on_click=toggle_menu_editor)

    if st.session_state.show_menu_editor:
        ensure_editor_state(st.session_state.menu)
        st.header("🛠️ Daily Editable Menu")
        with st.form("menu_editor_form"):
            updated_menu = render_editor(st.session_state.menu)
            save_clicked = st.form_submit_button("💾 Save Menu")

        if save_clicked:
            st.session_state.menu = updated_menu
            populate_editor_state(st.session_state.menu)
            save_menu(st.session_state.menu)
            st.success(f"✅ Menu saved to {MENU_JSON_PATH}")

    if st.button("📈 Open Weekly Analysis", use_container_width=True):
        st.session_state.show_weekly_analysis = not st.session_state.show_weekly_analysis

    if st.session_state.show_weekly_analysis:
        st.header("📅 Weekly Mess Analysis")
        for day, meals in st.session_state.menu.items():
            show_score_card(day, meals, show_canteen_actions=False)

    st.subheader("📤 Upload New Mess Schedule")
    st.caption("Upload a new weekly mess menu image to refresh the current bhawan and menu.")
    uploaded_file = st.file_uploader(
        "Upload a new mess schedule image",
        type=["png", "jpg", "jpeg"],
    )

    if uploaded_file is not None:
        uploaded_signature = get_uploaded_file_signature(uploaded_file)
        if uploaded_signature != st.session_state.last_uploaded_signature:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with open(UPLOADED_IMAGE_PATH, "wb") as file:
                file.write(uploaded_file.getbuffer())

            parsed_menu, parsed_range, parsed_bhawan = load_menu_from_parser(
                UPLOADED_IMAGE_PATH
            )
            st.session_state.menu = parsed_menu
            st.session_state.date_range = parsed_range
            st.session_state.bhawan_name = parsed_bhawan
            populate_editor_state(parsed_menu)
            st.session_state.last_uploaded_signature = uploaded_signature
            st.success("🎉 New mess menu loaded from image.")
