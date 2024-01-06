from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import Utility
import time

class wait_for_number_of_elements_to_load:
    def __init__(self,by_object,locator_string,num_objects = 2):
        self.by_object = by_object
        self.locator_string = locator_string
        self.num_objects = num_objects
    def __call__(self, driver):
        elements = driver.find_elements(self.by_object,self.locator_string)
        if(len(elements)>=self.num_objects):
            return elements
        else:
            return False

class GoogleJobScraper:
    def __init__(self):

        # Set options for browser
        self.options = None

        # Initialize WebDriver
        self.service = None
        self.driver = None
        self.search_term = None

    def start_driver(self,driver_path, browser_path,search_term,minimize = False):
        # Set options for browser
        self.options = Options()
        self.options.binary_location = browser_path

        # Initialize WebDriver
        self.service = Service(driver_path)
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        if minimize == True:
            self.driver.minimize_window()
        self.search_term = search_term

    def scroll_down(self):
        '''Scrolls down to load all the job listings.'''
        try:
            #waiting for elements to load
            elements = WebDriverWait(self.driver, 10).until(
            wait_for_number_of_elements_to_load(By.XPATH, '//div[@decode-data-ved]'))
            end_reached = False
            count = 1
            while end_reached == False:
                try:
                    element = WebDriverWait(self.driver,10).until(
                        EC.presence_of_element_located((By.XPATH, '//div[@decode-data-ved][position() = '+str(count)+']'))
                        )
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    count=count+1
                except Exception as e:
                    print(f"Error: {e}. Stopping recursion.")
                    end_reached = True
                    return
        except Exception as e:
            print(f"Error: Not enough listings.")
            return

    def extract_listing_information(self):
        time.sleep(10)
        listings_data = []
        try:
            listings = WebDriverWait(self.driver,10).until(EC.presence_of_all_elements_located((By.XPATH,'//div[@class="pE8vnd avtvi"]')))
            #Iterates through each individual listing
            for listing in listings:
                #grabs the title of each listing
                listing_dict = {
                "listHashing": None,
                "companyTitle": None,
                "jobTitle": None,
                "qualifications": None,
                "responsibilities": None,
                "benefits": None,
                "description": None,
                "dateScraped": None
                }
                listing_dict['dateScraped'] = datetime.now().strftime('%Y-%m-%d')
                listing_title = listing.find_element(By.XPATH,'.//h2[@jsname="SBkjJd"]').get_attribute('textContent')
                listing_company_name = listing.find_element(By.XPATH,'.//div[@class="nJlQNd sMzDkb"]').get_attribute('textContent')
                try:
                    listing_description = listing.find_element(By.XPATH, ".//div[@class='YgLbBe']").get_attribute('textContent')
                    listing_dict["description"] = listing_description
                except Exception as e:
                    print(f"Error: {e}")

                listing_dict["companyTitle"] = listing_company_name
                listing_dict["jobTitle"] = listing_title
                listing_hash = Utility.generate_hash(listing_title,listing_company_name)
                listing_dict["listHashing"] = listing_hash
                #grabs all of the categories of requirements needed for the job
                job_requirements = listing.find_elements(By.XPATH, './/div[@class="JxVj3d"]')
                #there are multiple items within each category of job requirements.
                #for some reason there are 2 sets of requirements, one for those who don't click show me, and the other for those who click show more.
                #so I grabbed the second set which include all of the requirements.
                for i in range(int(len(job_requirements)/2),len(job_requirements)):
                    category_body = job_requirements[i]
                    #gets the title of the category of requirements, for exapmle Qualifications, Responsibilities, Etc.
                    category_title = category_body.find_element(By.XPATH,'.//div[@class="iflMsb"]').get_attribute("textContent")

                    category_details =  " ".join([p.get_attribute('textContent') for p in category_body.find_elements(By.XPATH, './/div[not(@*)]')])
                    
                    if category_title == 'Qualifications':
                        listing_dict["qualifications"] = category_details
                    elif category_title == 'Responsibilities':
                        listing_dict["responsibilities"] = category_details
                    elif category_title == 'Benefits':
                        listing_dict["benefits"] = category_details

                listings_data.append(listing_dict)
        except Exception as e:
            print("No listings found, moving on.")
        return listings_data
            
    def save_listings_to_database(self,listings_data,database_manager,table_name):
        for listing in listings_data:
            database_manager.insert_data(table_name,listing)

    def go_to_job_listings(self, location_setting = None, date_posted_setting = None, job_type_setting = None):
        '''
            This function goes to the job listing, you can pass in arguments for the type of job listing you want.
            The arguments will be used to construct an XPATH to select the options, if None, no setting is selected.

            location_setting type: string
            location_setting possible options: "2 mi", "5 mi", "15 mi", "30 mi", "60 mi", 200 mi", "Anywhere"

            date_posted_setting type: string
            date_posted_setting possible options: "Past day", "Past 3 days", "Past week", "Past month"
            
            job_type_setting type: string
            job_type_setting possible options: "Internship", "Full-time", "Part-time", "Contractor"
        '''
        try:
            # Open google's website
            self.driver.get("https://www.google.com/")
            
            # Search for jobs on Google
            search_bar = WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.ID, "APjFqb")))
            search_bar.send_keys(self.search_term)
            search_bar.send_keys(Keys.ENTER)

            # Click on more jobs after the search
            more_jobs = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'esVihe')]"))
            )
            self.driver.execute_script("arguments[0].click();", more_jobs)

            if location_setting is not None:
                # Click on location and expand the search radius 
                location = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Location']"))
                )
                self.driver.execute_script("arguments[0].click();", location)

                # Wait for any overlay to disappear (replace 'overlayClass' with the actual class of the overlay)
                span_over_lay = WebDriverWait(self.driver, 10).until(
                    EC.invisibility_of_element_located((By.XPATH, "//div[text()='New! Find jobs based on education or experience requirements']"))
                )

                # Then click on the location_setting element
                location_setting_xpath = "//span[text()='"+location_setting+"']"
                location_setting = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, location_setting_xpath))
                )
                self.driver.execute_script("arguments[0].click();", location_setting)

            if date_posted_setting is not None:
                # Click on the date posted
                date_posted = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Date posted']"))
                )
                self.driver.execute_script("arguments[0].click();", date_posted)

                # Then click on the date_posted_setting element
                date_posted_setting_xpath = "//span[text()='"+date_posted_setting+"']"
                date_posted_setting = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, date_posted_setting_xpath))
                )
                self.driver.execute_script("arguments[0].click();", date_posted_setting)

            if job_type_setting is not None:
                #Clicking on the Type tab to open up job type settings
                type = WebDriverWait(self.driver,10).until(
                    EC.element_to_be_clickable((By.XPATH,"//span[text()='Type']"))
                )
                self.driver.execute_script("arguments[0].click();", type)

                #Clicks on the internship setting
                type_setting_xpath = "//span[text()='"+job_type_setting+"']"
                type_setting = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, type_setting_xpath))
                )
                self.driver.execute_script("arguments[0].click();", type_setting)
        except Exception as e:
            print("Couldn't load google, better luck next time")

    def quit_driver(self):
        self.driver.close()
        self.driver.quit()

    def get_url(self):
        return self.driver.current_url
