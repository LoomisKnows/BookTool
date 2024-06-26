import pandas as pd
from tkinter import Tk, simpledialog

def get_storage_information():
    Tk().withdraw()  # Hide the root window
    storage_data = []
    
    while True:
        shelf_name = simpledialog.askstring("Input", "Enter the name of the shelf (or type 'done' to finish):")
        if shelf_name.lower() == 'done':
            break
        dimensions = simpledialog.askstring("Input", f"Enter the dimensions (LxWxH) for {shelf_name}:")
        storage_data.append({"Shelf Name": shelf_name, "Dimensions": dimensions})

    if storage_data:
        df = pd.DataFrame(storage_data)
        df.to_excel('storage_spaces.xlsx', index=False, engine='openpyxl')
        print("Storage information saved to storage_spaces.xlsx")

if __name__ == "__main__":
    get_storage_information()
