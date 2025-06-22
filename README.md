```markdown
# Tech Titan Project 🚀

A Python‑based local server application that bundles multiple helper executables (`gpt`, `client`, `hide_window`) and serves an HTML interface via Flask.

---

## 🔧 Features

- **Self‑extracting executable**: Uses a bundled `dependencies.zip` to extract helper tools at runtime.
- **Subprocess management**: Launches `gpt`, `client`, and `hide_window` as separate processes.
- **Local web UI**: Serves `html/index.html` (and assets) via Flask at `http://localhost/`.
- **Cross‑platform packaging**: Designed for PyInstaller bundling into single executable files with runtime extraction.

---

## 📁 Project Structure

```
tech_titan_proj/
├── html/
│   ├── index.html
│   └── ... (CSS/JS/assets)
├── dependencies.zip     # Contains gpt.exe, client.exe, hide_window.exe (for distribution)
├── main.py              # Main controller script
└── README.md
```

---

## 🛠️ Getting Started

### 🧪 Prerequisites

- Python 3.8+
- PyInstaller (if building .exe)

Install dependencies:

```bash
pip install flask undetected-chromedriver beautifulsoup4 pywin32
```

> ⚠️ Windows only: `pywin32` is needed for window-hiding functionality.

---

### 🔧 Development

1. Build the package ZIP (optional if already provided):

   ```python
   # In Python shell or via script
   from main import package_files
   package_files("dependencies.zip")
   ```

2. Run locally for testing:

   ```bash
   python main.py
   ```

3. Open your browser at `http://localhost` to access the web UI.

---

## 📦 Packaging into `.exe`

To bundle everything into a single executable:

```bash
pyinstaller --onefile \
  --add-data "dependencies.zip;." \
  --add-data "html;html" \
  main.py
```

This embeds the ZIP and `html` folder. The `.exe` will extract helpers to a temp folder and launch the UI.

---

## 🧩 How It Works

1. **`main.py`** unpacks `dependencies.zip` (if not already extracted).
2. **Subprocesses** (`gpt.exe`, `client.exe`, `hide_window.exe`) are launched.
3. **Flask** serves the `html` folder on port 80 and opens a browser window.
4. All subprocesses terminate cleanly on exit (Ctrl+C).

---

## 🔧 Troubleshooting

- **Blank page / 404 errors**: Check that the `html` folder is located alongside `main.exe` (or included via PyInstaller).
- **Multiple startup logs**: Ensure `main()` is guarded by `if __name__ == "__main__":` to prevent re-execution when importing modules.
- **Subprocess not found**: Ensure the extracted executables have execute permissions.

---

## 🛠️ Customization Tips

- To **auto-overwrite** existing helper files on every launch, adjust `unpack_files()` to always extract.
- To **cleanup after exit**, add deletion logic for executables in the `except KeyboardInterrupt` block.
- To **update bundled helpers**, simply recreate `dependencies.zip` and rebuild the executable.

---

## 🚀 Future Improvements

- Support platform‑agnostic subprocesses (e.g. `.py` vs `.exe`) automatically.
- Add command‑line flags for debug mode, asset directory, or custom ports.
- Package client UI assets via Flask’s Blueprints or embed them directly.

---

## 🧾 License & Credits

This project is released under the [MIT License](LICENSE). Feel free to reuse and modify as needed.

---

> ✉️ **Need help?** Open an issue or submit a pull request. Happy coding!
```
