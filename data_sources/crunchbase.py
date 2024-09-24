
import requests

API_KEY = "83268cac2332bf2a8b9a2b41a49ef745"
companey = 'google'
url = f"https://api.crunchbase.com/v4/data/entities/organizations/{companey}?card_ids=founders,raised_funding_rounds&field_ids=categories,short_description,rank_org_company,founded_on,website,facebook,created_at&user_key={API_KEY}"

headers = {
    'X-Cb-User-Key': API_KEY
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print("Error:", response.status_code)

