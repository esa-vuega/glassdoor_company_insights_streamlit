import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import streamlit as st
import matplotlib.pyplot as plt

# Function to initialize the Selenium Chrome driver in headless mode
def init_driver():
    options = Options()
    options.headless = True  # Ensure headless mode is enabled
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')  # Disable GPU in case you are running on Linux
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Function to search company by name using Selenium and BeautifulSoup
def search_company_by_name(company_name):
    url = f"https://www.allabolag.se/what/{company_name}"
    
    # Use Selenium to load the page
    browser = init_driver()
    browser.get(url)
    
    # Parse the page source with BeautifulSoup
    html = BeautifulSoup(browser.page_source, 'html.parser')
    browser.quit()  # Close the browser after scraping
    
    # Find the company search results
    results_list = html.find_all('article', class_='box tw-border-gray-200')
    company_results = []
    
    if results_list:
        for result in results_list:
            # Extract company name
            company_name_tag = result.find('h2', class_='search-results__item__title')
            if company_name_tag:
                org_name = company_name_tag.text.strip()
                
                # Extract organization number
                org_number_tag = result.find('dd')
                if org_number_tag:
                    org_number = org_number_tag.text.strip()
                    company_results.append((org_name, org_number))
        
        return company_results
    else:
        return None

# Function to scrape data from a specific company page
def scrape_company_data(org_number, company_name):
    company_url = f"https://www.allabolag.se/{org_number.replace('-', '')}/{company_name.replace(' ', '-')}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    response = requests.get(company_url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract financial data from the webpage
        key_figures = soup.find('div', class_='company-account-figures')
        data = {}
        
        if key_figures:
            # Extract key financial data
            table = key_figures.find('table', class_='figures-table')
            if table:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) > 1:
                        data[row.th.text.strip()] = cols[0].text.strip()
        
        # Extract ratios from the chart
        ratios_section = soup.find('div', class_='chart chart--bar ct-chart')
        if ratios_section:
            ratios_data = {}
            labels = ratios_section.find_all('label', class_='chart__label')
            values = ratios_section.find_all('input', class_='chart__data')

            for i, label in enumerate(labels):
                year = label.text.strip()
                turnover = values[i * 2].get('value')
                res_fin = values[i * 2 + 1].get('value')
                ratios_data[year] = [turnover, res_fin]
            
            data['Ratios'] = ratios_data
        
        return data if data else "No financial data found."
    
    else:
        return f"Failed to retrieve the webpage. Status code: {response.status_code}"

# Function to plot the ratios
def plot_ratios(ratios_data):
    years = []
    turnover = []
    res_fin = []
    res_fin_colors = []

    # Collect data for plotting
    for year, values in ratios_data.items():
        years.append(year)
        turnover_value = float(values[0].replace(',', '').replace(' KSEK', '').replace(' ', '')) if values[0] else 0
        res_fin_value = float(values[1].replace(',', '').replace(' KSEK', '').replace(' ', '')) if values[1] else 0
        
        turnover.append(turnover_value)
        res_fin.append(res_fin_value)

        # Determine color for Res. e. fin
        if res_fin_value < 0:
            res_fin_colors.append('red')
        else:
            res_fin_colors.append('green')

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 6))
    width = 0.35
    ax.bar([x - width/2 for x in range(len(years))], turnover, width=width, label="Turnover", color='blue')
    ax.bar([x + width/2 for x in range(len(years))], res_fin, width=width, label="Res. e. fin", color=res_fin_colors)

    ax.set_xlabel('Years')
    ax.set_ylabel('KSEK')
    ax.set_title('Turnover and Res. e. fin Over the Years')
    ax.set_xticks(range(len(years)))
    ax.set_xticklabels(years)
    ax.legend()

    return fig

# Streamlit app
st.title('Company Search and Financial Data Scraper')

# Create a form for user input
with st.form("company_search_form"):
    company_name = st.text_input('Enter the company name:', '')
    search_button = st.form_submit_button(label='Search Company')

# Initialize session state for company options and selected data
if 'company_options' not in st.session_state:
    st.session_state.company_options = None
if 'selected_company_data' not in st.session_state:
    st.session_state.selected_company_data = None
if 'selected_company_name' not in st.session_state:
    st.session_state.selected_company_name = None
if 'selected_org_number' not in st.session_state:
    st.session_state.selected_org_number = None

if search_button and company_name:
    st.write(f"Searching for companies matching: {company_name}")
    company_options = search_company_by_name(company_name.replace(' ', '%20'))
    
    if company_options:
        # Store the company options in session state
        st.session_state.company_options = company_options
        
        st.write("Select a company from the dropdown below:")
        
        # Create a dropdown to select a company
        selected_company = st.selectbox("Choose a company:", [f"{name} (Org: {org})" for name, org in company_options])

        # If a company is selected from the dropdown, scrape its data
        if selected_company:
            selected_company_name, selected_org_number = selected_company.split(" (Org: ")
            selected_org_number = selected_org_number.strip(")")

            # Scrape financial data for the selected company when the company is selected
            st.session_state.selected_company_data = scrape_company_data(selected_org_number, selected_company_name)
            st.session_state.selected_company_name = selected_company_name
            st.session_state.selected_org_number = selected_org_number

# If a company has been selected, display its financial data
if st.session_state.selected_company_data is not None:
    company_data = st.session_state.selected_company_data
    selected_company = st.session_state.selected_company_name
    selected_org_number = st.session_state.selected_org_number

    if selected_company:
        st.write(f"Scraping data for {selected_company} (Org: {selected_org_number})")
        
        # Display the scraped data
        if isinstance(company_data, dict):
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Company Financial Data:**")
                for key, value in company_data.items():
                    if key != 'Ratios':
                        current_value = float(value.replace(' KSEK', '').replace(',', '').replace(' ', ''))
                        if current_value > 0:
                            st.markdown(f"<span style='color: green;'>{key}: {value}</span>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<span style='color: red;'>{key}: {value}</span>", unsafe_allow_html=True)

            with col2:
                if 'Ratios' in company_data:
                    st.write("**Ratios**")
                    table_data = [["Year", "Turnover", "Res. e. fin"]] + [[year, f"{ratio_values[0]} KSEK", f"{ratio_values[1]} KSEK"] for year, ratio_values in company_data['Ratios'].items()]
                    st.table(table_data)

            if 'Ratios' in company_data:
                st.write("**Ratios Plot:**")
                fig = plot_ratios(company_data['Ratios'])
                st.pyplot(fig)

            st.write("Data extracted from [Allabolag](https://www.allabolag.se/).")
        else:
            st.write(company_data)
