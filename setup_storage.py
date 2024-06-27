# setup_storage.py
import pandas as pd
from tkinter import Tk, Label, Entry, Button, messagebox

def get_storage_information():
    storage_data = []

    def add_shelf_data():
        shelf_name = entries["Shelf Name"].get()
        dimensions = entries["Dimensions"].get()
        genre = entries["Genre"].get()
        max_weight = entries["Max Weight"].get()
        special_characteristics = entries["Special Characteristics"].get()
        storage_class = entries["Storage Class"].get()

        storage_data.append({
            "Shelf Name": shelf_name,
            "Dimensions": dimensions,
            "Genre": genre,
            "Max Weight": max_weight,
            "Special Characteristics": special_characteristics,
            "Storage Class": storage_class
        })

        for entry in entries.values():
            entry.delete(0, 'end')

    def save_data_and_exit():
        if storage_data:
            df = pd.DataFrame(storage_data)
            df.to_excel('storage_spaces.xlsx', index=False, engine='openpyxl')
            messagebox.showinfo("Storage Information", "Storage information saved to storage_spaces.xlsx")
            print("Storage information saved to storage_spaces.xlsx")
        root.destroy()

    root = Tk()
    root.title("Storage Information")

    fields = ["Shelf Name", "Dimensions", "Genre", "Max Weight", "Special Characteristics", "Storage Class"]
    entries = {}

    for idx, field in enumerate(fields):
        Label(root, text=field).grid(row=idx, column=0)
        entry = Entry(root)
        entry.grid(row=idx, column=1)
        entries[field] = entry

    Button(root, text="Add Shelf", command=add_shelf_data).grid(row=len(fields), column=0)
    Button(root, text="Done", command=save_data_and_exit).grid(row=len(fields), column=1)

    root.mainloop()

if __name__ == "__main__":
    get_storage_information()
