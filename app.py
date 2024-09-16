import requests
from bs4 import BeautifulSoup

# The URL of the company page
url = "https://www.allabolag.se/5591764955/vuega-nordic-ab"

# Custom headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Send a GET request to fetch the content of the webpage
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the page content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract data from each div using the respective id
    bokslut = soup.find('div', id='bokslut')
    befattningar = soup.find('div', id='befattningar')
    verksamhet = soup.find('div', id='verksamhet')
    handelser = soup.find('div', id='handelser')
    fordon = soup.find('div', id='fordon')

    # Print the extracted data (You can modify this to store or further process it)
    print("Bokslut: ", bokslut.text if bokslut else "Not Found")
    print("Befattningar: ", befattningar.text if befattningar else "Not Found")
    print("Verksamhet: ", verksamhet.text if verksamhet else "Not Found")
    print("Händelser: ", handelser.text if handelser else "Not Found")
    print("Fordon: ", fordon.text if fordon else "Not Found")
else:
    print("Failed to retrieve the webpage. Status code:", response.status_code)
