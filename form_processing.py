# form_processing.py
import json
import pandas as pd
from tkinter import Tk, Toplevel, Label, Entry, Button, messagebox, Scale, HORIZONTAL, font
import random
from datetime import datetime

def get_additional_details(set_name, prefilled_data, storage_spaces, output_path):
    root = Tk()
    root.withdraw()
    form = Toplevel(root)
    form.title(f"Additional Details for {set_name}")

    current_year = datetime.now().year

    fields = {
        "Title": prefilled_data.get("Title", ""),
        "Author": prefilled_data.get("Author", ""),
        "Publisher": prefilled_data.get("Publisher", ""),
        "Year": prefilled_data.get("Year", ""),
        "Edition": prefilled_data.get("Edition", ""),
        "Pages": prefilled_data.get("Pages", ""),
        "Weight": prefilled_data.get("Weight", ""),
        "Dimensions": prefilled_data.get("Dimensions", ""),
        "Format": prefilled_data.get("Format", ""),
        "ISBN-10": prefilled_data.get("ISBN-10", ""),
        "ISBN-13": prefilled_data.get("ISBN-13", ""),
        "Genre": prefilled_data.get("Genre", ""),
        "Shelf": "",
        "Category": "",
        "Additional Information": ""
    }

    book_condition_fields = {
        "Cover Condition": None,
        "Spine Condition": None,
        "Pages Condition": None,
        "Extent of Damage/Markings": None,
        "Binding Integrity": None,
        "Dust Jacket Condition": None,
        "Markings and Annotations": None,
        "Stains and Odours": None
    }

    rating_descriptions = {
        "Cover Condition": {
            5: "No visible wear, pristine condition.",
            4: "Very minimal signs of use, no major defects.",
            3: "Some minor wear and tear (e.g., slight creases or scuffs).",
            2: "Noticeable wear (e.g., bent corners, significant scuff marks).",
            1: "Major damage (e.g., tears, significant creasing, missing parts)."
        },
        "Spine Condition": {
            5: "Spine is tight, no creases.",
            4: "Spine has minor signs of use but no creases.",
            3: "Some creases, but binding is still strong.",
            2: "Several creases, possible looseness in binding.",
            1: "Damaged or broken spine, loose pages."
        },
        "Pages Condition": {
            5: "Crisp, no marks or tears.",
            4: "Minimal wear, no writing or major stains.",
            3: "Some signs of use, such as slight yellowing or minor marks.",
            2: "Noticeable marks, creases, or light stains.",
            1: "Major stains, tears, or missing pages."
        },
        "Extent of Damage/Markings": {
            5: "No pages affected.",
            4: "1-5 pages with minor marks or damage.",
            3: "6-15 pages with marks or damage.",
            2: "16-30 pages with marks or damage.",
            1: "More than 30 pages with marks or damage."
        },
        "Binding Integrity": {
            5: "Binding is tight and intact.",
            4: "Binding is mostly intact with minimal looseness.",
            3: "Binding shows some looseness but holds together.",
            2: "Binding is loose but pages are still attached.",
            1: "Binding is broken, pages may be detached."
        },
        "Dust Jacket Condition": {
            5: "No damage, like new.",
            4: "Very slight wear, no major defects.",
            3: "Some wear, small tears, or creases.",
            2: "Noticeable wear and tear, larger tears.",
            1: "Significant damage or missing entirely."
        },
        "Markings and Annotations": {
            5: "No writing, highlighting, or stamps.",
            4: "Few marks or stamps that don't affect readability.",
            3: "Some annotations or highlighting, still readable.",
            2: "Extensive annotations, may affect readability.",
            1: "Too many markings, significantly affecting readability."
        },
        "Stains and Odours": {
            5: "No stains or odours.",
            4: "Few small stains, no noticeable odours.",
            3: "Some stains and slight musty odour.",
            2: "Large stains and strong odours.",
            1: "Extensive staining and unpleasant odours."
        },
    }

    entries = {}
    rating_scales = {}
    rating_labels = {}
    bold_font = font.Font(weight="bold")

    left_column = 0
    right_column = 2
    row = 0

    for field, value in fields.items():
        Label(form, text=field).grid(row=row, column=left_column, sticky='e')
        entry = Entry(form, width=40)
        entry.grid(row=row, column=left_column + 1)
        entry.insert(0, value)
        entries[field] = entry
        row += 1

    age_label = Label(form, text="Age")
    age_label.grid(row=row, column=left_column, sticky='e')
    age_entry = Entry(form, width=40)
    age_entry.grid(row=row, column=left_column + 1)
    entries["Age"] = age_entry
    row += 1

    row = 0
    Label(form, text="Book Condition", font=bold_font).grid(row=row, column=right_column, columnspan=2)
    row += 1

    def update_label(scale, field):
        value = scale.get()
        rating_labels[field].config(text=rating_descriptions[field][value])
        update_total_score()

    def update_total_score():
        total_score = calculate_total_score(entries, rating_scales)
        score_label.config(text=f"Total Score: {total_score}")

    for field in book_condition_fields.keys():
        Label(form, text=field, font=bold_font).grid(row=row, column=right_column, sticky='e')
        scale = Scale(form, from_=1, to=5, orient=HORIZONTAL)
        scale.grid(row=row, column=right_column + 1)
        scale.set(3)
        rating_scales[field] = scale
        rating_labels[field] = Label(form, text=rating_descriptions[field][3])
        rating_labels[field].grid(row=row + 1, column=right_column, columnspan=2)
        scale.config(command=lambda value, f=field: update_label(rating_scales[f], f))
        row += 2

    def assign_shelf(book_dimensions, book_genre, book_weight, storage_spaces):
        if not book_dimensions or book_dimensions == "0x0x0":
            return "TBD"
        if not book_weight or book_weight == "0":
            return "TBD"
        if not book_genre:
            book_genre = "None"

        book_dims = [float(dim) for dim in book_dimensions.split('x')]
        book_dims.sort()
        suitable_shelves = []

        for _, row in storage_spaces.iterrows():
            shelf_dims = [float(dim) for dim in row['Dimensions'].split('x')]
            shelf_dims.sort()
            max_weight = row['Max Weight']
            genre = row['Genre']

            if all(book_dim <= shelf_dim for book_dim, shelf_dim in zip(book_dims, shelf_dims)):
                if (max_weight == "None" or float(book_weight) <= float(max_weight)) and (genre == "None" or genre == book_genre):
                    suitable_shelves.append(row['Shelf Name'])

        if suitable_shelves:
            return random.choice(suitable_shelves)
        else:
            return "No suitable shelf found"

    def calculate_total_score(fields, rating_scales):
        score = sum(int(rating_scales[condition].get()) for condition in [
            "Cover Condition", "Spine Condition", "Pages Condition",
            "Extent of Damage/Markings", "Binding Integrity",
            "Dust Jacket Condition", "Markings and Annotations",
            "Stains and Odours"
        ])
        year = fields.get("Year")
        try:
            year = int(year.get())
            age = current_year - year
        except (ValueError, AttributeError):
            age = 0
        entries["Age"].delete(0, 'end')
        entries["Age"].insert(0, str(age))
        if age <= 10:
            score += 0
        elif age <= 20:
            score += 2
        elif age <= 50:
            score += 4
        elif age <= 100:
            score += 6
        else:
            score += 8
        return score

    def submit():
        for field in fields:
            fields[field] = entries[field].get()

        for field in rating_scales:
            book_condition_fields[field] = rating_scales[field].get()

        shelf = assign_shelf(fields["Dimensions"], fields["Genre"], fields["Weight"], storage_spaces)
        fields["Shelf"] = shelf
        fields["Total Score"] = calculate_total_score(fields, rating_scales)

        combined_fields = {**fields, **book_condition_fields}

        print("Submitting form with the following data:", combined_fields)

        with open(output_path, 'w') as f:
            json.dump(combined_fields, f)

        form.destroy()
        root.destroy()

        messagebox.showinfo("Shelf Assignment", f"The book has been assigned to shelf: {shelf}")

    score_label = Label(form, text="Total Score: 0", font=bold_font)
    score_label.grid(row=row, column=left_column, columnspan=2)
    
    Button(form, text="Submit", command=submit).grid(row=row + 1, column=left_column, columnspan=2)

    form.mainloop()

def main(set_name, prefilled_data, output_path, storage_spaces_path):
    storage_spaces = pd.read_excel(storage_spaces_path)
    get_additional_details(set_name, prefilled_data, storage_spaces, output_path)
    print(f"Additional details for {set_name} saved.")

if __name__ == "__main__":
    import sys
    set_name = sys.argv[1]
    prefilled_data_path = sys.argv[2]
    output_path = sys.argv[3]
    storage_spaces_path = sys.argv[4]

    with open(prefilled_data_path) as f:
        prefilled_data = json.load(f)

    main(set_name, prefilled_data, output_path, storage_spaces_path)
