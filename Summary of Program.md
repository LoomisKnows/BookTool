### Program Summary

This program is designed to automate the process of cataloging books by extracting bibliographic details from images of book covers, supplementing this information with additional data from an external API, and organizing the details in an inventory system. The program also assigns storage spaces for the books based on their dimensions.

#### Key Components and Workflow:

1. **Image Selection and Text Extraction**:
   - Users select images of book covers using a graphical file dialog.
   - The program extracts text from these images using Optical Character Recognition (OCR) via the `pytesseract` library.

2. **Data Processing and Supplementation**:
   - The extracted text is analyzed using OpenAI's GPT-3.5 model to obtain bibliographic details such as the title, author, publisher, ISBN, edition, and genre.
   - If available, additional book details (e.g., year, pages, weight, dimensions, format) are supplemented using the ISBNdb API.

3. **Interactive Form for Additional Details**:
   - Users are prompted through a GUI form to provide or verify additional details that might not be captured through OCR and API queries.
   - The program assigns a suitable storage shelf based on the dimensions of the book and available shelf space.

4. **Inventory Management**:
   - The program maintains an inventory of books in an Excel file. It checks if storage information is available and runs a setup script to collect storage shelf data if necessary.
   - Book details are consolidated into a DataFrame and saved to an Excel file.

5. **Temporary File Cleanup**:
   - The program generates temporary JSON files during processing, which are cleaned up after the inventory is updated.

### Components Overview:

- **set_up.py**: Collects storage shelf information from the user and saves it to an Excel file.
- **main.py**: Orchestrates the workflow of selecting book images, extracting and updating inventory details, and managing storage information.
- **form_fill.py**: Provides a GUI form for users to fill in additional book details and assigns a storage shelf.
- **BookTool.py**: Extracts text from book cover images, retrieves book details using OpenAI's GPT-3.5, supplements details with data from the ISBNdb API, and generates a synopsis of the book.

By automating these processes, the program streamlines the cataloging of books, making it easier to maintain an organized and comprehensive inventory system.
