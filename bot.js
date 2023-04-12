import { Telegraf } from 'telegraf';

import { getValue } from './database.js';

export let bot = null;

export async function setupBot(bot) {
    bot.command('start', async ctx => {
        console.log("start command called - CHAT ID: ", ctx.chat.id, " - FROM: ", ctx.from.username, "User ID: ", ctx.from.id);
    });






    // NOTE: THIS NEEDS TO BE LAST!!!
    // TODO: turn this into a modal kind of thing... where the user can enter messages (that will be deleted).. but the context is whatever inline keyboard is currently showing.  Easy to set a global where the bot keeps track of which "mode" it is in.
    // This is a catch-all for any messages that are not commands.
    bot.on('message', ctx => {
        if (mode_callback == null) {
            // bot.telegram.sendMessage(ctx.message.chat.id, "WARNING: I only respond to commands.  Please use /help to see a list of commands.");
            ctx.reply("WARNING: I only respond to commands.  You can always /start again if you need.");
            return;
        }

        mode_callback(ctx);

    })


    //// 'MIDDLEWARE' THAT RESTRICTS WHICH USER THE BOT WILL RESPOND TO ////
    const chatID = await getValue("chat_id");
    if (chatID === null) {
        console.log(">>> WARNING!!!\n>>>\tCHAT_ID not set.  Please set this in the .env file.\n>>>\tThis is the Telegram user ID that will be allowed to use this bot.\n>>>\tYou can find your user ID by sending a message to @userinfobot\n>>>\n");
    } else {
        bot.use((ctx, next) => {
            if (ctx.from.id.toString() === chatID) {
                return next();
            } else {
                console.log(`Unauthorized access attempt by user ID: ${ctx.from.id}`);
                // ctx.reply(`Sorry, you are not authorized to use this bot.`);
            }
        });
        //// SAY HELLO
        // bot.telegram.sendMessage(chatID, `Hello,\nI'm awake and ready to /start`);
    }
}


export async function killBot() {
    return new Promise(async (resolve, reject) => {
        console.log("killing bot...");

        if (bot === null) {
            console.log("bot is null - nevermind...");
            resolve();
            return;
        }

        bot
        try {
            await bot.stop();
        } catch (error) {
            console.error("ERROR: bot.stop() failed:", error);
        }

        const id = await getValue("chat_id")
        bot.telegram.sendMessage(id, `⚠️ *BOT SHUTDOWN\\!* ⚠️`, { parse_mode: 'MarkdownV2' })
            .then(() => {
                console.log("process exiting...");
                resolve();
            })
            .catch((err) => {
                console.error(err);
                reject(err);
            });
    });
};


export async function initBot() {
    console.log("Starting bot...");

    const token = await getValue("telegram_bot_token");
    console.log("bot token:", token);

    if (token == null) {
        console.error("ERROR: Telegram bot token is not set.");
        return;
    }

    const id = await getValue("chat_id");
    console.log("chat id:", id);

    if (id == null) {
        console.error("ERROR: Telegram chat id is not set.");
        return;
    }

    bot = new Telegraf(token);

    bot.launch();
    setupBot(bot);
}
