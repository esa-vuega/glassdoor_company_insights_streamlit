import streamlit as st
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from fake_useragent import UserAgent
import random
import time

# Function to install geckodriver for Selenium on Streamlit Cloud
@st.cache_resource
def install_ff_driver():
    os.system('sbase install geckodriver')  # Install geckodriver using seleniumbase
    os.system('ln -s /home/appuser/venv/lib/python3.7/site-packages/seleniumbase/drivers/geckodriver /home/appuser/venv/bin/geckodriver')

# Install driver only once per session
_ = install_ff_driver()

# Set up Selenium with Firefox in headless mode
opts = FirefoxOptions()
ua = UserAgent()
opts.add_argument(f"user-agent={ua.random}")
opts.add_argument("--headless")
browser = webdriver.Firefox(options=opts)

# Function to get Glassdoor company ID (adjust the logic as needed)
def get_company_id_selenium(company_name):
    search_url = f"https://www.glassdoor.com/Search/results.htm?keyword={company_name.replace(' ', '%20')}"
    browser.get(search_url)
    time.sleep(random.uniform(2, 5))
    st.write(f"Searching for: {company_name} on Glassdoor...")

    try:
        # Wait for the page to load and find the first company link (modify the XPath based on your requirement)
        company_link = browser.find_element(By.XPATH, "//a[@data-test='company-tile']")
        company_url = company_link.get_attribute('href')
        parts = company_url.split('-EI_IE')
        company_name = parts[0].split('Working-at-')[-1]
        company_id = parts[1].split('.')[0]

        return company_name, company_id
    except Exception as e:
        st.error(f"Failed to retrieve company ID: {e}")
        return None, None

# Function to scrape Glassdoor reviews (adjust logic based on the structure of the review page)
def fetch_glassdoor_reviews_selenium(company_name):
    glassdoorName, glassdoorID = get_company_id_selenium(company_name)
    if glassdoorName and glassdoorID:
        try:
            url = f"https://www.glassdoor.com/Reviews/{glassdoorName}-Reviews-E{glassdoorID}.htm"
            browser.get(url)
            st.write(f"Fetching reviews from: {url}")
            # Print the page source to Streamlit (or save to file)
            page_source = browser.page_source
            with open("page_source.html", "w", encoding="utf-8") as f:
                f.write(page_source)
            # Get the overall rating
            overall_rate_elem = browser.find_element(By.CLASS_NAME, "rating-headline-average_ratingContainer__PcIL1")
            overall_rate = overall_rate_elem.text

            # Extract reviews
            reviews_list = browser.find_elements(By.XPATH, "//ol[@class='ReviewsList_reviewsList__yepAi']/li")
            review_list = []

            for review_elem in reviews_list:
                title = review_elem.find_element(By.CLASS_NAME, 'review-details_titleHeadline__Bjso2').text
                pros = review_elem.find_element(By.CLASS_NAME, 'review-details_pro__ZiMB2').text
                cons = review_elem.find_element(By.CLASS_NAME, 'review-details_con__TuzoC').text
                rate = review_elem.find_element(By.CLASS_NAME, "review-details_subRatingContainer__eEV95").text

                # Remove "Pros" and "Cons" labels from texts
                review_list.append({
                    'title': title.strip(),
                    'pros': pros.strip()[4:],  # Remove first 4 characters (label "Pros")
                    'cons': cons.strip()[4:],  # Remove first 4 characters (label "Cons")
                    'rate': rate.strip()
                })

            return overall_rate, review_list
        except Exception as e:
            st.error(f"Failed to fetch reviews: {e}")
            return None, []
    else:
        return None, []

# Streamlit UI
st.title("Glassdoor Reviews Fetcher (Selenium)")

# Input company name
company_name_input = st.text_input("Enter Company Name", "American University in Cairo")

if st.button("Fetch Reviews"):
    if company_name_input:
        overall_rate, company_reviews = fetch_glassdoor_reviews_selenium(company_name_input)

        if overall_rate and company_reviews:
            # Display overall rating
            st.write(f"Overall Rating: {overall_rate}")

            # Display reviews
            st.subheader("Reviews:")
            for idx, review in enumerate(company_reviews):
                st.write(f"**Review {idx + 1}:**")
                st.write(f"**Title:** {review['title']}")
                st.write(f"**Pros:** {review['pros']}")
                st.write(f"**Cons:** {review['cons']}")
                st.write(f"**Rating:** {review['rate']}")
                st.write("---")
        else:
            st.error("Failed to fetch reviews or no reviews found.")
    else:
        st.error("Please enter a company name.")
