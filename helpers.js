
import config from './config.js';

import { db, closeMongoDBConnection, connectToMongoDB } from "./database.js";
import { initBot, killBot } from './bot.js';
import { killIntterra, runIntterra } from './intterra.js';


export async function closeApp() {
    console.log("Closing app...");
    try {
        await killBot();
        await closeMongoDBConnection();
        await killIntterra();
        console.log("Closed app successfully");
        process.exit(0);
    } catch (error) {
        console.error("Error closing app: ", error);
        process.exit(1);
    }
}
