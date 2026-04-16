import argparse
from datetime import datetime, timedelta
import re
from pathlib import Path

import cv2
import pandas as pd
import pytesseract


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

DAY_PATTERN = re.compile(
    r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)$",
    re.IGNORECASE,
)
WEEKDAY_ANYWHERE_PATTERN = re.compile(
    r"\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b",
    re.IGNORECASE,
)
DATE_PATTERN = re.compile(r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b")
BHAWAN_PATTERN = re.compile(r"\b([A-Za-z]+)\s+Bhawan\s+Mess\b", re.IGNORECASE)
COFFEE_SHOP_PATTERN = re.compile(r"\b([A-Za-z]+)\s+Bhawan\s+Coffee\s+Shop\b", re.IGNORECASE)
CANTEEN_BOARD_PATTERN = re.compile(r"\b([A-Za-z]+)\s+Bhawan\s+Canteen\b", re.IGNORECASE)

DAY_CANTEEN_MENU = [
    {"item": "Plain Paratha", "price": 10, "category": "Paratha"},
    {"item": "Aloo Paratha", "price": 15, "category": "Paratha"},
    {"item": "Aloo Pyaj Paratha", "price": 15, "category": "Paratha"},
    {"item": "Gobhi Muli Paratha", "price": 15, "category": "Paratha"},
    {"item": "Paneer Paratha", "price": 25, "category": "Paratha"},
    {"item": "Cheese Paratha", "price": 25, "category": "Paratha"},
    {"item": "Mix Paratha", "price": 25, "category": "Paratha"},
    {"item": "Egg Paratha", "price": 25, "category": "Paratha"},
    {"item": "Double Egg Paratha", "price": 30, "category": "Paratha"},
    {"item": "Double Egg Roll", "price": 40, "category": "Roll"},
    {"item": "Double Egg Cheese Roll", "price": 50, "category": "Roll"},
    {"item": "Paneer Roll", "price": 50, "category": "Roll"},
    {"item": "Paneer Cheese Roll", "price": 60, "category": "Roll"},
    {"item": "Fry Noodles", "price": 30, "category": "Continental"},
    {"item": "Chowmin", "price": 30, "category": "Continental"},
    {"item": "Egg Noodles", "price": 35, "category": "Continental"},
    {"item": "Egg Chowmin", "price": 35, "category": "Continental"},
    {"item": "Macroni", "price": 30, "category": "Continental"},
    {"item": "Spring Roll", "price": 40, "category": "Continental"},
    {"item": "Veg Momos", "price": 60, "category": "Momos"},
    {"item": "Paneer Momos", "price": 80, "category": "Momos"},
    {"item": "White Sauce Pasta", "price": 40, "category": "Continental"},
    {"item": "Red Sauce Pasta", "price": 35, "category": "Continental"},
    {"item": "Chilly Potato", "price": 40, "category": "Continental"},
    {"item": "Hunny Chilly Potato", "price": 50, "category": "Continental"},
    {"item": "Bhelpuri", "price": 25, "category": "Snacks"},
    {"item": "Aloo Sandwich", "price": 30, "category": "Sandwich"},
    {"item": "Veg Sandwich", "price": 35, "category": "Sandwich"},
    {"item": "Paneer Sandwich", "price": 40, "category": "Sandwich"},
    {"item": "Cheese Grilled Sandwich", "price": 40, "category": "Sandwich"},
    {"item": "Samosa", "price": 7, "category": "Snacks"},
    {"item": "Bread Pakoda", "price": 10, "category": "Snacks"},
    {"item": "Mix Pakoda", "price": 10, "category": "Snacks"},
    {"item": "Paneer Pakoda", "price": 25, "category": "Snacks"},
    {"item": "French Fries", "price": 25, "category": "Snacks"},
    {"item": "Poha", "price": 30, "category": "Snacks"},
    {"item": "Veg Patties", "price": 15, "category": "Snacks"},
    {"item": "Masala Patties", "price": 20, "category": "Snacks"},
    {"item": "Paneer Patties", "price": 25, "category": "Snacks"},
    {"item": "Bread Butter", "price": 15, "category": "Eggs"},
    {"item": "Bun Butter", "price": 15, "category": "Eggs"},
    {"item": "Plain Omelette", "price": 20, "category": "Eggs"},
    {"item": "Bun Omelette", "price": 30, "category": "Eggs"},
    {"item": "Bread Omelette", "price": 30, "category": "Eggs"},
    {"item": "Full Fry", "price": 25, "category": "Eggs"},
    {"item": "Half Fry", "price": 20, "category": "Eggs"},
    {"item": "Egg Bhurji", "price": 25, "category": "Eggs"},
    {"item": "French Toast", "price": 25, "category": "Eggs"},
    {"item": "Bun Samosa", "price": 15, "category": "Snacks"},
    {"item": "Vada Pav", "price": 20, "category": "Snacks"},
    {"item": "Veg Burger", "price": 30, "category": "Burger"},
    {"item": "Cheese Burger", "price": 40, "category": "Burger"},
]

NIGHT_CANTEEN_MENU = [
    {"item": "Tea", "price": 10, "category": "Beverages"},
    {"item": "Coffee", "price": 20, "category": "Beverages"},
    {"item": "Plain Milk", "price": 20, "category": "Beverages"},
    {"item": "Haldi Milk", "price": 20, "category": "Beverages"},
    {"item": "Bournvita Milk", "price": 20, "category": "Beverages"},
    {"item": "Plain Patties", "price": 20, "category": "Snacks"},
    {"item": "Masala Patties", "price": 25, "category": "Snacks"},
    {"item": "Cheese Patties", "price": 35, "category": "Snacks"},
    {"item": "Tandoori Patties", "price": 35, "category": "Snacks"},
    {"item": "Pizza Patties", "price": 30, "category": "Snacks"},
    {"item": "Chilli Patties", "price": 35, "category": "Snacks"},
    {"item": "Makhni Patties", "price": 35, "category": "Snacks"},
    {"item": "Poha", "price": 30, "category": "Snacks"},
    {"item": "Plain Maggi", "price": 30, "category": "Maggi"},
    {"item": "Veg Maggi", "price": 30, "category": "Maggi"},
    {"item": "Cheese Maggi", "price": 40, "category": "Maggi"},
    {"item": "Butter Maggi", "price": 35, "category": "Maggi"},
    {"item": "Extra Masala Maggi", "price": 35, "category": "Maggi"},
    {"item": "Egg Maggi", "price": 40, "category": "Maggi"},
    {"item": "Veg Burger", "price": 30, "category": "Burger"},
    {"item": "Cheese Burger", "price": 40, "category": "Burger"},
    {"item": "Tandoori Burger", "price": 40, "category": "Burger"},
    {"item": "Makhni Burger", "price": 40, "category": "Burger"},
    {"item": "Bun Butter", "price": 15, "category": "Breads"},
    {"item": "Bun Butter Bhujia", "price": 20, "category": "Breads"},
    {"item": "Bread Butter", "price": 15, "category": "Breads"},
    {"item": "Bun Butter Cheese", "price": 25, "category": "Breads"},
    {"item": "Bread Butter Cheese", "price": 25, "category": "Breads"},
    {"item": "Veg Sandwich", "price": 35, "category": "Sandwich"},
    {"item": "Cheese Sandwich", "price": 40, "category": "Sandwich"},
    {"item": "Egg Sandwich", "price": 50, "category": "Sandwich"},
    {"item": "Tandoori Sandwich", "price": 40, "category": "Sandwich"},
    {"item": "Makhni Sandwich", "price": 40, "category": "Sandwich"},
    {"item": "Pizza Sandwich", "price": 40, "category": "Sandwich"},
    {"item": "Bhelpuri", "price": 30, "category": "Snacks"},
    {"item": "Macroni", "price": 30, "category": "Continental"},
    {"item": "Chowmein", "price": 30, "category": "Continental"},
    {"item": "Egg Chowmeen", "price": 40, "category": "Continental"},
    {"item": "Egg Macroni", "price": 40, "category": "Continental"},
    {"item": "Veg Bread Omelette 2 Egg", "price": 35, "category": "Eggs"},
    {"item": "Plain Bread Omelette 2 Egg", "price": 30, "category": "Eggs"},
    {"item": "Veg Bunn Omelette 2 Egg", "price": 35, "category": "Eggs"},
    {"item": "Plain Bunn Omelette 2 Egg", "price": 30, "category": "Eggs"},
    {"item": "Bread Cheese Omelette 2 Egg", "price": 35, "category": "Eggs"},
    {"item": "Bunn Cheese Omelette 2 Egg", "price": 40, "category": "Eggs"},
    {"item": "French Toast 2 Egg", "price": 30, "category": "Eggs"},
    {"item": "Toast Bhujia 2 Egg", "price": 30, "category": "Eggs"},
    {"item": "Plain Omelette 2 Egg", "price": 25, "category": "Eggs"},
    {"item": "Egg Full Fry", "price": 25, "category": "Eggs"},
    {"item": "Egg Half Fry", "price": 20, "category": "Eggs"},
    {"item": "Peanut Chaat Half", "price": 30, "category": "Snacks"},
    {"item": "Peanut Chaat Full", "price": 50, "category": "Snacks"},
    {"item": "Chole Kulche", "price": 40, "category": "Snacks"},
    {"item": "Pav Bhaji", "price": 40, "category": "Snacks"},
    {"item": "Momos 6 Pcs", "price": 30, "category": "Momos"},
    {"item": "Momos 12 Pcs", "price": 60, "category": "Momos"},
]

SAROJINI_CANTEEN_MENU = [
    {"item": "Simple Tea", "price": 10, "category": "Beverages"},
    {"item": "Kulhad Tea", "price": 15, "category": "Beverages"},
    {"item": "Medium Tea", "price": 15, "category": "Beverages"},
    {"item": "Large Tea", "price": 20, "category": "Beverages"},
    {"item": "Milk", "price": 20, "category": "Beverages"},
    {"item": "Bournvita Milk", "price": 25, "category": "Beverages"},
    {"item": "Cold Coffee Plain", "price": 25, "category": "Beverages"},
    {"item": "Coffee with Ice Cream", "price": 35, "category": "Beverages"},
    {"item": "Hot Coffee", "price": 20, "category": "Beverages"},
    {"item": "Makhni Burger", "price": 40, "category": "Burger"},
    {"item": "Burger", "price": 30, "category": "Burger"},
    {"item": "Burger Cheese Veg", "price": 40, "category": "Burger"},
    {"item": "Plain Omelets 2 Egg", "price": 25, "category": "Eggs"},
    {"item": "Bread Omelets", "price": 30, "category": "Eggs"},
    {"item": "Bun Omelets", "price": 30, "category": "Eggs"},
    {"item": "Bun Butter", "price": 15, "category": "Breads"},
    {"item": "Bun Butter Bhujia", "price": 20, "category": "Breads"},
    {"item": "Half Egg Fry", "price": 20, "category": "Eggs"},
    {"item": "Full Egg Fry", "price": 30, "category": "Eggs"},
    {"item": "Bread Butter Toast", "price": 15, "category": "Breads"},
    {"item": "Cheese Grilled Toast", "price": 25, "category": "Sandwich"},
    {"item": "Grilled Veg Toast", "price": 25, "category": "Sandwich"},
    {"item": "Cheese Garlic Bread", "price": 40, "category": "Breads"},
    {"item": "Poha Half Plate", "price": 20, "category": "Snacks"},
    {"item": "Poha Full Plate", "price": 30, "category": "Snacks"},
    {"item": "Bengoli Momos Steam", "price": 30, "category": "Momos"},
    {"item": "Bengoli Momos Fried", "price": 30, "category": "Momos"},
    {"item": "French Fries", "price": 30, "category": "Snacks"},
    {"item": "Bhelpuri", "price": 25, "category": "Snacks"},
    {"item": "Plain Maggi", "price": 30, "category": "Maggi"},
    {"item": "Egg Maggi", "price": 50, "category": "Maggi"},
    {"item": "Cheese Maggi", "price": 40, "category": "Maggi"},
    {"item": "Fried Meggi", "price": 50, "category": "Maggi"},
    {"item": "Chowmein", "price": 30, "category": "Continental"},
    {"item": "Egg Chowmein", "price": 50, "category": "Continental"},
    {"item": "Macaroni", "price": 30, "category": "Continental"},
    {"item": "Tomato Soup", "price": 30, "category": "Soup"},
    {"item": "Mix Veg Soup", "price": 30, "category": "Soup"},
    {"item": "Sweet Corn Soup", "price": 30, "category": "Soup"},
    {"item": "Plain Patties", "price": 15, "category": "Snacks"},
    {"item": "Masala Patties", "price": 20, "category": "Snacks"},
    {"item": "Cheese Patties", "price": 30, "category": "Snacks"},
    {"item": "Pizza Patties", "price": 35, "category": "Snacks"},
    {"item": "Makhni Patties", "price": 35, "category": "Snacks"},
    {"item": "Tandoori Patties", "price": 30, "category": "Snacks"},
    {"item": "Sweet Corn Patties", "price": 30, "category": "Snacks"},
    {"item": "Veg Sandwich", "price": 30, "category": "Sandwich"},
    {"item": "Egg Sandwich", "price": 35, "category": "Sandwich"},
    {"item": "Egg Bhujji Pav", "price": 40, "category": "Eggs"},
    {"item": "Peanuts Chat", "price": 40, "category": "Snacks"},
]

VIGYAN_CANTEEN_MENU = [
    {"item": "Plain Paratha", "price": 10, "category": "Paratha"},
    {"item": "Aloo Paratha", "price": 15, "category": "Paratha"},
    {"item": "Piyaj Pyaj Aloo Pyaj Paratha", "price": 15, "category": "Paratha"},
    {"item": "Gobhi Paratha", "price": 15, "category": "Paratha"},
    {"item": "Mooli Paratha", "price": 15, "category": "Paratha"},
    {"item": "Paneer Paratha", "price": 25, "category": "Paratha"},
    {"item": "Paneer Piyaj Paratha", "price": 20, "category": "Paratha"},
    {"item": "Egg Paratha", "price": 20, "category": "Paratha"},
    {"item": "Samosa", "price": 7, "category": "Snacks"},
    {"item": "Bondu", "price": 10, "category": "Snacks"},
    {"item": "Mix Pakoda 100gm", "price": 30, "category": "Snacks"},
    {"item": "Paneer Pakoda 100gm", "price": 40, "category": "Snacks"},
    {"item": "Sweet Corn Pakoda 100gm", "price": 35, "category": "Snacks"},
    {"item": "Bread Pakoda", "price": 10, "category": "Snacks"},
    {"item": "Potato Chilli 100gm", "price": 40, "category": "Snacks"},
    {"item": "French Fries Half", "price": 30, "category": "Snacks"},
    {"item": "French Fries Full", "price": 50, "category": "Snacks"},
    {"item": "Spring Roll Full 12 pcs", "price": 40, "category": "Snacks"},
    {"item": "Veg Patties", "price": 15, "category": "Snacks"},
    {"item": "Veg Masala Patties", "price": 20, "category": "Snacks"},
    {"item": "Masala Patties with Cheese", "price": 30, "category": "Snacks"},
    {"item": "Poha Half", "price": 20, "category": "Snacks"},
    {"item": "Poha Full", "price": 30, "category": "Snacks"},
    {"item": "Bhel", "price": 30, "category": "Snacks"},
    {"item": "Chana Chat Half", "price": 30, "category": "Snacks"},
    {"item": "Chana Chat Full", "price": 50, "category": "Snacks"},
    {"item": "Sweet Corn", "price": 35, "category": "Snacks"},
    {"item": "Bread Butter 2 pcs", "price": 15, "category": "Breads"},
    {"item": "Bun Butter 1 pcs", "price": 15, "category": "Breads"},
    {"item": "Plain Omelette 2 Egg", "price": 25, "category": "Eggs"},
    {"item": "Bun Omelette 2 Egg", "price": 30, "category": "Eggs"},
    {"item": "Bread Omelette 2 Egg", "price": 30, "category": "Eggs"},
    {"item": "Half Egg Fry 2 Egg", "price": 25, "category": "Eggs"},
    {"item": "Full Egg Fry 2 Egg", "price": 25, "category": "Eggs"},
    {"item": "Bun Samosa Plain", "price": 15, "category": "Snacks"},
    {"item": "Veg Burger", "price": 30, "category": "Burger"},
    {"item": "Burger Mac D Tikki Cheese", "price": 40, "category": "Burger"},
    {"item": "Aloo Sandwich Grilled", "price": 35, "category": "Sandwich"},
    {"item": "Vegetable Sandwich", "price": 35, "category": "Sandwich"},
    {"item": "Vegetable Sandwich Cheese", "price": 40, "category": "Sandwich"},
    {"item": "Paneer Sandwich", "price": 50, "category": "Sandwich"},
    {"item": "Egg Sandwich", "price": 50, "category": "Sandwich"},
    {"item": "Chowmein Plate", "price": 30, "category": "Continental"},
    {"item": "Chowmein Eggs", "price": 40, "category": "Continental"},
    {"item": "Macroni", "price": 30, "category": "Continental"},
    {"item": "Pasta White Sauce", "price": 40, "category": "Continental"},
    {"item": "Cheese Pasta White Sauce", "price": 50, "category": "Continental"},
    {"item": "Red Sauce Pasta", "price": 40, "category": "Continental"},
    {"item": "Veg Momos 6 pcs", "price": 30, "category": "Momos"},
    {"item": "Soup Maggi", "price": 30, "category": "Maggi"},
    {"item": "Cheese Maggi", "price": 40, "category": "Maggi"},
    {"item": "Masala Soup Maggi", "price": 35, "category": "Maggi"},
    {"item": "Egg Maggi", "price": 40, "category": "Maggi"},
    {"item": "Egg Fry Maggi", "price": 40, "category": "Maggi"},
    {"item": "Fry Maggi", "price": 30, "category": "Maggi"},
    {"item": "Upma", "price": 30, "category": "South Indian"},
    {"item": "Uttapam With Sambhar and Coconut Chutney", "price": 40, "category": "South Indian"},
    {"item": "Masala Dosa", "price": 40, "category": "South Indian"},
    {"item": "Plain Dosa", "price": 25, "category": "South Indian"},
    {"item": "Onion Masala Dosa", "price": 45, "category": "South Indian"},
    {"item": "Paneer Dosa", "price": 70, "category": "South Indian"},
    {"item": "Tea", "price": 10, "category": "Beverages"},
    {"item": "Tea Cardamom", "price": 15, "category": "Beverages"},
    {"item": "Hot Lemon Tea", "price": 10, "category": "Beverages"},
    {"item": "Sweet Milk For Ice Cream", "price": 20, "category": "Beverages"},
    {"item": "Sweet Milk Tone", "price": 15, "category": "Beverages"},
    {"item": "Bournvita Milk", "price": 20, "category": "Beverages"},
    {"item": "Hot Coffee", "price": 15, "category": "Beverages"},
    {"item": "Cold Coffee", "price": 25, "category": "Beverages"},
    {"item": "Banana Mango Shake", "price": 25, "category": "Beverages"},
    {"item": "Chocolate Shake", "price": 30, "category": "Beverages"},
    {"item": "Oreo Shake", "price": 25, "category": "Beverages"},
    {"item": "Lassi", "price": 25, "category": "Beverages"},
    {"item": "Nimbu Pani", "price": 15, "category": "Beverages"},
    {"item": "Soda Shikanji", "price": 20, "category": "Beverages"},
    {"item": "Cola Shikanji", "price": 25, "category": "Beverages"},
    {"item": "Plain Chapati", "price": 7, "category": "Meals"},
    {"item": "Butter Chapati", "price": 8, "category": "Meals"},
    {"item": "Aloo Jeera Half", "price": 30, "category": "Meals"},
    {"item": "Aloo Jeera Full", "price": 50, "category": "Meals"},
    {"item": "Paneer Butter Masala", "price": 60, "category": "Meals"},
    {"item": "Paneer Bhurji", "price": 60, "category": "Meals"},
    {"item": "Shahi Paneer", "price": 60, "category": "Meals"},
    {"item": "Chola Kulcha", "price": 35, "category": "Meals"},
    {"item": "Fried Rice", "price": 30, "category": "Meals"},
    {"item": "Paneer Fried Rice", "price": 50, "category": "Meals"},
    {"item": "Egg Fried Rice", "price": 40, "category": "Meals"},
    {"item": "Rice With Chola", "price": 45, "category": "Meals"},
    {"item": "Dal With Rice", "price": 45, "category": "Meals"},
    {"item": "Aloo Tomato Half", "price": 30, "category": "Meals"},
    {"item": "Aloo Tomato Full", "price": 50, "category": "Meals"},
    {"item": "Chana Masala Half", "price": 30, "category": "Meals"},
    {"item": "Chana Masala Full", "price": 50, "category": "Meals"},
    {"item": "Mutter Paneer", "price": 60, "category": "Meals"},
    {"item": "Kadhai Paneer 12 pcs", "price": 140, "category": "Meals"},
    {"item": "Paneer Roll", "price": 50, "category": "Roll"},
    {"item": "Egg Roll", "price": 40, "category": "Roll"},
    {"item": "Paneer Cheese Roll", "price": 60, "category": "Roll"},
    {"item": "Paneer Egg Roll", "price": 80, "category": "Roll"},
    {"item": "Veg Roll", "price": 40, "category": "Roll"},
]


def preprocess_image(image_path: Path):
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    upscaled = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    denoised = cv2.GaussianBlur(upscaled, (3, 3), 0)
    processed = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11,
    )
    return processed


