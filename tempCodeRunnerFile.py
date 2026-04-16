import json
from pathlib import Path

import streamlit as st

from mess_data import parse_menu


DATA_DIR = Path("data")
MENU_JSON_PATH = DATA_DIR / "mess_menu.json"
DEFAULT_IMAGE_PATH = Path("menu.jpg")
MEAL_COLUMNS = ["Breakfast", "Lunch", "Dinner"]


def split_items(items_text):
    if not items_text:
        return []
    return [item.strip() for item in items_text.split("|") if item.strip()]


def load_menu_from_parser(image_path: Path):
    day_table, date_range = parse_menu(image_path)
    menu = {}

    for record in day_table.to_dict(orient="records"):
        day = record["Day"]
        menu[day] = {
            "Date": record["Date"],
            "Breakfast": split_items(record["Breakfast"]),
            "Lunch": split_items(record["Lunch"]),
            "Dinner": split_items(record["Dinner"]),
        }

    return menu, date_range


def load_menu():
    if MENU_JSON_PATH.exists():
        with open(MENU_JSON_PATH, "r", encoding="utf-8") as file:
            return json.load(file), ""

    if DEFAULT_IMAGE_PATH.exists():
        return load_menu_from_parser(DEFAULT_IMAGE_PATH)

    return {}, ""


def save_menu(menu):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(MENU_JSON_PATH, "w", encoding="utf-8") as file:
        json.dump(menu, file, indent=4)


def render_editor(menu):
    updated_menu = {}

    for day, meals in menu.items():
        st.subheader(day)
        date_value = st.text_input(
            f"Date ({day})",
            meals.get("Date", ""),
            key=f"date_{day}",
        )

        updated_menu[day] = {"Date": date_value}

        for meal in MEAL_COLUMNS:
            items = ", ".join(meals.get(meal, []))
            edited = st.text_input(
                f"{meal} ({day})",
                items,
                key=f"{meal}_{day}",
            )
            updated_menu[day][meal] = [item.strip() for item in edited.split(",") if item.strip()]

    return updated_menu


st.set_page_config(page_title="Mess Menu", layout="wide")
st.title("Mess Menu")

if "menu" not in st.session_state or "date_range" not in st.session_state:
    menu, date_range = load_menu()
    st.session_state.menu = menu
    st.session_state.date_range = date_range


uploaded_file = st.file_uploader(
    "Upload a new mess schedule image",
    type=["png", "jpg", "jpeg"],
)

if uploaded_file is not None:
    temp_image_path = Path(uploaded_file.name)
    with open(temp_image_path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    parsed_menu, parsed_range = load_menu_from_parser(temp_image_path)
    st.session_state.menu = parsed_menu
    st.session_state.date_range = parsed_range
    st.success("New mess menu loaded from image.")


if st.session_state.date_range:
    st.caption(f"Week: {st.session_state.date_range}")

if not st.session_state.menu:
    st.warning("No menu data found. Add `menu.jpg` or upload an image to begin.")
else:
    st.session_state.menu = render_editor(st.session_state.menu)

    if st.button("Save Menu"):
        save_menu(st.session_state.menu)
        st.success(f"Menu saved to {MENU_JSON_PATH}")