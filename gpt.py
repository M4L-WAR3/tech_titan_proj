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

from selenium.webdriver.common.by import By


def get_chrome_window_pid():
    hwnds = []
    def enum_windows(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and 'chrome' in win32gui.GetWindowText(hwnd).lower():
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            hwnds.append((hwnd, pid))
        return True

    win32gui.EnumWindows(enum_windows, None)
    if hwnds:
        print(f"Chrome window hwnds and PIDs: {hwnds}")
        return hwnds[0][1]  # return PID of first visible Chrome window
    else:
        print("No visible Chrome window found.")
        return None
    


HOST = '127.0.0.1'
PORT = 65432
persistent_driver = None
stop_server = False

# Setup and hide Chrome window
def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    caps = options.to_capabilities()
    caps['goog:loggingPrefs'] = {'browser': 'ALL'}
    driver = uc.Chrome(options=options, desired_capabilities=caps)
    driver.delete_all_cookies()
    return driver

def force_hide_chrome_window(pid):
    def hide_window(hwnd, _):
        try:
            _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
            if window_pid == pid and win32gui.IsWindowVisible(hwnd):
                class_name = win32gui.GetClassName(hwnd)
                if class_name == "Chrome_WidgetWin_1":
                    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                    ex_style &= ~win32con.WS_EX_APPWINDOW
                    ex_style |= win32con.WS_EX_TOOLWINDOW
                    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)
                    win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
                    win32gui.EnableWindow(hwnd, False)
        except Exception:
            pass
        return True

    def monitor():
        while True:
            win32gui.EnumWindows(hide_window, None)
            time.sleep(0.2)

    threading.Thread(target=monitor, daemon=True).start()

def get_all_chrome_pids():
    pids = set()
    def enum_windows(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and 'chrome' in win32gui.GetWindowText(hwnd).lower():
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            pids.add(pid)
        return True
    win32gui.EnumWindows(enum_windows, None)
    return pids

def get_or_create_driver():
    global persistent_driver

    # Get PIDs before launching driver
    pids_before = get_all_chrome_pids()
    print("[Chrome PIDs before driver start]", pids_before)

    if persistent_driver is None:
        persistent_driver = setup_driver()
        persistent_driver.get("https://chatgpt.com")
        time.sleep(2)

        # Get PIDs after launching driver
        pids_after = get_all_chrome_pids()
        print("[Chrome PIDs after driver start]", pids_after)

        # Find new PID(s) by set difference
        new_pids = pids_after - pids_before
        if new_pids:
            chrome_pid_real = new_pids.pop()
            print("[New Chrome PID]", chrome_pid_real)
        else:
            chrome_pid_real = persistent_driver.service.process.pid  # fallback
            print("[Fallback Chrome PID]", chrome_pid_real)

        # Send the new Chrome window PID to the hide window server
        try:
            s = socket.socket()
            s.connect(('127.0.0.1', 65433))
            s.sendall(struct.pack('I', chrome_pid_real))
            s.close()
        except Exception as e:
            print(f"Error sending PID to hide_window.py: {e}")

        persistent_driver.save_screenshot("before_prompt.png")

    return persistent_driver


def perform_selenium_task(prompt_msg):
    driver = get_or_create_driver()

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
                    console.log("📝 Response text:", latest.innerHTML);
                }} else {{
                    console.warn("⚠️ No chat elements found.");
                }}
            }}
        }}
    }}, 500);
}})();

sendMessageAndMonitorResponse({json.dumps(prompt_msg)});
    """)

    time.sleep(2)
    driver.save_screenshot("after_prompt.png")

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
                match = re.search(r'"📝 Response text:"\\s*"(.+?)"$', msg)
                if match:
                    response_text = match.group(1)
                    responses.append(response_text)
                else:
                    responses.append(msg)
                seen_msgs.add(msg)
                if responses:
                    return {"responses": responses}

        time.sleep(0.5)

    return {"responses": responses}

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

def signal_handler(sig, frame):
    global stop_server
    print("Signal received, stopping server...")
    stop_server = True

signal.signal(signal.SIGINT, signal_handler)

def run_server():
    global stop_server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")
        while not stop_server:
            s.settimeout(1.0)
            try:
                conn, addr = s.accept()
            except socket.timeout:
                continue
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    run_server()