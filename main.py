import os
import subprocess
import pandas as pd
from tkinter import Tk, filedialog
import json

def select_images():
    Tk().withdraw()  # Hide the root window
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
    return image_sets

def run_script(script_path, args):
    subprocess.run(['python', script_path] + args)

def update_inventory(df, book_details):
    new_row = pd.DataFrame([book_details])
    updated_df = pd.concat([df, new_row], ignore_index=True)
    return updated_df

def check_storage_information():
    storage_file = 'storage_spaces.xlsx'
    if not os.path.exists(storage_file):
        print(f"{storage_file} not found. Running setup script...")
        run_script('setup.py', [])
    else:
        print(f"Loaded storage information from {storage_file}")

def main():
    check_storage_information()
    
    image_sets = select_images()
    
    filename = 'book_inventory.xlsx'
    if os.path.exists(filename):
        df = pd.read_excel(filename)
        print(f"Loaded existing dataframe from {filename}")
    else:
        df = pd.DataFrame(columns=["Title", "Author", "Publisher", "Year", "Edition", "Pages", "Weight", "Dimensions", "Format", "ISBN-10", "ISBN-13", "Genre"])
        print("Created new dataframe.")

    json_files_to_cleanup = []

    for set_name, image_set in image_sets.items():
        print(f"Processing set: {set_name}")

        # Define output file paths
        book_details_path = f'{set_name}_book_details.json'
        additional_details_path = f'{set_name}_additional_details.json'
        
        # Add paths to cleanup list
        json_files_to_cleanup.append(book_details_path)
        json_files_to_cleanup.append(additional_details_path)

        # Run the BookTool script for the image set
        run_script('BookTool.py', image_set + [book_details_path])

        # Run the form-filling script for additional details
        storage_spaces_path = 'storage_spaces.xlsx'  # Path to storage spaces Excel file
        run_script('form_fill.py', [set_name, book_details_path, additional_details_path, storage_spaces_path])

        # Load temporary files produced by both scripts and consolidate data
        with open(book_details_path) as f:
            book_details = json.load(f)
        with open(additional_details_path) as f:
            additional_details = json.load(f)
        
        combined_details = {**book_details, **additional_details}
        df = update_inventory(df, combined_details)
    
    print("Saving the dataframe to Excel file...")
    df.to_excel(filename, index=False, engine='openpyxl')
    print(f"Data saved to {filename}")

    # Cleanup JSON files
    for json_file in json_files_to_cleanup:
        try:
            os.remove(json_file)
            print(f"Removed temporary file: {json_file}")
        except OSError as e:
            print(f"Error removing temporary file {json_file}: {e}")

if __name__ == "__main__":
    main()
