import subprocess
import webbrowser
import signal
import sys
from flask import Flask
import threading
import time
import socket
import threading
import json
import time
import signal
import re
import undetected_chromedriver as uc
import win32gui
import win32process
import win32con
import threading
import struct;
import socket
import struct
import win32gui
import win32process
import win32con
import time
import sys
import threading
from flask import Flask, render_template_string, request, jsonify, send_from_directory, abort
import socket
import os
import html
import json
import re
from bs4 import BeautifulSoup
import base64
import zipfile
import os

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller .exe"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)

def unpack_files(zip_path):
    if not os.path.exists(zip_path):
        print(f"Error: {zip_path} not found.")
        sys.exit(1)
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        for file_name in zipf.namelist():
            if os.path.exists(file_name):
                print(f"Skipping '{file_name}': already exists.")
            else:
                zipf.extract(file_name)
                print(f"Extracted '{file_name}'")

processes = []

# Folder containing index.html and other assets
SERVE_FOLDER = os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), "html")
#SERVE_FOLDER = "html"

def run_flask():
    app = Flask(__name__)

    @app.route("/")
    def serve_index():
        return send_from_directory(SERVE_FOLDER, "index.html")

    @app.route('/<path:filename>')
    def serve_file(filename):
        safe_path = os.path.join(SERVE_FOLDER, filename)
        if os.path.commonpath([os.path.abspath(safe_path), os.path.abspath(SERVE_FOLDER)]) != os.path.abspath(SERVE_FOLDER):
            abort(404)
        if os.path.exists(safe_path):
            return send_from_directory(SERVE_FOLDER, filename)
        else:
            abort(404)

    app.run(host="0.0.0.0", port=80)

def start_process(script_name):
    if script_name.endswith(".exe"):
        return subprocess.Popen([script_name])
    else:
        return subprocess.Popen([sys.executable, script_name])

def main():
    global processes

    unpack_files(get_resource_path("dependencies.zip"))

    if not os.path.isdir(SERVE_FOLDER):
        print(f"Error: folder '{SERVE_FOLDER}' does not exist.")
        sys.exit(1)
    if not os.path.isfile(os.path.join(SERVE_FOLDER, "index.html")):
        print(f"Error: '{SERVE_FOLDER}/index.html' not found.")
        sys.exit(1)

    processes.append(start_process("gpt.exe"))
    processes.append(start_process("hide_window.exe"))
    processes.append(start_process("client.exe"))

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    time.sleep(1)
    webbrowser.open("http://localhost")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping processes...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.wait()
        print("All processes stopped. Exiting.")

if __name__ == "__main__":
    main()