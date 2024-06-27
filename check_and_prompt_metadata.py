# check_and_prompt_metadata.py
import os
import pandas as pd
from PIL import Image
from tkinter import Tk, filedialog, messagebox

def select_images():
    root = Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(
        title="Select Images",
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
    )
    root.destroy()
    return file_paths

def extract_metadata(image_path):
    with Image.open(image_path) as img:
        info = img.info
    return info

def search_excel_for_set(set_name, df):
    matches = df[df['Title'] == set_name]
    return matches

def check_metadata_and_prompt(image_paths, df):
    for image_path in image_paths:
        metadata = extract_metadata(image_path)
        if 'Data by Sar' in metadata.get('comment', ''):
            set_name = os.path.basename(image_path).split('_')[0]
            matches = search_excel_for_set(set_name, df)
            if not matches.empty:
                match = matches.iloc[0]
                missing_info = [col for col in df.columns if pd.isna(match[col]) or match[col] == '']
                message = f"Set '{set_name}' has already been processed.\n"
                if missing_info:
                    message += "The following information is missing:\n" + "\n".join(missing_info)
                    response = messagebox.askyesno("Missing Information", f"{message}\nDo you want to fill in the missing information?")
                    if response:
                        fill_missing_information(set_name, missing_info, df)
                    else:
                        messagebox.showinfo("Update Required", f"Please update the Excel sheet directly. The item is on line {match.name + 2}.")
                else:
                    response = messagebox.askyesno("Already Processed", f"{message}\nDo you want to process the image again as if it is new?")
                    if response:
                        process_as_new(image_path)
                    else:
                        messagebox.showinfo("Update Required", f"Please update the Excel sheet directly. The item is on line {match.name + 2}.")
            else:
                messagebox.showinfo("Not Processed", f"Set '{set_name}' has not been processed before. Proceeding as new.")
                process_as_new(image_path)

def fill_missing_information(set_name, missing_info, df):
    # Here, implement the logic to prompt the user to fill in the missing information.
    # You can create a simple form to collect the missing data and update the dataframe and the Excel sheet accordingly.
    pass

def process_as_new(image_path):
    # Implement the logic to process the image as if it is new.
    pass

def main():
    image_paths = select_images()
    filename = 'book_inventory.xlsx'
    df = pd.read_excel(filename, sheet_name='Sheet1')

    check_metadata_and_prompt(image_paths, df)

if __name__ == "__main__":
    main()