def load_ocr_words(image):
    data = pytesseract.image_to_data(
        image,
        output_type=pytesseract.Output.DICT,
        config="--oem 3 --psm 6",
    )

    words = []
    for i, raw_text in enumerate(data["text"]):
        text = raw_text.strip()
        if not text:
            continue

        confidence = float(data["conf"][i])
        if confidence < 15:
            continue

        left = int(data["left"][i])
        top = int(data["top"][i])
        width = int(data["width"][i])
        height = int(data["height"][i])
        words.append(
            {
                "text": text,
                "left": left,
                "top": top,
                "right": left + width,
                "bottom": top + height,
                "center_y": top + height / 2,
            }
        )
    return words


def normalize_token(token: str) -> str:
    cleaned = re.sub(r"[^A-Za-z]", "", token)
    return cleaned.lower()


def detect_day_anchors(words):
    anchors = []
    for word in words:
        token = normalize_token(word["text"])
        for weekday in WEEKDAYS:
            if token == weekday.lower():
                anchors.append(
                    {
                        "day": weekday,
                        "top": word["top"],
                        "bottom": word["bottom"],
                        "center_y": word["center_y"],
                    }
                )
                break

    anchors.sort(key=lambda item: item["center_y"])

    unique = []
    for anchor in anchors:
        if unique and abs(anchor["center_y"] - unique[-1]["center_y"]) < 20:
            continue
        unique.append(anchor)
    return unique


