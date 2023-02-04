import platform
import os
import re

import pprint

import dotenv

from selenium import webdriver

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
    # button = driver.find_element_by_css_selector("button.btn-success")
    # button = driver.find_element_by_css_selector("button.btn-lg.btn-success.btn-block.btn-default[type='submit']")
    # button = driver.find_element_by_xpath("//button[@type='submit' and contains(., 'Sign in')]")

    button.click()



def get_assignments(driver: webdriver.Chrome):

    # Wait for the elements to be present
    # wait = WebDriverWait(driver, 10)
    # assignments = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.assignment")))
    # wait = WebDriverWait(driver, 10)
    # assignments = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div.assignment")))

    # print("Assignments: " + str(len(assignments)))


    # for assignment in assignments:
    #     unit = assignment.find_element(By.CSS_SELECTOR, "h3")
    #     print(unit.text)
    #     print(1)

    assignments = driver.find_elements(By.CSS_SELECTOR, "div.assignment")
    num_assignments = len(assignments)

    wait = WebDriverWait(driver, 10)
    wait.until(lambda driver: len(driver.find_elements(By.CSS_SELECTOR, "div.assignment")) > num_assignments)

    das_units = []

    assignments = driver.find_elements(By.CSS_SELECTOR, "div.assignment")
    for assignment in assignments:
        # unit = assignment.find_element(By.CSS_SELECTOR, "h3")
        unit = assignment.find_element(By.CSS_SELECTOR, "h3:not([class])")
        unit = unit.text.strip().split('\n')[0]
        # unit = unit.text.strip()

        result = re.search("^.*?\d+", unit)

        if result is None:
            continue

        res = result.group()

        # the rest of the list starting with this unit is not needed.. these are cross-staffed, etc.
        if res == "FireBoat Reserve 1":
            break

        # skip these...
        if res in ["Batt Chief 5", "Callback Trades", "Mobile Command 9", "Water Tender 13", "Water Tender 16"]:
            continue

        if "Rehab" in res:
            continue

        # print(res)


        person = assignment.find_elements(By.CSS_SELECTOR, "h4")

        people = []
        for p in person:

            if p.text == "RUN SHORT":
                continue

            # TODO check if there are 4 names... but sometimes people have three names... - this is a trade

            people.append(p.text.split("\n")[0])


        das_units.append([
            res,
            people
        ])
        # das_units.append({
        #     "unit": res,
        #     "people": people
        # })

    print("------")
    pprint.pprint(das_units)

    words = ["a1", "b3", "c1"]

    def extract_number(word):
        match = re.search(r'\d+', word[0])
        return int(match.group(0))

    das_units = sorted(das_units, key=extract_number)
    # das_units = sorted(das_units, key=lambda x: x[0])

    with open("das_units.txt", "w") as f:
        for line in das_units:
            f.write(str(line) + "\n")
        # f.write(str(das_units))

def main():

    options = Options()
    options.add_argument("--headless")

    if platform.system() == 'Darwin':
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    elif platform.system() == 'Linux':
        driver = webdriver.Chrome(options=options)
    else:
        raise Exception("Unsupported OS")


    driver.get("https://www.crewsense.com/Application/Login/")

    login(driver)

    get_assignments(driver)

    driver.quit()


if __name__ == '__main__':
    dotenv.load_dotenv()

    # TODO setup logging

    main()
