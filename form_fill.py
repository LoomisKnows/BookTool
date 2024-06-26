import json
import pandas as pd
from tkinter import Tk, Toplevel, Label, Entry, Button, simpledialog, messagebox

def get_additional_details(set_name, prefilled_data, storage_spaces):
    root = Tk()
    root.withdraw()  # Hide the root window
    form = Toplevel(root)
    form.title(f"Additional Details for {set_name}")

    # Create labels and entries for each field
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
        "Category": ""
    }
    
    entries = {}
    
    row = 0
    for field, value in fields.items():
        Label(form, text=field).grid(row=row, column=0, sticky='e')
        entry = Entry(form, width=40)
        entry.grid(row=row, column=1)
        entry.insert(0, value)
        entries[field] = entry
        row += 1

    def assign_shelf(book_dimensions, storage_spaces):
        book_dims = [float(dim) for dim in book_dimensions.split('x')]
        book_dims.sort()
        for _, row in storage_spaces.iterrows():
            shelf_dims = [float(dim) for dim in row['Dimensions'].split('x')]
            shelf_dims.sort()
            if all(book_dim <= shelf_dim for book_dim, shelf_dim in zip(book_dims, shelf_dims)):
                return row['Shelf Name']
        return "No suitable shelf found"

    def submit():
        for field in fields:
            fields[field] = entries[field].get()

        if not fields["Dimensions"]:
            fields["Dimensions"] = simpledialog.askstring("Input", "Dimensions (LxWxH):")

        shelf = assign_shelf(fields["Dimensions"], storage_spaces)
        fields["Shelf"] = shelf

        with open(output_path, 'w') as f:
            json.dump(fields, f)
        form.destroy()
        messagebox.showinfo("Shelf Assignment", f"The book has been assigned to shelf: {shelf}")

    Button(form, text="Submit", command=submit).grid(row=row, columnspan=2)

    form.mainloop()
    root.destroy()

def main(set_name, prefilled_data, output_path, storage_spaces_path):
    storage_spaces = pd.read_excel(storage_spaces_path)
    get_additional_details(set_name, prefilled_data, storage_spaces)
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
