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



def scrapFromLocation(speciality, location):
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
        deployment_name="shecodes", ## For getting diseases
        temperature=0.7
    )
    urls=urls[:10]
    for i in urls:
        site = i
        web_scrape_tool = ScrapeWebsiteTool(website_url=site)

        # Create agents
        web_scraper_agent = Agent(
            role='Web Scraper',
            goal='Effectively Scrape data on the websites for your company',
            backstory='''You are an expert web scraper, your job is to scrape all the data of the doctors on the given website. Try to scrape information like name of the doctor, Doctor specialization, doctor qualification and address of the doctor from the info section and the star rating and fee. Don't Scrape anything other than mentioned. I don't want Patient Stories, consult Q&A
            give the out put in the form of dictionaries with keys as doctor_name, specialization, address, star_rating,fees and experience. And experience only years 
                        ''',
            tools=[web_scrape_tool],
            verbose=True,
            llm=llm
        )

        # Define tasks
        web_scraper_task = Task(
            description='Scrape all the relevant data on the site requested by the agent, so people can get an idea about nearby best doctors to consult',
            expected_output='All the required content of the website as stated.',
            agent=web_scraper_agent,
            output_file='data.txt'
        )

        # Assemble a crew
        crew = Crew(
            agents=[web_scraper_agent],
            tasks=[web_scraper_task],
            verbose=2,
        )

        # Execute tasks
        result = crew.kickoff()
        print(result)

        with open('results.txt', 'a') as f:
            f.write(result+'\n')
