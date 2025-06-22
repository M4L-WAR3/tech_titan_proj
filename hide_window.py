import socket
import struct
import win32gui
import win32process
import win32con
import time
import sys
import threading

HOST = '127.0.0.1'
PORT = 65433

def maximize_chrome_window(pid):
    def enum_and_maximize(hwnd, _):
        try:
            _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
            if window_pid == pid and win32gui.IsWindowVisible(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        except Exception as e:
            print(f"Maximize error: {e}")
        return True

    win32gui.EnumWindows(enum_and_maximize, None)

def continuously_minimize_chrome_window(pid, interval=0.5):
    def minimizer_loop():
        while True:
            try:
                def enum_and_minimize(hwnd, _):
                    try:
                        _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                        if window_pid == pid and win32gui.IsWindowVisible(hwnd):
                            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                    except Exception:
                        pass
                    return True

                win32gui.EnumWindows(enum_and_minimize, None)
                time.sleep(interval)
            except Exception as e:
                print(f"Error in minimizer thread: {e}")
                break

    thread = threading.Thread(target=minimizer_loop, daemon=True)
    thread.start()


def print_windows_for_pid(pid):
    hwnds = []

    def enum_windows_callback(hwnd, _):
        try:
            _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
            if window_pid == pid:
                title = win32gui.GetWindowText(hwnd)
                visible = win32gui.IsWindowVisible(hwnd)
                print(f"hwnd={hwnd} title='{title}' visible={visible}")
                hwnds.append(hwnd)
        except Exception as e:
            print(f"Error in callback: {e}")
        return True

    win32gui.EnumWindows(enum_windows_callback, None)
    return hwnds

def hide_windows_by_pid(pid, timeout=5):
    start_time = time.time()
    hwnds = []

    while time.time() - start_time < timeout:
        hwnds = print_windows_for_pid(pid)
        visible_hwnds = [hwnd for hwnd in hwnds if win32gui.IsWindowVisible(hwnd)]
        if visible_hwnds:
            break
        time.sleep(0.5)

    if visible_hwnds:
        for hwnd in visible_hwnds:
            maximize_chrome_window(pid)  # Maximize once
            continuously_minimize_chrome_window(pid)  # Keep minimizing forever
            #win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            #win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            #smooth_hide_chrome_window(pid)
            # Move off-screen instead of hiding
            #win32gui.MoveWindow(hwnd, -2000, -2000, 800, 600, True)
            #win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
            print(f"Hidden window hwnd={hwnd} for PID={pid}")
    else:
        print(f"No visible window found for PID {pid} after {timeout} seconds.")

def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")

        try:
            while True:
                conn, addr = s.accept()
                with conn:
                    print('Connected by', addr)
                    while True:
                        data = conn.recv(4)
                        if not data:
                            break
                        pid = struct.unpack('I', data)[0]
                        print(f"Received PID: {pid}")
                        hide_windows_by_pid(pid)
        except KeyboardInterrupt:
            print("\nServer shutting down gracefully.")
            sys.exit(0)

if __name__ == "__main__":
    run_server()

