import openai
import pytesseract
from PIL import Image
import pandas as pd
import requests
from tkinter import Tk, filedialog
import os
from dotenv import load_dotenv
import re
import json

# Load environment variables from .env file
load_dotenv()

# Initialize the openai client
api_key = os.environ.get("OPENAI_API_KEY")
if api_key:
    print("OpenAI API Key loaded successfully\n")
else:
    print("Failed to load OpenAI API Key\n")
openai.api_key = api_key

isbndb_api_url = "https://api2.isbndb.com/book"  # ISBNdb API endpoint
isbndb_api_key = os.environ.get("ISBNDB_API_KEY")
isbndb_api_key_set = bool(isbndb_api_key)

if not isbndb_api_key_set:
    print("ISBNdb API Key is not set. Skipping ISBNdb API queries.\n")

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
    6. Edition of the Book
    7. Genre of the Book

    If the information is not available, please state 'Not found' for that item.

    Text: {text}
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
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
        "6. Edition of the Book": "Edition",
        "7. Genre of the Book": "Genre"
    }
    for line in details_text.split('\n'):
        if ": " in line:
            key, value = line.split(": ", 1)
            mapped_key = mapping.get(key.strip(), key.strip())
            details_dict[mapped_key] = value.strip()
    return details_dict

def query_isbndb_api(isbn):
    url = f"{isbndb_api_url}/{isbn}"
    headers = {"Authorization": f"Bearer {isbndb_api_key}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error querying ISBNdb API: {e}\n")
        return {}

def supplement_book_details(book_details):
    if isbndb_api_key_set:
        isbn = book_details.get("ISBN-10") or book_details.get("ISBN-13")
        if isbn:
            api_data = query_isbndb_api(isbn)
            if 'book' in api_data:
                api_book_data = api_data['book']
                for key in ["Year", "Pages", "Weight", "Dimensions", "Format"]:
                    if key not in book_details or not book_details[key]:
                        book_details[key] = api_book_data.get(key, "Not found")
                        book_details[key] += " [Supplemented]"
                    else:
                        book_details[key] += " [Extracted]"
    return book_details

def generate_synopsis(book_details):
    prompt = f"""
    Using the following book details, write a brief synopsis of the book:

    Title: {book_details.get('Title')}
    Author: {book_details.get('Author')}
    Publisher: {book_details.get('Publisher')}
    Year: {book_details.get('Year')}
    Edition: {book_details.get('Edition')}
    Pages: {book_details.get('Pages')}
    Weight: {book_details.get('Weight')}
    Dimensions: {book_details.get('Dimensions')}
    Format: {book_details.get('Format')}
    ISBN-10: {book_details.get('ISBN-10')}
    ISBN-13: {book_details.get('ISBN-13')}
    Genre: {book_details.get('Genre')}
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        synopsis = response.choices[0].message['content']
        return synopsis
    except Exception as e:
        print(f"Error generating synopsis: {e}\n")
        return ""

def update_dataframe(df, book_details):
    book_details = supplement_book_details(book_details)
    new_row = pd.DataFrame([book_details])
    print("Book details to be added to the DataFrame:")
    for key, value in book_details.items():
        print(f"{key}: {value}")
    print("\n")
    
    updated_df = pd.concat([df, new_row], ignore_index=True)
    
    return updated_df

def process_image_set(image_set, output_path):
    combined_text = ""
    for image_path in image_set:
        print(f"Processing image: {image_path}\n")
        text = extract_text_from_image(image_path)
        combined_text += text + "\n"

    if combined_text.strip():
        book_details_and_description = get_book_details(combined_text)
        book_details = parse_book_details(book_details_and_description)
        with open(output_path, 'w') as f:
            json.dump(book_details, f)
        print(f"Book details saved to {output_path}")
        synopsis = generate_synopsis(book_details)
        print("Synopsis:\n", synopsis)
    else:
        print("No text extracted from images.\n")

def main(image_set_paths, output_path):
    process_image_set(image_set_paths, output_path)

if __name__ == "__main__":
    import sys
    image_set_paths = sys.argv[1:-1]
    output_path = sys.argv[-1]
    main(image_set_paths, output_path)
