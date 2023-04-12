import os
import platform
from time import sleep
import logging
import dotenv
import bs4
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class Config:
    UNIT = None
    UNIT_PHONETIC = None
    INTTERRA_USERNAME = None
    INTTERRA_PASSWORD = None

    TWILIO_SID = None
    TWILIO_TOKEN = None
    TWILIO_PHONENUMBER_TO = None
    TWILIO_PHONENUMBER_FROM = None

this_config = Config()

def sendSMS(msg):
    from twilio.rest import Client
    client = Client(this_config.TWILIO_SID, this_config.TWILIO_TOKEN)
    message = client.messages.create(
        to=this_config.TWILIO_PHONENUMBER_TO, 
        from_=this_config.TWILIO_PHONENUMBER_FROM,
        body=msg)


def phonetic_address(address: str) -> str:
    address = address.replace("NW ", "northwest ")
    address = address.replace("NE ", "northeast ")
    address = address.replace("SW ", "southwest ")
    address = address.replace("SE ", "southeast ")
    address = address.replace("N ", "north ")
    address = address.replace("S ", "south ")

    address = address.replace(" AVE", " avenue")
    address = address.replace(" ST", "street ")
    address = address.replace(" RD", "road ")
    address = address.replace(" PKWY", "parkway ")
    address = address.replace(" BLVD", " boulevard")
    address = address.replace(" CT", " court")

    return address


def speak(call, address, latlon):
    """
        Truck goes woop woop
    """

    logging.info(f"CALL: {call} at {address}")
    os.popen(f"say {this_config.UNIT_PHONETIC} has a {call} at {phonetic_address(address)}")
    sendSMS(f"{call}\n{address}\nhttps://www.google.com/maps/place/{latlon}")


def open_page():
    options = Options()
    options.add_argument("--headless")

    if platform.system() == 'Darwin':
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    elif platform.system() == 'Linux':
        driver = webdriver.Chrome( options=options)
    else:
        exit(1)

    URL = 'https://apps.intterragroup.com'
    driver.get( URL )
    sleep(2)

    return driver


def login(driver: webdriver.Chrome):
    username = driver.find_element(by=By.NAME, value="username")
    username.send_keys(this_config.INTTERRA_USERNAME)

    password = driver.find_element(by=By.NAME, value="password")
    password.send_keys(this_config.INTTERRA_PASSWORD)

    driver.find_element(by=By.XPATH, value='//button').click()
    driver.refresh()
    sleep(5)


def alert_loop(driver: webdriver.Chrome):
    last_call = None
    all_calls = None

    while True:
        html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
        soup = bs4.BeautifulSoup(html, 'lxml')

        calls = []

        rows = soup.find_all(name="section", attrs={"class": "table-row-section"})

        if rows == []:
            # this catches a 'failure to load' error when the sidebar sitrep mon doesn't appear
            driver.refresh()

        for tr in rows:
            try:
                div = tr.find(name="div", attrs={"class": "content"})
                call = div.find(name="h3", attrs={"class": "can-notify-highlight"}).text
                units_addr = div.find(name="label", attrs={"class": "description"}).text

                _unit = units_addr.split('●')[1].strip()
                units = []
                for u in _unit.split(' '):
                    units.append(u)

                addr = units_addr.split('●')[2].strip()
                addr = addr.split('[')[0]

                if this_config.UNIT in units:
                    if last_call != (call, addr):
                        logging.info(f"NEW CALL!!!! {this_config.UNIT} - {call} - {addr}")

                        for i in driver.find_elements(by=By.TAG_NAME, value='span'):
                            if i.text.strip() == this_config.UNIT:
                                try:
                                    i.click()
                                except selenium.common.exceptions.ElementClickInterceptedException:
                                        pass
                                break

                        latlon = None
                        for i in driver.find_elements(by=By.TAG_NAME, value='label'):
                            a = i.get_attribute('data-bind')
                            if "text: latitude() + ', ' + longitude(), highlightOnChange: 10000" == a:
                                print(i.text)
                                latlon = i.text.replace(' ', '')
                        driver.refresh()

                        speak(call, addr, latlon)
                        last_call = (call, addr)

                calls.append((call, addr, units))

            except (AttributeError, IndexError) as e:
                logging.error(f"PARSING ERROR - EXCEPTION HANDLED", exc_info=True)
                driver.refresh()
                sleep(2)

        if all_calls != calls:
            all_calls = calls
            print("\n\n\n\n")
            for c in calls:
                print(c)

        sleep(1)


def main():
    log_format="[%(levelname)s] (%(filename)s @ %(lineno)d) %(message)s"
    logginglevel = logging.INFO
    logging.basicConfig(
        level=logginglevel,
        format=log_format,
        handlers=[logging.StreamHandler(),
                  logging.FileHandler('debug.log', mode='w')])


    logging.info(f"STARTING...")

    logging.getLogger('WDM').setLevel(logging.ERROR)

    driver = open_page()

    login(driver)

    try:
        alert_loop(driver)
    except KeyboardInterrupt:
        print("GOOD BYE!!!!!!!!!!")
        driver.quit()
        exit(0)

if __name__ == "__main__":
    dotenv.load_dotenv()

    this_config.UNIT = os.getenv("UNIT")
    this_config.UNIT_PHONETIC = os.getenv("UNIT_PHONETIC")
    this_config.INTTERRA_USERNAME = os.getenv("INTTERRA_USERNAME")
    this_config.INTTERRA_PASSWORD = os.getenv("INTTERRA_PASSWORD")

    this_config.TWILIO_SID = os.getenv("TWILIO_SID")
    this_config.TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
    this_config.TWILIO_PHONENUMBER_TO = os.getenv("TWILIO_PHONENUMBER_TO")
    this_config.TWILIO_PHONENUMBER_FROM = os.getenv("TWILIO_PHONENUMBER_FROM")

    main()
