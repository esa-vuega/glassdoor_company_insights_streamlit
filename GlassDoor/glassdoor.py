import requests
from bs4 import BeautifulSoup
import streamlit as st
import cloudscraper

def get_company_id(company_name):
    search_url = f"https://www.glassdoor.com/Search/results.htm?keyword={company_name.replace(' ', '%20')}"
    print(search_url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://www.glassdoor.com/',
        'DNT': '1',  # Do Not Track
        'Cache-Control': 'max-age=0',
    }

    scraper = cloudscraper.create_scraper()
    response = scraper.get(search_url, headers=headers)
    st.write(response.headers)
    # response = requests.get(search_url, headers=headers)
    st.write(response.status_code)
    print(response.status_code)
    soup = BeautifulSoup(response.text, 'html.parser')

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
        st.error(f"Company '{company_name}' not found on Glassdoor.")
        return None, None
    

def fetch_glassdoor_reviews(company_name):
    glassdoorName, glassdoorID = get_company_id(company_name)
    if glassdoorName and glassdoorID:
        url = f"https://www.glassdoor.com/Reviews/{glassdoorName}-Reviews-E{glassdoorID}.htm"
        print(url)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.google.com/',
            'DNT': '1',  # Do Not Track
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'TE': 'Trailers'
        }

        response = requests.get(url, headers=headers)
        st.write(response.status_code)
        print(response.status_code)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Overall rating
        overall_rate = soup.find('div', class_="rating-headline-average_ratingContainer__PcIL1").text
        
        # Find reviews
        reviews = soup.find('ol', class_="ReviewsList_reviewsList__yepAi")
        reviews = reviews.find_all('li')
        
        # Extract title, pros, and cons with checks
        review_list = []
        for review in reviews:
            title = review.find('div', class_='review-details_titleHeadline__Bjso2')
            pros = review.find('div', class_="review-details_pro__ZiMB2")
            cons = review.find('div', class_="review-details_con__TuzoC")
            rate = review.find('div', class_="review-details_subRatingContainer__eEV95")

            if title and pros and cons:
                review_list.append({
                    'title': title.text.strip(),
                    'pros': pros.text.strip()[4:],  # Remove first 4 characters
                    'cons': cons.text.strip()[4:],  # Remove first 4 characters
                    'rate': rate.text.strip()
                })
        
        return overall_rate, review_list
    else:
        return None, []

# Helper function to convert rating to stars
# def display_stars(rating, max_stars=5):
#     filled_stars = "★" * int(float(rating))
#     empty_stars = "☆" * (max_stars - int(float(rating)))
#     return filled_stars + 


def display_stars(rating, max_stars=5):
    full_star_img = 'https://res.cloudinary.com/dwdrbmeng/image/upload/v1726581834/ef5kaqqtyfbksgvcegoj.png'
    half_star_img = 'https://res.cloudinary.com/dwdrbmeng/image/upload/v1726582152/kyqmy0chxyjeq0mt1dzf.png'
    empty_star_img = 'https://res.cloudinary.com/dwdrbmeng/image/upload/v1726581834/v48droljw5n3rgqmc1cz.png'

    rating=float(rating)
    full_stars = int(rating)
    half_star = 1 if (rating - full_stars) >= 0.5 else 0
    empty_stars = max_stars - full_stars - half_star
    
    star_html = ""
    
    # Add full stars
    star_html += f'<img src="{full_star_img}" width="20" style="display:inline-block;">' * full_stars
    
    # Add half star if applicable
    if half_star:
        star_html += f'<img src="{half_star_img}" width="20" style="display:inline-block;">'
    
    # Add empty stars
    star_html += f'<img src="{empty_star_img}" width="20" style="display:inline-block;">' * empty_stars
    
    # Display stars horizontally
    return f'<span style="margin-left: 10px; display: inline-block;">{star_html}</span>'
    

# Streamlit UI
st.title("Glassdoor Reviews Fetcher")

# Input company name
company_name_input = st.text_input("Enter Company Name", "American University in Cairo")

if st.button("Fetch Reviews"):
    if company_name_input:
        overall_rate, company_reviews = fetch_glassdoor_reviews(company_name_input)
        
        if overall_rate and company_reviews:
            # Display overall rating with stars
            rating_text = f"<span style='font-size: 24px; font-weight: bold;'>Overall Rating: {overall_rate}</span>"
            stars_html = display_stars(overall_rate)
            combined_html = f'<div style="display: flex; align-items: center;">{rating_text} {stars_html}</div>'

            # Use this in your main code
            st.markdown(combined_html, unsafe_allow_html=True)
            
            # Display reviews
            st.subheader(f"Reviews:")
            for idx, review in enumerate(company_reviews):
                # st.markdown(f"**Review {idx + 1}:**")
                review_rating_html = display_stars(review['rate'])
                st.markdown(f"**Rating:** {review['rate']} {review_rating_html}", unsafe_allow_html=True)
                st.write(f"**{review['title']}**")
                st.markdown(f"<span style='color: green; font-weight: bold;'>Pros:</span> \n\n{review['pros']}", unsafe_allow_html=True)
                st.markdown(f"<span style='color: red; font-weight: bold;'>Cons:</span> \n\n{review['cons']}", unsafe_allow_html=True)
    
                st.write("---")
        else:
            st.error("Failed to fetch reviews or no reviews found.")
    else:
        st.error("Please enter a company name.")