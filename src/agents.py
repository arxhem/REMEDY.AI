import os
import traceback
from typing import Any, Dict, List, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
# import google
import google.generativeai as genai
import pathlib
import textwrap
from IPython.display import Markdown
import PIL.Image
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from crewai import Agent, Task, Crew
from langchain_community.chat_models import AzureChatOpenAI
from crewai_tools import ScrapeWebsiteTool
import folium
from folium.plugins import MarkerCluster, MiniMap
import json 
import re
import requests

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument('--headless')  # Run in headless mode (without opening browser window)
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Create a new WebDriver instance


from dotenv import load_dotenv
load_dotenv()

AZURE_OPENAI_ENDPOINT=os.getenv("AZURE_OPENAI_API_BASE")
AZURE_OPENAI_KEY=os.getenv("AZURE_OPENAI_API_KEY")
AZURE_VERSION=os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_TYPE=os.getenv("AZURE_OPENAI_API_TYPE")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class Document:
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}

def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

# Configure the Generative AI client
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('models/gemini-pro-vision')



def scrapeFromLocation(speciality, location):
    # Open the URL
    driver = webdriver.Chrome(options=chrome_options)
    speciality.replace(' ', '%20')
    location.replace(' ', '%20')
    driver.get(f'https://www.practo.com/search/doctors?results_type=doctor&q=%5B%7B%22word%22%3A%22{speciality}%22%2C%22autocompleted%22%3Atrue%2C%22category%22%3A%22subspeciality%22%7D%2C%7B%22word%22%3A%22{location}%22%2C%22autocompleted%22%3Atrue%2C%22category%22%3A%22locality%22%7D%5D&city=Bangalore')
    # Get page source and parse it with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Keep scrolling to the bottom of the page until no more content is loaded
    while True:
        # Scroll to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait for some time to allow content to load
        time.sleep(2)  # Adjust delay as needed
        last_height = driver.execute_script("return document.body.scrollHeight")
        # Check if the page height has changed after scrolling
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Get the updated page source after scrolling
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Navigate to the container with all doctor cards
    doctor_cards = soup.find_all('div', class_='u-border-general--bottom')

    intro='https://www.practo.com/'
    urls=[]
    # Extract URLs from each card
    for card in doctor_cards:
        try:
            # Try to find the div containing the <a> tag
            div_tag = card.find('div', class_='info-section')
            if div_tag:
                # Within the div, find the <a> tag
                anchor_tag = div_tag.find('a', href=True)
                if anchor_tag:
                    url = anchor_tag['href']
                    urls.append(intro+url)
                else:
                    logging.info("URL not found within the div.")
            else:
                logging.info("Div tag not found in the card.")

            
        except AttributeError as e:
            logging.info(f"AttributeError: {e}")
    logging.info(f"Found {urls} URLs.")
    # Close the WebDriver
    driver.quit()
    return urls

def AgenticScrap(urls):
    llm = AzureChatOpenAI(
        openai_api_version=AZURE_VERSION,
        openai_api_key=AZURE_OPENAI_KEY,
        openai_api_base=AZURE_OPENAI_ENDPOINT,
        openai_api_type=AZURE_OPENAI_TYPE,
        deployment_name="shecodes",
        temperature=0.7
    )
    urls = urls[:10]
    with open('results.txt', 'a') as f:
        for i in urls:
            site = i
            web_scrape_tool = ScrapeWebsiteTool(website_url=site)

            web_scraper_agent = Agent(
                role='Web Scraper',
                goal='Effectively Scrape data on the websites for your company',
                backstory='''You are an expert web scraper, your job is to scrape the data of the doctors on the given website. Try to scrape information like name of the doctor, Doctor specialization, doctor qualification and address of the doctor from the info section and the star rating and fee. Don't Scrape anything other than mentioned. I don't want Patient Stories, consult Q&A
                            give the out put in the form of dictionaries with keys as doctor_name, specialization, address, star_rating,fees and experience. And experience only years. Don't give the rupee symbol in the fee key's value. 
                            ''',
                tools=[web_scrape_tool],
                verbose=True,
                llm=llm
            )

            web_scraper_task = Task(
                description='''Scrape the relevant data like  name of the doctor, Doctor specialization, doctor qualification and address of the doctor from the info section and the star rating and fee. Don't Scrape anything other than mentioned. I don't want Patient Stories, consult Q&A
                            give the out put in the form of dictionaries with keys as doctor_name, specialization, address, star_rating,fees and experience. And experience only years. Don't give the rupee symbol in the fee key's value. on the site requested in the backstory, so people can get an idea about nearby best doctors to consult''',
                expected_output="All the required content of the website as stated.",
                agent=web_scraper_agent,
                output_file='data.txt'
            )

            crew = Crew(
                agents=[web_scraper_agent],
                tasks=[web_scraper_task],
                verbose=2,
            )

            result = crew.kickoff()
            print(result)
            # Write each result as a JSON object in a separate line
            f.write(json.dumps(result) + '\n')



