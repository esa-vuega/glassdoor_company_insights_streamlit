import requests
from bs4 import BeautifulSoup

def fetch_glassdoor_reviews(company_name):
    url = f"https://www.glassdoor.com/Reviews/Ejada-Reviews-E453040.htm"  # Adjust URL as needed
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
    rate= soup.find('div',class_="rating-headline-average_ratingContainer__PcIL1")
    print("Rate", rate.text)
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
    
    return review_list

# Example: Fetch Glassdoor reviews about a company
company_reviews = fetch_glassdoor_reviews("American-University-in-Cairo")

print("\nReviews:\n")
for review in company_reviews:
    print(f"Rate:{review['rate']}\n{review['title']}\nPros:\n{review['pros']}\nCons:\n{review['cons']}\n")
