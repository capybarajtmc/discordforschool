import asyncio
import threading
from flask import Flask, render_template, request, redirect, url_for, flash
import discord

intents = discord.Intents.all()
client = discord.Client(intents=intents)

DISCORD_USER_TOKEN = "discordtoken"

app = Flask(__name__)
app.secret_key = "replace_with_a_secure_random_key"

def run_client():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(client.start(DISCORD_USER_TOKEN))

client_thread = threading.Thread(target=run_client, daemon=True)
client_thread.start()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/send", methods=["POST"])
def send():
    channel_id = request.form.get("channel_id", "").strip()
    message = request.form.get("message", "").strip()

    if not channel_id or not message:
        flash("Channel ID and message are required.", "error")
        return redirect(url_for("index"))

    try:
        cid_int = int(channel_id)
    except ValueError:
        flash("Channel ID must be a number.", "error")
        return redirect(url_for("index"))

    async def _send():
        channel = await client.fetch_channel(cid_int)
        await channel.send(message)

    try:
        asyncio.run_coroutine_threadsafe(_send(), client.loop)
        flash("Message sent.", "success")
    except Exception as e:
        flash(f"Failed to send: {e}", "error")

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
