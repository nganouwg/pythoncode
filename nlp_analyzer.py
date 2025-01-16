

#Apply natural language processing (NLP) to analyze sections (e.g., sentiment analysis or keyword extraction).

'''
    To extract information about the company's products and services from the cleaned 10-K text
    we can use Named Entity Recognition (NER) and keyword extraction techniques.

'''

import spacy


# Predefined list of common stock market sectors
SECTOR_KEYWORDS = [
    "Technology", "Healthcare", "Financials", "Consumer Discretionary", 
    "Consumer Staples", "Energy", "Industrials", "Utilities", 
    "Real Estate", "Communication Services", "Materials"
]

def extract_products_and_services(text):
    """
    Extracts products and services mentioned in the text using Named Entity Recognition (NER).

    :param text: The input plain text
    :return: A list of extracted products and services
    """
    nlp = spacy.load("en_core_web_sm")  # Load spaCy's English model
    doc = nlp(text)

    # Extract entities of type PRODUCT or other relevant categories
    products_and_services = []
    for ent in doc.ents:
        if ent.label_ in {"PRODUCT", "ORG"}:  # Adjust based on observed data
            products_and_services.append(ent.text)

    return set(products_and_services)  # Remove duplicates

def get_products_and_services(filename):
    # Load the cleaned text file
    with open(filename, "r", encoding="utf-8") as file:
        cleaned_text = file.read()

    # Extract products and services
    extracted_info = extract_products_and_services(cleaned_text)

    # Save results to a file
    with open("data/products_and_services.txt", "w", encoding="utf-8") as file:
        file.write("\n".join(extracted_info))

    print("Extracted products and services saved to 'products_and_services.txt'")

def extract_sectors(text):
    """
    Extracts stock market sectors mentioned in the text.

    :param text: The input plain text
    :return: A list of detected sectors
    """
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    # Search for sector-related terms
    detected_sectors = set()
    for token in doc:
        if token.text in SECTOR_KEYWORDS:
            detected_sectors.add(token.text)
    
    # Check for phrases or patterns around "sector" or "industry"
    for sent in doc.sents:
        if "sector" in sent.text.lower() or "industry" in sent.text.lower():
            for keyword in SECTOR_KEYWORDS:
                if keyword in sent.text:
                    detected_sectors.add(keyword)

    return list(detected_sectors)

def get_sectors(filename):
    # Load the cleaned text file
    with open(filename, "r", encoding="utf-8") as file:
        cleaned_text = file.read()

    # Extract sectors
    sectors = extract_sectors(cleaned_text)

    # Save the results
    with open("data/sectors_detected.txt", "w", encoding="utf-8") as file:
        file.write("\n".join(sectors))

    print("Detected sectors saved to 'sectors_detected.txt'")


if __name__ == "__main__":

    #get_products_and_services(filename="data/Item_1_cleaned.txt")

    get_sectors(filename="data/Item_1_cleaned.txt")