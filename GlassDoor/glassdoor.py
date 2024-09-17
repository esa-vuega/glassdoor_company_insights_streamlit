import requests
from bs4 import BeautifulSoup

def get_company_id(company_name):
    search_url = f"https://www.glassdoor.com/Search/results.htm?keyword={company_name.replace(' ', '%20')}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.google.com/',
        'DNT': '1',  # Do Not Track
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    print(search_url)
    # Find the first result that matches the company
    company_link = soup.find('a', {'data-test': 'company-tile'})
    
    if company_link:
        company_url = company_link['href']
        parts = company_url.split('-EI_IE')
    
        # Extract company name (first part after 'Working-at-')
        company_name = parts[0].split('Working-at-')[-1]
        
        # Extract company ID (the number part)
        company_id = parts[1].split('.')[0]
        
        return company_name, company_id
    else:
        print(f"Company '{company_name}' not found on Glassdoor.")
        return None, None
    

def fetch_glassdoor_reviews(company_name):
    glassdoorName, glassdoorID= get_company_id(company_name)
    url = f"https://www.glassdoor.com/Reviews/{glassdoorName}-Reviews-E{glassdoorID}.htm"
    print(url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.google.com/',
        'DNT': '1',  # Do Not Track
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    response = requests.get(url, headers=headers)
    # print(response)
    soup = BeautifulSoup(response.text, 'html.parser')
    overall_rate= soup.find('div',class_="rating-headline-average_ratingContainer__PcIL1").text
    reviews = soup.find('ol', class_="ReviewsList_reviewsList__yepAi")
    reviews = reviews.find_all('li')
    # Extract title and text with checks
    review_list = []
    for review in reviews:
        title = review.find('div', class_='review-details_titleHeadline__Bjso2')
        pros = review.find('div', class_="review-details_pro__ZiMB2")
        cons = review.find('div', class_="review-details_con__TuzoC")
        rate = review.find('div', class_="review-details_subRatingContainer__eEV95")

        if title and pros and cons:
            review_list.append({

                'title': title.text.strip(),
                'pros': pros.text.strip()[4:],
                'cons': cons.text.strip()[4:],
                'rate':rate.text.strip()
            })
    
    return overall_rate, review_list

# Example: Fetch Glassdoor reviews about a company
overall_rate, company_reviews = fetch_glassdoor_reviews("American university in cairo")

print("\nReviews:\n")
for review in company_reviews:
    print(f"Rate:{review['rate']}\n{review['title']}\nPros:\n{review['pros']}\nCons:\n{review['cons']}\n")
