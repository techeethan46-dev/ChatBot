# Connected Discord-GitHub | Discord: Ethan | Roblox: EthanDev

import discord
from discord.ext import commands
from discord import app_commands
import os
import google.generativeai as genai

# init gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())
bot.intents.message_content = True

history = {}

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("bot is online")

@bot.event
async def on_message(msg):
    if msg.author.bot: 
        return

    pinged = bot.user in msg.mentions
    
    is_reply = False
    if msg.reference and msg.reference.resolved:
        if msg.reference.resolved.author == bot.user:
            is_reply = True

    if pinged or is_reply:
        txt = msg.content.replace(f"<@{bot.user.id}>", "").strip()
        
        if not txt:
            await msg.reply("what's up?")
            return

        uid = msg.author.id
        if uid not in history:
            history[uid] = []
            
        history[uid].append(f"User: {txt}")
        
        # trim to last 6 msgs
        history[uid] = history[uid][-6:]

        prompt = "\n".join(history[uid]) + "\nBot:"

        async with msg.channel.typing():
            try:
                # using async so we dont block the gateway heartbeat
                res = await model.generate_content_async(prompt)
                ans = res.text
                
                history[uid].append(f"Bot: {ans}")
                
                if len(ans) > 2000:
                    ans = ans[:1996] + "..."
                    
                await msg.reply(ans)
                
            except Exception as e:
                print(e)
                await msg.reply("error generating response")
                # history[uid].pop() # remove failed prompt from memory

    await bot.process_commands(msg)


@bot.tree.command(name="clear", description="clears your ai chat history")
async def clear_cmd(interaction: discord.Interaction):
    uid = interaction.user.id
    if uid in history:
        del history[uid]
        await interaction.response.send_message("memory cleared.", ephemeral=True)
    else:
        await interaction.response.send_message("nothing to clear.", ephemeral=True)


# will crash if token isnt set, which is fine
bot.run(os.environ.get("BOT_TOKEN"))

