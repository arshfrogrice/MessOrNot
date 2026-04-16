# MessOrNot 🍽️

## What & Why

Every IIT Roorkee student faces a daily dilemma:

> Should I eat in the mess or go outside?

Mess menus are messy, inconsistent, and often not reliable indicators of food quality. Students end up wasting time deciding or making poor choices.

**MessOrNot solves this by converting messy real-world data into actionable decisions.**

---

## What it does

* 📸 Extracts mess menu from images (OCR)
* ✏️ Allows editing & correcting menu data
* 📊 Calculates:

  * Taste score
  * Nutrition score
* 🧠 Generates a final **mess score**
* 🔥 Recommends:

  * Eat in mess OR
  * Skip and check outside options
* 🍜 Shows canteen alternatives with price-based recommendations

---

## Features

* Smart scoring system (taste + nutrition)
* Editable UI for OCR correction
* Decision engine for breakfast, lunch, and dinner
* Day-wise and meal-wise menu handling
* Canteen alternatives for lunch and dinner
* Lightweight and fast (Streamlit-based)

---

## Tech Stack

* Python
* Streamlit
* Tesseract OCR
* OpenCV
* Pandas
* JSON / CSV data storage

---

## How to Run

```bash
cd MessOrNot
python -m streamlit run app.py
```

---

## Demo

https://drive.google.com/file/d/1U9Unsa3-QI8ootXmQDIYNMVj-lapjc8r/view?usp=sharing

---

## Future Improvements

* Live food data scraping
* Personalized recommendations
* Better OCR cleanup and menu parsing
* Mobile-friendly UI
