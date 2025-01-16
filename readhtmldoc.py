import html 
import re 
from bs4 import BeautifulSoup


def extract_section(soup, section_name):
    """
    Extracts a specific section from the 10-K HTML content.

    :param soup: BeautifulSoup object of the 10-K content
    :param section_name: The name of the section to extract (e.g., "Item 1.")
    :return: The extracted section text or None if not found
    """
    #for string in soup.stripped_strings:
    #    if "Item 1" in string:
    #        print(string)

    # Locate the section header
    section = soup.find(
        "div",
        style=lambda style: style and "padding-left:45pt" in style,
        string=lambda text: text and section_name in text
    )
    if not section:
        print(f"Section '{section_name}' not found.")
        return None
    
    print(section)
    
    # Get the parent tag of the section header
    parent = section.find_parent()

    print(f"{parent}"[:1000])
    
    # Collect all sibling elements until the next section
    section_content = []
    for sibling in parent.find_next_siblings():
        if sibling.name and any(f"item {i}" in sibling.get_text(strip=True).lower() for i in range(2, 16)):
            break  # Stop at the next "Item" header
        section_content.append(sibling)

    # Combine the extracted content
    return "\n".join(str(tag) for tag in section_content)

def clean_html_to_text(html_content):
    """
    Cleans the extracted HTML content and converts it to plain text.

    :param html_content: The raw HTML content
    :return: Cleaned plain text
    """
    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')

    # Remove unnecessary tags
    for tag in soup(['style', 'script']):
        tag.decompose()  # Remove the tag and its contents

    # Extract plain text
    text = soup.get_text(separator="\n", strip=True)

    # Decode HTML entities
    text = html.unescape(text)

    # Normalize special characters
    text = re.sub(r'\u00A0', ' ', text)  # Replace non-breaking space
    text = re.sub(r'\u2019', "'", text)  # Replace right single quote/apostrophe
    text = re.sub(r'\u201C|\u201D', '"', text)  # Replace left/right double quotes

    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Optional: Normalize text (e.g., lowercase)
    # text = text.lower()

    return text

def gethtmlsections(filename):
    with open(filename, "r", encoding='utf-8') as file:
        html_content = file.read()

    # Parse the file
    soup = BeautifulSoup(html_content, features="xml")

    # Extract sections
    sections_to_extract = [#"Item 1.", 
                        "Item 7."
                        ]
    for section in sections_to_extract:
        extracted_text = extract_section(soup, section)
        if extracted_text:
            # Save each section to a file
            filename = f"data/{section.replace(' ', '_').replace('.', '')}.html"
            with open(filename, "w", encoding="utf-8") as file:
                file.write(extracted_text)
            print(f"Extracted '{section}' and saved to '{filename}'")

def htmltoplaintext(filename):
    with open(filename, "r", encoding="utf-8") as file:
        extracted_html = file.read()

    # Clean and convert to plain text
    cleaned_text = clean_html_to_text(extracted_html)

    # Save the plain text to a file
    with open("data/Item_1_cleaned.txt", "w", encoding="utf-8") as file:
        file.write(cleaned_text)

    print("Cleaned text saved to 'Item_1_cleaned.txt'")

if __name__ == "__main__":

    #TODO - Return the list of html files
    #gethtmlsections(filename="data/aapl_10k.html")   

    htmltoplaintext(filename="data/Item_1.html")

    
