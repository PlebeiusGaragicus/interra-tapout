import platform
import os
import time
import re

import dotenv

from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# NOTE:
# need to add these to your .env file
#CREW_USER=""
#CREW_PASS=""




def login(driver: webdriver.Chrome):

    wait = WebDriverWait(driver, 10)

    username = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#username")))
    username = driver.find_element(By.CSS_SELECTOR, "#username")
    username.send_keys( os.getenv("CREW_USER") )

    password = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#password")))
    password = driver.find_element(By.CSS_SELECTOR, "#password")
    password.send_keys( os.getenv("CREW_PASS") )

    button = driver.find_element(By.CSS_SELECTOR, "button.btn-success")
    button.click()



def get_assignments(driver: webdriver.Chrome):

    # Wait for the elements to be present
    # wait = WebDriverWait(driver, 10)
    # assignments = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.assignment")))
    # wait = WebDriverWait(driver, 10)
    # assignments = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div.assignment")))

    assignments = driver.find_elements(By.CSS_SELECTOR, "div.assignment")
    num_assignments = len(assignments)

    # go to the next day
    next_day = driver.find_element(By.CSS_SELECTOR, "i.fa.fa-fw.icon-arrow-right")
    next_day.click()

    time.sleep(10)

    # wait for the number of assignments to change
    # we NEED this because otherwise we will have an empty list of assignments
    # these load dynamically after page loads, apparently
    wait = WebDriverWait(driver, 10)
    wait.until(lambda driver: len(driver.find_elements(By.CSS_SELECTOR, "div.assignment")) > num_assignments)

    shift = driver.find_element(By.CSS_SELECTOR, "span.label.day-color").text

    # this is what we are after
    das_units = []

    # this is the unit - Engine 3, Truck 3, etc.
    assignments = driver.find_elements(By.CSS_SELECTOR, "div.assignment")
    for assignment in assignments:
        # unit = assignment.find_element(By.CSS_SELECTOR, "h3")
        unit = assignment.find_element(By.CSS_SELECTOR, "h3:not([class])")
        unit = unit.text.strip().split('\n')[0]

        # too much text gets pulled in, so we need to extract the up and and including the number.
        result = re.search("^.*?\d+", unit)

        if result is None:
            continue

        res = result.group()

        # skip these...
        if res in ["Batt Chief 5", "Callback Trades", "Mobile Command 9", "Water Tender 13", "Water Tender 16"]:
            continue
        # these are all cross-staffed
        if "Rehab" in res:
            continue
        # the rest of the list starting with this unit is not needed.. these are cross-staffed, etc.
        if res == "FireBoat Reserve 1":
            break

        # this is a row of ONE person.  The naming makes no sense
        each_person = assignment.find_elements(By.CSS_SELECTOR, "tr.shift")

        people = []
        for p in each_person:

            name = p.find_element(By.CSS_SELECTOR, "h4").text.split("\n")[0]

            # <td class="time-period listview" width="25%">08:00 - 08:00</td>
            hours = p.find_element(By.CSS_SELECTOR, "td.time-period.listview").text

            if name == "RUN SHORT":
                continue

            people.append([
                name,
                hours
            ])

        das_units.append([
            res,
            people
        ])


    # SORT the list by the number in the unit name (this way Truck 3 is before Engine 3)
    def extract_number(word):
        match = re.search(r'\d+', word[0])
        return int(match.group(0))
    das_units = sorted(das_units, key=extract_number)

    date = driver.find_element(By.CSS_SELECTOR, "span.friendly-date").text

    #re that gets rid of the first word, command and space
    date = re.sub(r'^\w+,\s', '', date)

    with open(f"{shift} {date}.txt", "w") as f:
        for line in das_units:
            f.write(str(line) + "\n")

def main():

    options = Options()
    # options.add_argument("--headless")

    if platform.system() == 'Darwin':
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    elif platform.system() == 'Linux':
        driver = webdriver.Chrome(options=options)
    else:
        raise Exception("Unsupported OS")


    driver.get("https://www.crewsense.com/Application/Login/")

    login(driver)

    try:
        get_assignments(driver)
    except TimeoutException:
        print("TimeoutException")
        exit(1)

    driver.quit()


if __name__ == '__main__':
    dotenv.load_dotenv()

    # TODO setup logging

    main()
