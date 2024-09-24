import requests
import csv

def get_company_insights(company_name, api_key):
    url = f"https://kgsearch.googleapis.com/v1/entities:search"
    
    # Parameters for the API request
    params = {
        'query': company_name,
        'key': api_key,
        'limit': 1,
        'indent': True,
    }

    # Sending the request to the Knowledge Graph API
    response = requests.get(url, params=params)

    if response.status_code == 200:
        # Parse and return the insights
        result = response.json()
        if 'itemListElement' in result and len(result['itemListElement']) > 0:
            entity = result['itemListElement'][0]['result']
            return {
                'name': entity.get('name', 'N/A'),
                'description': entity.get('description', 'N/A'),
                'detailed_description': entity.get('detailedDescription', {}).get('articleBody', 'N/A'),
                'url': entity.get('detailedDescription', {}).get('url', 'N/A'),
                'type': ', '.join(entity.get('@type', ['N/A'])),
                'image': entity.get('image', {}).get('contentUrl', 'N/A'),
                'identifier': entity.get('identifier', 'N/A'),
                'additional_type': ', '.join(entity.get('additionalType', ['N/A']))
            }
        else:
            return None  # No insights found
    else:
        return f"Error: {response.status_code}, {response.text}"

def save_insights_to_csv(insights, file_name):
    # Specify the column names for the CSV
    fieldnames = ['name', 'description', 'detailed_description', 'url', 'type', 'image', 'identifier', 'additional_type']

    # Writing to the CSV file
    with open(file_name, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Write the header
        writer.writeheader()

        # Write the company insights (if available)
        if insights:
            writer.writerow(insights)
        else:
            print("No data available to save.")

api_key = 'AIzaSyDrL5RucJxjrEvTgdj1DmcosxoGAZPGuiA'
company_name = 'Google'
insights = get_company_insights(company_name, api_key)

if isinstance(insights, dict):
    print(insights)
    save_insights_to_csv(insights, 'company_insights.csv')
else:
    print(insights)
