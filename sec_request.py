import requests
import os
import json

def fetch_latest_10k(cik):
    """
    Fetch the latest 10-K filing for a company using its CIK.

    :param cik: Central Index Key (CIK) of the company
    """
    base_url = "https://data.sec.gov/submissions/CIK"
    headers = {
        "User-Agent": "Georges Nganou <nganouwg001@gmail.com>",
        "Accept-Encoding": "gzip, deflate",
        "Host": "data.sec.gov"
    }

    # Pad the CIK with leading zeros to ensure it is 10 digits
    cik = str(cik).zfill(10)

    # Fetch the submission index
    url = f"{base_url}{cik}.json"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch data for CIK {cik}. HTTP Status: {response.status_code}")
        return

    data = response.json()

    #with open(f"data/CIK_submission{cik}.json","w") as f:
    #    json.dump(data, f)

    # Filter for 10-K filings
    filings = data.get("filings", {}).get("recent", {})
    if not filings:
        print(f"No filings found for CIK {cik}.")
        return

    form_types = filings.get("form", [])
    accession_numbers = filings.get("accessionNumber", [])
    filing_dates = filings.get("filingDate", [])
    document_urls = filings.get("primaryDocument", [])

    # Find the latest 10-K
    for i, form in enumerate(form_types):
        if form == "10-K":
            accession_number = accession_numbers[i].replace("-", "")
            document_url = document_urls[i]
            filing_date = filing_dates[i]

            # Construct the URL to download the filing
            download_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_number}/{document_url}"
            print(f"Downloading 10-K for CIK {cik}, Filing Date: {filing_date}")
            
            # Save the file locally
            filename = f"data/10-K_{cik}_{filing_date}.html"

            doc_response = requests.get(download_url, headers=headers)

            if doc_response.status_code == 200:
                print("Request succeeded!")
                with open(filename, "wb") as file:
                    file.write(doc_response.content)
                print("10-K downloaded successfully.")
            else:
                print(f"Failed with status code: {doc_response.status_code}")

            '''
            with requests.get(download_url, headers=headers, stream=True) as r:
                if r.status_code == 200:
                    with open(filename, "wb") as f:
                        f.write(r.content)
                    print(f"10-K saved as {filename}")
                else:
                    print(f"Failed to download the 10-K. HTTP Status: {r.status_code}")
            return
            '''

    print(f"No 10-K found for CIK {cik}.")

# Example: Fetch latest 10-K for a given CIK
cik_number = "0000320193"  # Example CIK for Apple Inc.
fetch_latest_10k(cik_number)


#https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/aapl-20240928.htm