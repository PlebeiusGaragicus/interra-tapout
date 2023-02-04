# interra-tapout
Truck goes whoop whoop, engine goes beep beep.  That's basically it.

# download and setup

```sh
# get the code
git clone https://github.com/PlebeiusGaragicus/interra-tapout.git
cd IntterraWebScraper

# setup python virtual environment, install dependencies
python3 -m venv venv/
source venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt

chmod +x run
```

# create config.py

Run this multi-line command to create your config.py

```sh
cat > config.py << EOF
UNIT = ""
UNIT_PHONETIC = ""
INTTERRA_USERNAME = ""
INTTERRA_PASSWORD = ""
TWILIO_SID = ""
TWILIO_TOKEN = ""
TWILIO_PHONENUMBER_TO = ""
TWILIO_PHONENUMBER_FROM = ""
EOF
```

Next, edit config.py to include your username and password, etc...

# run

```sh
# activate the virtual environment
source venv/bin/activate

# run the script
python3 tapout.py
```

# Further research...

```
https://apps.intterragroup.com/#/FirstDue/SitstatSitStatMonitor/45.525/-122.6989/14

https://apps.intterragroup.com/#/FirstDue/<APP>/<LATTITUDE>/<LONGITUDE>/<ZOOM LEVEL>
```

- https://dc.intterragroup.com/docs/