def get_coordinates(address, api_key):
    # Construct the URL for the Geocoding API
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={requests.utils.quote(address)}&key={api_key}"

    # Send the GET request to the API
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        if 'results' in data and len(data['results']) > 0:
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            print(f"No results found for address: {address}")
            return None
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

# User location data

def extract_addresses_from_json(file_path):
    addresses = []
    with open(file_path, 'r') as file:
        data = json.load(file)
        for entry in data:
            if 'address' in entry and 'doctor_name' in entry:
                addresses.append((entry['address'], entry['doctor_name']))
    return addresses

def create_map(addresses, api_key, user):
    # Initialize the map with a light mode tile
    user_location = {'latitude':{user.lat}, 'longitude': {user.long}, 'name': 'User Location'}
    m = folium.Map(location=[user.lat, user.long], zoom_start=13, tiles='OpenStreetMap')

    # Add user marker with a popup and a tooltip
    folium.Marker(
        location=[user_location['latitude'], user_location['longitude']],
        popup=folium.Popup(f"<b>{user_location['name']}</b>", max_width=300),
        tooltip='User Location',
        icon=folium.Icon(color='blue', icon='user', prefix='fa')
    ).add_to(m)

    # Initialize marker cluster for doctors
    marker_cluster = MarkerCluster().add_to(m)

    # Iterate through each address
    for address, doctor_name in addresses:
        coordinates = get_coordinates(address, api_key)
        if coordinates:
            latitude, longitude = coordinates
            folium.Marker(
                location=[latitude, longitude],
                popup=folium.Popup(f"<b>{doctor_name}</b>", max_width=300),
                tooltip=doctor_name,
                icon=folium.Icon(color='red', icon='plus-square', prefix='fa')
            ).add_to(marker_cluster)

            # Draw line from user to doctor
            folium.PolyLine(
                locations=[
                    [user_location['latitude'], user_location['longitude']],
                    [latitude, longitude]
                ],
                color='green',
                weight=1
            ).add_to(m)

    # Add a mini-map for better navigation
    mini_map = MiniMap(toggle_display=True)
    m.add_child(mini_map)

    # Return the map object
    return m


def extract_dictionaries_from_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Regular expression to match JSON-like dictionaries
    dict_pattern = re.compile(r'\{.*?\}', re.DOTALL)
    
    # Find all matches in the file content
    dict_matches = dict_pattern.findall(content)
    
    return dict_matches

def preprocess_dict_string(dict_str):
    # Replace single quotes with double quotes if necessary
    dict_str = dict_str.replace("'", '"')
    return dict_str

def extract_dictionaries(dict_list):
    dictionaries = []
    for dict_str in dict_list:
        try:
            dict_str = preprocess_dict_string(dict_str)
            data = json.loads(dict_str)
            dictionaries.append(data)
        except json.JSONDecodeError:
            print(f"Error decoding JSON: {dict_str}")
    
    return dictionaries

def save_dictionaries_to_json(dictionaries, output_file):
    with open(output_file, 'w') as file:
        json.dump(dictionaries, file, indent=4)

