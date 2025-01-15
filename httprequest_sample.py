import requests

url = "https://www.sec.gov/Archives/edgar/data/320193/000032019321000105/aapl-20210925.htm"
headers = {
    "User-Agent": "Georges Nganou <nganouwg001@gmail.com>",
    "Accept-Encoding": "gzip, deflate",
    "Host": "www.sec.gov"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("Request succeeded!")
    with open("data/aapl_10k_2021.html", "wb") as file:
        file.write(response.content)
    print("10-K downloaded successfully.")
else:
    print(f"Failed with status code: {response.status_code}")