def infer_missing_anchors(day_anchors):
    if not day_anchors:
        return []

    if len(day_anchors) == len(WEEKDAYS):
        return day_anchors

    weekday_index = {day: index for index, day in enumerate(WEEKDAYS)}
    completed = []

    for index, anchor in enumerate(day_anchors):
        completed.append(anchor)
        if index == len(day_anchors) - 1:
            continue

        current_day_index = weekday_index[anchor["day"]]
        next_day_index = weekday_index[day_anchors[index + 1]["day"]]
        gap = next_day_index - current_day_index
        if gap <= 1:
            continue

        y_step = (day_anchors[index + 1]["center_y"] - anchor["center_y"]) / gap
        for missing_offset in range(1, gap):
            inferred_day = WEEKDAYS[current_day_index + missing_offset]
            inferred_y = anchor["center_y"] + y_step * missing_offset
            completed.append(
                {
                    "day": inferred_day,
                    "top": int(inferred_y - 20),
                    "bottom": int(inferred_y + 20),
                    "center_y": inferred_y,
                    "inferred": True,
                }
            )

    completed.sort(key=lambda item: item["center_y"])
    return completed


def row_boundaries(day_anchors, image_height):
    if not day_anchors:
        return []

    if len(day_anchors) > 1:
        spacing = [
            day_anchors[index + 1]["center_y"] - day_anchors[index]["center_y"]
            for index in range(len(day_anchors) - 1)
        ]
        typical_spacing = sum(spacing) / len(spacing)
    else:
        typical_spacing = 220

    boundaries = []
    for index, anchor in enumerate(day_anchors):
        if index == 0:
            top = max(0, int(anchor["top"] - 20))
        else:
            top = int((day_anchors[index - 1]["center_y"] + anchor["center_y"]) / 2)

        if index == len(day_anchors) - 1:
            bottom = min(image_height, int(anchor["center_y"] + typical_spacing / 2))
        else:
            bottom = int((anchor["center_y"] + day_anchors[index + 1]["center_y"]) / 2)

        boundaries.append({"day": anchor["day"], "top": top, "bottom": bottom})
    return boundaries


