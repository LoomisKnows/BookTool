# image_processing.py
import openai
import pytesseract
from PIL import Image
import json
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY")
openai.api_key = api_key

def extract_text_from_image(image_path):
    try:
        print(f"Extracting text from image: {image_path}")  # Debug print
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"Error extracting text from image: {e}")
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
        print("Sending request to OpenAI API")  # Debug print
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
        print(f"Error getting book details: {e}")
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

def process_image_set(image_set, output_path):
    combined_text = ""
    for image_path in image_set:
        print(f"Processing image: {image_path}")  # Debug print
        text = extract_text_from_image(image_path)
        combined_text += text + "\n"

    if combined_text.strip():
        book_details_and_description = get_book_details(combined_text)
        book_details = parse_book_details(book_details_and_description)
        with open(output_path, 'w') as f:
            json.dump(book_details, f)
        print(f"Book details saved to {output_path}")
    else:
        print("No text extracted from images.")

def main(image_set_paths, output_path):
    process_image_set(image_set_paths, output_path)

if __name__ == "__main__":
    import sys
    image_set_paths = sys.argv[1:-1]
    output_path = sys.argv[-1]
    main(image_set_paths, output_path)
