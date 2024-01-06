import Scraper
import DatabaseManager
import Utility
import time
from plyer import notification
import MachineLearningModel
import os

def main():

    current_directory = os.path.dirname(__file__)
    parent_directory = os.path.dirname(current_directory)
    notificationlog_path = os.path.join(parent_directory,'notificationlog.txt')
    chromedriver_path = os.path.join(parent_directory,'chromedriver-win64','chromedriver.exe')
    database_path = os.path.join(parent_directory,'DataBase','google_database.db')
    brave_browser_path = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
    chrome_browser_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"


    scraper = Scraper.GoogleJobScraper()
    database_manager = DatabaseManager.GoogleDatabaseManager()
    
    sql_table_name = 'recent_job_listings'
    search_terms = [
        "software development jobs",
        "data science jobs",
        "information technology jobs",
        "cybersecurity jobs"
    ]
    for i in range(len(search_terms)):
        # Establish a connection to the database
        database_manager.connect(database_path)
        database_manager.create_table(
            f"""CREATE TABLE IF NOT EXISTS {sql_table_name}
            (JobID INTEGER PRIMARY KEY,
            ListHashing varchar(64) UNIQUE,
            CompanyTitle varchar(255),
            JobTitle varchar(255),
            Qualifications varchar(5000),
            Responsibilities varchar(5000),
            Benefits varchar(5000),
            Description TEXT,
            DateScraped DATE);""")
        # Starts the web browser to begin the scraping process
        scraper.start_driver(driver_path = chromedriver_path,browser_path = chrome_browser_path,search_term = search_terms[i],minimize = True)
        scraper.go_to_job_listings(location_setting = '30 mi', date_posted_setting = 'Past 3 days', job_type_setting = 'Internship')
        scraper.scroll_down()
        # Listing data is a list of dictionarys. Each dictionary has a listing in it.
        listings_data = scraper.extract_listing_information()
        # I loop through each dictionary and check to see if it is a new listing, checking to see if it is stored in the database. If there is, push a notification of a new job listing

        for listing in listings_data:
            
            listing_title = listing['jobTitle']
            listing_company_name = listing['companyTitle']
            listing_hash = Utility.generate_hash(listing_title,listing_company_name)
            print(listing_hash, listing_title, listing_company_name)

            if database_manager.check_hash_exists(sql_table_name,listing_hash) == 0:
                print('New job listing found')
                model = MachineLearningModel.TextClassification()
                print(listing_title)
                print()
                url = scraper.get_url()
                predicton = model.predict_category(text=listing_title)
                notification_message = "JobTitle: "+listing_title+"\nCompanyTitle: "+listing_company_name+"\nJobType: "+predicton
                # Send a notification
                notification.notify(
                    title='New Job Alert!',
                    message=notification_message,
                    timeout=10  # Duration in seconds
                )
                file = open(notificationlog_path,"a")
                file.write(notification_message+"\nLink: "+url+"\n\n")
                file.close()



        scraper.save_listings_to_database(listings_data,database_manager,sql_table_name)
        scraper.quit_driver()
        database_manager.remove_old_listings(sql_table_name, 30)
        database_manager.close()
        print("\n\n\n\n\n")

main()