import os
import subprocess
import pandas as pd
from tkinter import Tk, filedialog
import json
import time

def select_images():
    root = Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(
        title="Select Images",
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
    )
    image_sets = {}
    for file_path in file_paths:
        set_name = os.path.basename(file_path).split('_')[0]
        if set_name not in image_sets:
            image_sets[set_name] = []
        image_sets[set_name].append(file_path)
    root.destroy()
    return image_sets

def run_script(script_path, args):
    process = subprocess.Popen(['python', script_path] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    print(stdout)
    if process.returncode != 0:
        print(f"Error: {stderr}")
    return process.returncode

def update_inventory(df, book_details):
    new_row = pd.DataFrame([book_details])
    updated_df = pd.concat([df, new_row], ignore_index=True)
    return updated_df

def update_condition_sheet(df_conditions, book_details):
    book_title = book_details.get("Title", "Unknown Title")
    condition_fields = {
        "Cover Condition", "Spine Condition", "Pages Condition", "Extent of Damage/Markings",
        "Binding Integrity", "Dust Jacket Condition", "Markings and Annotations", "Stains and Odours"
    }
    condition_data = {field: book_details.get(field, "Not Rated") for field in condition_fields}
    condition_data["Title"] = book_title
    new_condition_row = pd.DataFrame([condition_data])
    updated_df_conditions = pd.concat([df_conditions, new_condition_row], ignore_index=True)
    return updated_df_conditions

def check_storage_information():
    storage_file = 'storage_spaces.xlsx'
    if not os.path.exists(storage_file):
        print(f"{storage_file} not found. Running setup script...")
        run_script('setup_storage.py', [])
    else:
        print(f"Loaded storage information from {storage_file}")

def start_processing(set_name, image_set, df, df_conditions):
    book_details_path = f'{set_name}_book_details.json'
    additional_details_path = f'{set_name}_additional_details.json'

    start_time = time.time()
    image_process_result = run_script('image_processing.py', image_set + [book_details_path])
    end_time = time.time()
    print(f"Image processing for {set_name} took {end_time - start_time} seconds.")

    if image_process_result != 0:
        print(f"Error processing images for set {set_name}.")
        return df, df_conditions

    if not os.path.exists(book_details_path):
        print(f"Error: {book_details_path} was not created.")
        return df, df_conditions

    form_process_result = run_script('form_processing.py', [set_name, book_details_path, additional_details_path, 'storage_spaces.xlsx'])
    if form_process_result != 0:
        print(f"Error processing form for set {set_name}.")
        return df, df_conditions

    if not os.path.exists(additional_details_path):
        print(f"Error: {additional_details_path} was not created.")
        return df, df_conditions

    with open(book_details_path) as f:
        book_details = json.load(f)
    with open(additional_details_path) as f:
        additional_details = json.load(f)

    combined_details = {**book_details, **additional_details}
    df = update_inventory(df, combined_details)
    df_conditions = update_condition_sheet(df_conditions, combined_details)

    print(f"Set {set_name} processing completed!")

    return df, df_conditions

def main():
    image_sets = select_images()
    total_sets = len(image_sets)

    filename = 'book_inventory.xlsx'
    condition_sheet_name = 'Sheet 2'

    if os.path.exists(filename):
        with pd.ExcelFile(filename) as xls:
            df = pd.read_excel(xls, sheet_name='Sheet1')
            df_conditions = pd.read_excel(xls, sheet_name=condition_sheet_name) if condition_sheet_name in xls.sheet_names else pd.DataFrame(columns=["Title", "Cover Condition", "Spine Condition", "Pages Condition", "Extent of Damage/Markings", "Binding Integrity", "Dust Jacket Condition", "Markings and Annotations", "Stains and Odours"])
        print(f"Loaded existing dataframe from {filename}")
    else:
        df = pd.DataFrame(columns=["Title", "Author", "Publisher", "Year", "Edition", "Pages", "Weight", "Dimensions", "Format", "ISBN-10", "ISBN-13", "Genre", "Cover Condition", "Spine Condition", "Pages Condition", "Extent of Damage/Markings", "Binding Integrity", "Dust Jacket Condition", "Markings and Annotations", "Stains and Odours", "Total Score", "Additional Information"])
        df_conditions = pd.DataFrame(columns=["Title", "Cover Condition", "Spine Condition", "Pages Condition", "Extent of Damage/Markings", "Binding Integrity", "Dust Jacket Condition", "Markings and Annotations", "Stains and Odours"])
        print("Created new dataframe.")

    # Call the metadata check and prompt script
    run_script('check_and_prompt_metadata.py', [])

    for set_name in image_sets:
        df, df_conditions = start_processing(set_name, image_sets[set_name], df, df_conditions)

    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        df_conditions.to_excel(writer, sheet_name=condition_sheet_name, index=False)
    print(f"Updated dataframe saved to {filename}")

    # Call the metadata generation script
    run_script('generate_image_metadata.py', [])

if __name__ == "__main__":
    main()