def group_words_into_lines(words, tolerance=18):
    if not words:
        return []

    ordered = sorted(words, key=lambda item: (item["top"], item["left"]))
    lines = []

    for word in ordered:
        if not lines:
            lines.append([word])
            continue

        current_line = lines[-1]
        avg_top = sum(item["top"] for item in current_line) / len(current_line)
        if abs(word["top"] - avg_top) <= tolerance:
            current_line.append(word)
        else:
            lines.append([word])

    rendered = []
    for line in lines:
        line = sorted(line, key=lambda item: item["left"])
        rendered.append(" ".join(item["text"] for item in line))
    return rendered


def collapse_text(lines):
    cleaned = []
    for line in lines:
        text = re.sub(r"\s+", " ", line).strip(" |")
        if text:
            cleaned.append(text)
    combined = " | ".join(cleaned)
    combined = WEEKDAY_ANYWHERE_PATTERN.sub("", combined)
    combined = re.sub(r"\s+\|\s+", " | ", combined)
    combined = re.sub(r"\s{2,}", " ", combined)
    return combined.strip(" |")


def extract_date(row_words):
    ordered = sorted(row_words, key=lambda item: (item["top"], item["left"]))
    for word in ordered:
        match = DATE_PATTERN.search(word["text"])
        if match:
            return match.group(0)
    joined = " ".join(word["text"] for word in ordered)
    match = DATE_PATTERN.search(joined)
    return match.group(0) if match else ""


