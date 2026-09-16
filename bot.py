import os
import asyncio
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")
INVITE_LINK = "https://discord.gg/ctrhRxSKsA"
CHANNEL_NAME = "join-deep-ocean"
TARGET_COUNT = 100

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")


@bot.command()
@commands.has_permissions(administrator=True)
async def reset(ctx, confirm: str):
    if confirm != "CONFIRM":
        await ctx.send("Cancelled. Use `!reset CONFIRM` to proceed.")
        return

    guild = ctx.guild
    await ctx.send("Starting reset. This will take a while due to rate limits...")

    deleted = 0
    for channel in list(guild.channels):
        try:
            await channel.delete(reason="Server reset requested by admin")
            deleted += 1
            await asyncio.sleep(1.5)
        except discord.HTTPException as e:
            print(f"Failed to delete {channel.name}: {e}")
            await asyncio.sleep(5)

    print(f"Deleted {deleted} channels.")

    created = []
    for i in range(1, TARGET_COUNT + 1):
        try:
            ch = await guild.create_text_channel(
                name=f"{CHANNEL_NAME}-{i}",
                reason="Server reset requested by admin",
            )
            created.append(ch)
            await asyncio.sleep(2)
        except discord.HTTPException as e:
            print(f"Failed to create channel {i}: {e}")
            await asyncio.sleep(10)

    for ch in created:
        try:
            await ch.send(f"Join Deep Ocean {INVITE_LINK}")
            await asyncio.sleep(0.8)
            await ch.send(f"Join Deep Ocean {INVITE_LINK}")
            await asyncio.sleep(1.5)
        except discord.HTTPException as e:
            print(f"Failed to send to {ch.name}: {e}")
            await asyncio.sleep(5)

    if created:
        try:
            await created[0].send("✅ Reset complete. Join Deep Ocean.")
        except Exception:
            pass


bot.run(TOKEN)
