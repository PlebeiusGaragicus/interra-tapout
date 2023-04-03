import puppeteer from 'puppeteer';
import cheerio from 'cheerio';
import twilio from 'twilio';
import dotenv from 'dotenv';

dotenv.config({ path: '../.env' });

const config = {
    UNIT: process.env.UNIT,
    UNIT_PHONETIC: process.env.UNIT_PHONETIC,
    INTTERRA_USERNAME: process.env.INTTERRA_USERNAME,
    INTTERRA_PASSWORD: process.env.INTTERRA_PASSWORD,
    TWILIO_SID: process.env.TWILIO_SID,
    TWILIO_TOKEN: process.env.TWILIO_TOKEN,
    TWILIO_PHONENUMBER_TO: process.env.TWILIO_PHONENUMBER_TO,
    TWILIO_PHONENUMBER_FROM: process.env.TWILIO_PHONENUMBER_FROM,
};

const client = twilio(config.TWILIO_SID, config.TWILIO_TOKEN);

function sendSMS(msg) {
    client.messages.create({
        to: config.TWILIO_PHONENUMBER_TO,
        from: config.TWILIO_PHONENUMBER_FROM,
        body: msg,
    });
}

function phoneticAddress(address) {
    address = address.replace("NW ", "northwest ");
    address = address.replace("NE ", "northeast ");
    address = address.replace("SW ", "southwest ");
    address = address.replace("SE ", "southeast ");
    address = address.replace("N ", "north ");
    address = address.replace("S ", "south ");

    address = address.replace(" AVE", " avenue");
    address = address.replace(" ST", "street ");
    address = address.replace(" RD", "road ");
    address = address.replace(" PKWY", "parkway ");
    address = address.replace(" BLVD", " boulevard");
    address = address.replace(" CT", " court");

    return address;
}

function speak(call, address, latlon) {
    console.log(`CALL: ${call} at ${address}`);
    // Replace this line with the appropriate text-to-speech library or API call for your system
    console.log(`say ${config.UNIT_PHONETIC} has a ${call} at ${phoneticAddress(address)}`);
    sendSMS(`${call}\n${address}\nhttps://www.google.com/maps/place/${latlon}`);
}



async function openPage() {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    await page.goto('https://apps.intterragroup.com');
    // TODO
    // https://stackoverflow.com/a/39914235
    await page.waitForTimeout(2000);

    return { browser, page };
}


async function login(page) {
    console.log("Logging in to Intterra...")
    await page.type('[name="username"]', config.INTTERRA_USERNAME);
    await page.type('[name="password"]', config.INTTERRA_PASSWORD);
    // await page.click('//button');
    await page.click('button.primary');
    await page.waitForTimeout(5000);
    console.log("Survived 5 second login timeout")
}


async function alertLoop(page) {
    let lastCall = null;
    let allCalls = null;

    while (true) {
        const html = await page.content();
        const $ = cheerio.load(html);

        const calls = [];

        const rows = $('section.table-row-section');

        if (rows.length === 0) {
            await page.reload();
        }

        rows.each((_, row) => {
            try {
                const call = $(row).find('h3.can-notify-highlight').text().trim();
                const unitsAddr = $(row).find('label.description').text().trim();

                const [_unit, addr] = unitsAddr.split('●').slice(1).map(s => s.trim());
                const units = _unit.split(' ');

                if (units.includes(config.UNIT)) {
                    if (!lastCall || (call !== lastCall[0] || addr !== lastCall[1])) {
                        console.log(`NEW CALL!!!! ${config.UNIT} - ${call} - ${addr}`);

                        // Add any additional logic for clicking elements, refreshing the page, etc.

                        const latlon = 'LAT,LON'; // Replace this line with the appropriate logic to extract the latitude and longitude
                        speak(call, addr, latlon);
                        lastCall = [call, addr];
                    }
                }

                calls.push([call, addr, units]);
            } catch (e) {
                console.error('PARSING ERROR - EXCEPTION HANDLED', e);
                page.reload();
                sleep(2000);
            }
        });

        if (!arraysEqual(allCalls, calls)) {
            allCalls = calls;
            console.log('\n\n\n\n');
            calls.forEach((call) => {
                console.log(call);
            });
        }

        await new Promise((resolve) => setTimeout(resolve, 1000));
    }
}

// https://stackoverflow.com/a/14853974
// CoPilot
function arraysEqual(a, b) {
    if (a === b) return true;
    if (a == null || b == null) return false;
    if (a.length !== b.length) return false;

    for (let i = 0; i < a.length; ++i) {
        if (a[i] !== b[i]) return false;
    }
    return true;
}

// chatGPT-4
// function arraysEqual(a, b) {
//     if (a.length !== b.length) return false;

//     for (let i = 0; i < a.length; i++) {
//         if (Array.isArray(a[i]) && Array.isArray(b[i])) {
//             if (!arraysEqual(a[i], b[i])) return false;
//         } else if (a[i] !== b[i]) {
//             return false;
//         }
//     }

//     return true;
// }


(async () => {
    console.log("Starting Intterra Alert Listener")
    const { browser, page } = await openPage();
    await login(page);
    try {
        await alertLoop(page);
    } catch (e) {
        console.error(e);
        await browser.close();
    }
})();