def parse_date_token(date_token: str):
    for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%y", "%d/%m/%y", "%d-%m-%y"):
        try:
            return datetime.strptime(date_token, fmt)
        except ValueError:
            continue
    return None


def fill_missing_dates(table, date_range):
    if not date_range:
        return table

    range_parts = date_range.split(" to ")
    if len(range_parts) != 2:
        return table

    start_date = parse_date_token(range_parts[0])
    if start_date is None:
        return table

    table = table.copy()
    for index in range(len(table)):
        if not table.at[index, "Date"]:
            table.at[index, "Date"] = (start_date + timedelta(days=index)).strftime(
                "%d.%m.%Y"
            )
    return table


def build_day_table(words, image_shape):
    image_height, image_width = image_shape[:2]
    anchors = infer_missing_anchors(detect_day_anchors(words))
    rows = row_boundaries(anchors, image_height)

    if not rows:
        raise ValueError(
            "Could not detect weekday rows in the menu image. "
            "Try a clearer image or adjust OCR preprocessing."
        )

    # These ratios match the typical weekly mess menu layout:
    # day/date at left, breakfast in the first middle block,
    # lunch in the second middle block, and dinner on the right.
    breakfast_end = int(image_width * 0.46)
    lunch_end = int(image_width * 0.72)

    records = []
    for row in rows:
        row_words = [
            word for word in words if row["top"] <= word["center_y"] < row["bottom"]
        ]

        date_text = extract_date(row_words)
        breakfast_words = [
            word for word in row_words if 0 <= word["left"] < breakfast_end
        ]
        lunch_words = [
            word for word in row_words if breakfast_end <= word["left"] < lunch_end
        ]
        dinner_words = [word for word in row_words if lunch_end <= word["left"]]

        breakfast_lines = group_words_into_lines(breakfast_words)
        lunch_lines = group_words_into_lines(lunch_words)
        dinner_lines = group_words_into_lines(dinner_words)

        breakfast_text = collapse_text(
            [
                line
                for line in breakfast_lines
                if not DAY_PATTERN.search(line.strip())
                and not DATE_PATTERN.search(line)
            ]
        )
        lunch_text = collapse_text(
            [
                line
                for line in lunch_lines
                if not DAY_PATTERN.search(line.strip())
                and not DATE_PATTERN.search(line)
            ]
        )
        dinner_text = collapse_text(
            [
                line
                for line in dinner_lines
                if not DAY_PATTERN.search(line.strip())
                and not DATE_PATTERN.search(line)
            ]
        )

        records.append(
            {
                "Day": row["day"],
                "Date": date_text,
                "Breakfast": breakfast_text,
                "Lunch": lunch_text,
                "Dinner": dinner_text,
            }
        )

    return pd.DataFrame(records)


