# ----------------------------------------------------------------------------
#                            => CREDITS <=
# ----------------------------------------------------------------------------
#                 HACK: Developed and maintained by VXNET
#                        ✦ Do not copy code. ✦
#               ✦ Discord: https://discord.gg/HmGHGww2kY ✦
#                      Web: http://lefeu.nvnet.pl
# ----------------------------------------------------------------------------

from flask import Flask, render_template, request, jsonify
import logging

import asyncio
import threading
import hashlib
import os

from .async_websocket import discord_auto_responder
from .utils import read_config, write_config
from .current_state import State_AutoResponder, State_Flask

app = Flask(__name__)

@app.after_request
def add_header(response):
    """
    Add headers to forcefully disable caching.
    """
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# Stop flag for the background task
stop_flag = threading.Event()



@app.route("/")
def home():
    return render_template('index.html')

@app.route("/status")
def status():
    return render_template("status.html")

@app.route("/configuration")
def configuration():
    return render_template("configuration.html")

@app.route("/get-config")
def get_config():
    return jsonify(read_config())

@app.route("/save-config", methods=['POST'])
def save_config():
    try:
        data = request.json
        write_config(data)
        return jsonify({"status": "success", "message": "Configuration updated!"})
    except Exception as e:
        print("Error:", e)
        return jsonify({"status": "error", "message": f"Failed to update configuration! {e}"}), 500


@app.route("/start-auto-responder-thread")
def start_responder_thread():
    if not hasattr(State_AutoResponder, "thread") or State_AutoResponder.thread is None or not State_AutoResponder.thread.is_alive():
        State_AutoResponder.status = "PENDING"

        # Run the task in a background thread
        def start_task():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def run_discord_auto_responder():
                State_AutoResponder.status = "STARTED"
                # while not stop_flag.is_set():  # Check if the task should stop
                await discord_auto_responder()  # Ensure discord_auto_responder() is async
                #     await asyncio.sleep(5)  # Optional sleep to prevent tight looping
                # State_AutoResponder.status = "COMPLETED"

            loop.run_until_complete(run_discord_auto_responder())

        # Start the task in a separate thread
        task_thread = threading.Thread(target=start_task, daemon=True)
        State_AutoResponder.thread = task_thread
        task_thread.start()

        return jsonify({"status": "STARTED"})
    else:
        return jsonify({"status": "ALREADY RUNNING"})


@app.route("/api")
def api():
    return jsonify(
        {
            "status": "OPERATING NORMALLY",
            "message": f"Welcome {os.getlogin()}"
        }
    )

@app.route("/api/services-status")
def services_status():
    return jsonify(
        {
            "status-flask": State_Flask.status,
            "status-discord-auto-responder": State_AutoResponder.status
        }
    )


# DEVELOPMENT HELPERS:

# @app.route("/rootpath")
# def rootpath():
#     return f"root path: {app.root_path}"


def run_flask_server():
    log = logging.getLogger('werkzeug')
    log.disabled = True
    app.run( host="0.0.0.0", port=read_config()['SERVER']['port'], debug=False, use_reloader=False, threaded=True )