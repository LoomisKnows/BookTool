import openai
import pytesseract
from PIL import Image
import pandas as pd
import requests
from tkinter import Tk, filedialog, simpledialog
import os
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()

# Initialize the openai client
api_key = os.environ.get("OPENAI_API_KEY")
if api_key:
    print("OpenAI API Key loaded successfully\n")
else:
    print("Failed to load OpenAI API Key\n")
openai.api_key = api_key

library_api_url = "https://library.example.com/api"  # Replace with actual library API URL
library_api_key = os.environ.get("LIBRARY_API_KEY")
library_api_key_set = bool(library_api_key)

if not library_api_key_set:
    print("Library API Key is not set. Skipping library API queries.\n")

def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"Error extracting text from image: {e}\n")
        return ""

def get_book_details(text):
    prompt = f"""
    Analyse the following text and obtain the following data in a concise format:
    1. Title of the Book
    2. Name of the Author
    3. Name of the Publisher
    4. ISBN-10 of the Book
    5. ISBN-13 of the Book
    6. Year of Publishing
    7. Edition of the Book
    8. Number of Pages
    9. Weight of the Book
    10. Dimensions of the Book
    11. Hardback or Softback
    12. Genre of the Book

    Text: {text}
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        details = response.choices[0].message['content']
        return details
    except Exception as e:
        print(f"Error getting book details: {e}\n")
        return ""

def parse_book_details(details_text):
    details_dict = {}
    mapping = {
        "1. Title of the Book": "Title",
        "2. Name of the Author": "Author",
        "3. Name of the Publisher": "Publisher",
        "4. ISBN-10 of the Book": "ISBN-10",
        "5. ISBN-13 of the Book": "ISBN-13",
        "6. Year of Publishing": "Year",
        "7. Edition of the Book": "Edition",
        "8. Number of Pages": "Pages",
        "9. Weight of the Book": "Weight",
        "10. Dimensions of the Book": "Dimensions",
        "11. Hardback or Softback": "Format",
        "12. Genre of the Book": "Genre"
    }
    for line in details_text.split('\n'):
        if ": " in line:
            key, value = line.split(": ", 1)
            mapped_key = mapping.get(key.strip(), key.strip())
            details_dict[mapped_key] = value.strip()
    return details_dict

def query_library_api(isbn):
    url = f"{library_api_url}/books"
    params = {"isbn": isbn}
    headers = {"Authorization": f"Bearer {library_api_key}"}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error querying library API: {e}\n")
        return {}

def update_dataframe(df, book_details):
    # Query library API for missing information if the API key is set
    if library_api_key_set:
        isbn = book_details.get("ISBN-10") or book_details.get("ISBN-13")
        if isbn:
            api_data = query_library_api(isbn)
            for key, value in api_data.items():
                if key in book_details and book_details[key] == "Data not provided in the given text":
                    book_details[key] = value

    # Prompt for remaining missing information
    for key, value in book_details.items():
        if value == "Data not provided in the given text":
            user_input = simpledialog.askstring("Input", f"Please enter the {key} for the book '{book_details['Title']}' by {book_details['Author']}:")
            if user_input:
                book_details[key] = user_input
    
    new_row = pd.DataFrame([book_details])
    print("Book details to be added to the DataFrame:")
    for key, value in book_details.items():
        print(f"{key}: {value}")
    print("\n")
    
    updated_df = pd.concat([df, new_row], ignore_index=True)
    
    return updated_df

def select_images():
    Tk().withdraw()  # We don't want a full GUI, so keep the root window from appearing
    file_paths = filedialog.askopenfilenames(
        title="Select Images",
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
    )
    image_sets = {}
    for file_path in file_paths:
        # Extract set name from file name (assuming format: setname_bookname.ext)
        set_name = os.path.basename(file_path).split('_')[0]
        if set_name not in image_sets:
            image_sets[set_name] = []
        image_sets[set_name].append(file_path)
    return image_sets

def process_image_set(image_set, df):
    combined_text = ""
    for image_path in image_set:
        print(f"Processing image: {image_path}\n")
        text = extract_text_from_image(image_path)
        combined_text += text + "\n"

    if combined_text.strip():
        book_details_and_description = get_book_details(combined_text)
        book_details = parse_book_details(book_details_and_description)
        df = update_dataframe(df, book_details)
    else:
        print("No text extracted from images.\n")
    return df

def main():
    image_sets = select_images()
    
    filename = 'book_inventory.xlsx'
    if os.path.exists(filename):
        df = pd.read_excel(filename)
        print(f"Loaded existing dataframe from {filename}\n")
    else:
        df = pd.DataFrame(columns=["Title", "Author", "Publisher", "Year", "Edition", "Pages", "Weight", "Dimensions", "Format", "ISBN-10", "ISBN-13", "Genre"])
        print("Created new dataframe.\n")

    for set_name, image_set in image_sets.items():
        print(f"Processing set: {set_name}\n")
        df = process_image_set(image_set, df)

    print("Saving the dataframe to Excel file...\n")
    df.to_excel(filename, index=False, engine='openpyxl')
    print(f"Data saved to {filename}\n")

if __name__ == "__main__":
    main()