def extract_date_range(image):
    crops = [image, image[: image.shape[0] // 4, :]]
    configs = ["--oem 3 --psm 6", "--oem 3 --psm 11"]

    for crop in crops:
        for config in configs:
            text = pytesseract.image_to_string(crop, config=config)
            match = re.search(
                r"(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})\s*(?:to|-)\s*(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})",
                text,
            )
            if match:
                return f"{match.group(1)} to {match.group(2)}"
    return ""


def extract_bhawan_name(image):
    crops = [image, image[: image.shape[0] // 4, :]]
    configs = ["--oem 3 --psm 6", "--oem 3 --psm 11"]

    for crop in crops:
        for config in configs:
            text = pytesseract.image_to_string(crop, config=config)
            match = BHAWAN_PATTERN.search(text)
            if match:
                name = match.group(1).strip()
                return f"{name.title()} Bhawan"
    return ""


def extract_board_title(image, board_type):
    crops = [image, image[: image.shape[0] // 3, :]]
    configs = ["--oem 3 --psm 6", "--oem 3 --psm 11"]

    pattern = CANTEEN_BOARD_PATTERN if board_type == "canteen" else COFFEE_SHOP_PATTERN
    fallback = "Jawahar Bhawan Canteen" if board_type == "canteen" else "Jawahar Bhawan Coffee Shop"

    for crop in crops:
        for config in configs:
            text = pytesseract.image_to_string(crop, config=config)
            match = pattern.search(text)
            if match:
                name = match.group(1).strip().title()
                suffix = "Canteen" if board_type == "canteen" else "Coffee Shop"
                return f"{name} Bhawan {suffix}"
    return fallback


def parse_menu(image_path: Path):
    original_image = cv2.imread(str(image_path))
    if original_image is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")

    processed_image = preprocess_image(image_path)
    words = load_ocr_words(processed_image)
    date_range = extract_date_range(original_image)
    bhawan_name = extract_bhawan_name(original_image)
    table = build_day_table(words, processed_image.shape)
    table = fill_missing_dates(table, date_range)
    return table, date_range, bhawan_name


def get_day_canteen_data(image_path: Path | None = None):
    board_name = "Jawahar Bhawan Canteen"
    if image_path is not None and Path(image_path).exists():
        image = cv2.imread(str(image_path))
        if image is not None:
            board_name = extract_board_title(image, "canteen")

    return {
        "name": board_name,
        "hours": "2 PM to 2 AM",
        "menu": DAY_CANTEEN_MENU,
    }


def get_night_canteen_data(image_paths=None):
    board_name = "Jawahar Bhawan Coffee Shop"
    if image_paths:
        for image_path in image_paths:
            path = Path(image_path)
            if not path.exists():
                continue
            image = cv2.imread(str(path))
            if image is not None:
                board_name = extract_board_title(image, "coffee_shop")
                break

    return {
        "name": board_name,
        "hours": "2 AM to 2 PM",
        "menu": NIGHT_CANTEEN_MENU,
    }


def get_sarojini_canteen_data(image_path: Path | None = None):
    return {
        "name": "Sarojini Bhawan Day Canteen",
        "hours": "Day Canteen",
        "menu": SAROJINI_CANTEEN_MENU,
    }


def get_vigyan_canteen_data(image_path: Path | None = None):
    return {
        "name": "Vigyan Kunj Day Canteen",
        "hours": "Day Canteen",
        "menu": VIGYAN_CANTEEN_MENU,
    }


def build_meal_table(day_table):
    meal_table = day_table.melt(
        id_vars=["Day", "Date"],
        value_vars=["Breakfast", "Lunch", "Dinner"],
        var_name="Meal",
        value_name="Items",
    )
    meal_order = pd.CategoricalDtype(
        categories=["Breakfast", "Lunch", "Dinner"],
        ordered=True,
    )
    weekday_order = pd.CategoricalDtype(categories=WEEKDAYS, ordered=True)

    meal_table["Meal"] = meal_table["Meal"].astype(meal_order)
    meal_table["Day"] = meal_table["Day"].astype(weekday_order)
    meal_table = meal_table.sort_values(["Meal", "Day"]).reset_index(drop=True)
    return meal_table


def main():
    parser = argparse.ArgumentParser(
        description="Extract clean day-wise and meal-wise mess menu tables from a weekly schedule image."
    )
    parser.add_argument(
        "image",
        nargs="?",
        default="menu.jpg",
        help="Path to the weekly mess menu image.",
    )
    parser.add_argument(
        "--csv",
        default="clean_menu.csv",
        help="Path to save the cleaned day-wise table as CSV.",
    )
    parser.add_argument(
        "--meal-csv",
        default="clean_menu_by_meal.csv",
        help="Path to save the cleaned meal-wise table as CSV.",
    )
    args = parser.parse_args()

    image_path = Path(args.image)
    csv_path = Path(args.csv)
    meal_csv_path = Path(args.meal_csv)

    day_table, date_range, bhawan_name = parse_menu(image_path)
    meal_table = build_meal_table(day_table)

    pd.set_option("display.max_colwidth", None)
    if bhawan_name:
        print(f"Bhawan: {bhawan_name}")
    if date_range:
        print(f"Weekly Menu: {date_range}\n")
    print("Day-wise table:\n")
    print(day_table.to_string(index=False))
    print("\nMeal-wise table:\n")
    print(meal_table.to_string(index=False))

    day_table.to_csv(csv_path, index=False)
    meal_table.to_csv(meal_csv_path, index=False)
    print(f"\nSaved day-wise table to: {csv_path.resolve()}")
    print(f"Saved meal-wise table to: {meal_csv_path.resolve()}")


if __name__ == "__main__":
    main()
