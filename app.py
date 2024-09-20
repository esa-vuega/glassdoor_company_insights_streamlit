import streamlit as st
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

# Function to scrape data from the input URL
def scrape_company_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    response = requests.get(url, headers=headers)
    
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
            # Extract years and ratio values
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
            res_fin_colors.append('red')  # Color red if less than 0
        else:
            res_fin_colors.append('green')  # Otherwise blue

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 6))  # Set figure size
    width = 0.35
    ax.bar([x - width/2 for x in range(len(years))], turnover, width=width, label="Turnover", color='blue')
    ax.bar([x + width/2 for x in range(len(years))], res_fin, width=width, label="Res. e. fin", color=res_fin_colors)

    # Labels and title
    ax.set_xlabel('Years')
    ax.set_ylabel('KSEK')
    ax.set_title('Turnover and Res. e. fin Over the Years')
    ax.set_xticks(range(len(years)))
    ax.set_xticklabels(years)
    ax.legend()

    return fig

# Streamlit app
st.title('Company Financial Data and Ratios Scraper')

# Create a form for user input
with st.form("scrape_form"):
    company_url = st.text_input('Enter the company page URL:', 'https://www.allabolag.se/5591764955/vuega-nordic-ab')
    submit_button = st.form_submit_button(label='Scrape Data')

# When the form is submitted, scrape the data
if submit_button:
    if company_url:
        st.write(f"Scraping data from: {company_url}")
        company_data = scrape_company_data(company_url)
        
        # Display the scraped data
        if isinstance(company_data, dict):
            # Create two columns for the financial data
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Company Financial Data:**")
                for key, value in company_data.items():
                    if key != 'Ratios':
                        # Color coding based on increase/decrease
                        current_value = float(value.replace(' KSEK', '').replace(',', '').replace(' ', ''))  # Remove spaces
                        if current_value > 0:
                            st.markdown(f"<span style='color: green;'>{key}: {value}</span>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<span style='color: red;'>{key}: {value}</span>", unsafe_allow_html=True)

            with col2:
                if 'Ratios' in company_data:
                    st.write("**Ratios**")
                    # Adding headers for the table
                    table_data = [
                        ["Year", "Turnover", "Res. e. fin"]
                    ] + [
                        [year, f"{ratio_values[0]} KSEK", f"{ratio_values[1]} KSEK"] for year, ratio_values in company_data['Ratios'].items()
                    ]
                    st.table(table_data)

            # Plot the ratios as a bar chart in a separate row
            if 'Ratios' in company_data:
                st.write("**Ratios Plot:**")
                fig = plot_ratios(company_data['Ratios'])
                st.pyplot(fig)

            # Source note
            st.write("Data extracted from [Allabolag](https://www.allabolag.se/).")

        else:
            st.write(company_data)
    else:
        st.write("Please enter a valid URL.")
