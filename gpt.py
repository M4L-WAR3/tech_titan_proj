import socket
import threading
import json
import time
import signal
import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import re

HOST = '127.0.0.1'
PORT = 65432

def setup_driver():
    options = uc.ChromeOptions()
    #options.add_argument('--headless')  # Run headless
    #options.add_argument('--window-size=1920,1080')  # Optional: simulate a large screen
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    caps = options.to_capabilities()
    caps['goog:loggingPrefs'] = {'browser': 'ALL'}
    driver = uc.Chrome(options=options, desired_capabilities=caps)
    #driver.set_window_position(-10000, 0)  # Moves it offscreen
    driver.delete_all_cookies()
    return driver

def perform_selenium_task(prompt_msg):
    # You can hardcode your URL here or make it configurable
    url = "https://chatgpt.com"

    driver = setup_driver()
    try:
        driver.get(url)
        time.sleep(2)  # Wait for JS to load

        # Inject JS with prompt_msg embedded
        driver.execute_script(f"""
let r = 0;

function sendMessageAndMonitorResponse(msg) {{
    setTimeout(() => {{
        const paragraphs = document.getElementsByTagName("p");
        const paragraph = paragraphs[paragraphs.length - 2];
        if (paragraph) {{
            paragraph.innerText = msg;
        }} else {{
            console.warn("Paragraph index " + r + " not found.");
        }}

        setTimeout(() => {{
            const sendButton = document.getElementById("composer-submit-button");
            if (sendButton) {{
                sendButton.click();
                r++;
            }} else {{
                console.warn("Send button not found.");
            }}
        }}, 1000);
    }}, 1000);
}}

(function monitorContinuously() {{
    let isStreaming = false;
    setInterval(() => {{
        const streamingElems = document.getElementsByClassName("streaming-animation");
        if (streamingElems.length > 0) {{
            isStreaming = true;
        }} else {{
            if (isStreaming) {{
                isStreaming = false;
                const chatElements = document.getElementsByClassName("markdown prose dark:prose-invert w-full break-words dark");
                if (chatElements.length > 0) {{
                    const latest = chatElements[chatElements.length - 1];
                    console.log("✅ Streaming ended. Latest response element:", latest);
                    console.log("📝 Response text:", latest.innerText || latest.textContent);
                }} else {{
                    console.warn("⚠️ No chat elements found.");
                }}
            }}
        }}
    }}, 500);
}})();

sendMessageAndMonitorResponse({json.dumps(prompt_msg)});
        """)

        # Collect console logs that start with '📝 Response text:'
        responses = []
        seen_msgs = set()
        timeout = 120
        start_time = time.time()

        while time.time() - start_time < timeout:
            logs = driver.get_log('browser')
            for entry in logs:
                msg = entry['message']
                if 'console-api' in msg and '📝 Response text:' in msg and msg not in seen_msgs:
                    print("📝 JS Console:", msg)
                    match = re.search(r'"📝 Response text:"\s*"(.+?)"$', msg)
                    if match:
                        response_text = match.group(1)
                        responses.append(response_text)
                    else:
                        responses.append(msg)
                    seen_msgs.add(msg)

                    # ✅ BREAK EARLY once response is captured
                    if responses:
                        return {"responses": responses}

            time.sleep(0.5)

        # If timeout ends and no early return
        return {"responses": responses}

    finally:
        #input("Press Enter to close browser...")
        driver.quit()

def handle_client(conn, addr):
    print(f"Connected by {addr}")
    try:
        data = conn.recv(4096)
        if not data:
            return

        prompt_msg = data.decode('utf-8').strip()
        if not prompt_msg:
            conn.sendall(b'{"error": "Empty prompt"}')
            return

        result = perform_selenium_task(prompt_msg)

        response_json = json.dumps(result)
        conn.sendall(response_json.encode('utf-8'))

    except Exception as e:
        error_msg = json.dumps({"error": str(e)})
        conn.sendall(error_msg.encode('utf-8'))
    finally:
        conn.close()

stop_server = False

def signal_handler(sig, frame):
    print("Signal received, stopping server...")
    exit()
    stop_server = True

signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C

def run_server():
    global stop_server  # Add this line to modify the global variable
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")
        while not stop_server:
            s.settimeout(1.0)  # timeout every 1 second to check stop flag
            try:
                conn, addr = s.accept()
            except socket.timeout:
                continue
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    run_server()