from flask import Flask, render_template_string, request, jsonify, send_from_directory
import socket
import os
import html
import json
import re
from bs4 import BeautifulSoup

app = Flask(__name__)

BASE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        textarea { height: 100px; font-size: 1em; }
        pre { background: #f8f9fa; padding: 15px; white-space: pre-wrap; border-radius: 5px; }
    </style>
</head>
<body class="bg-light py-4">
    <div class="container">
        <h1 class="mb-4">{{ title }}</h1>

        {% if show_subject %}
        <div class="mb-3">
            <label for="subject" class="form-label">Choose Subject:</label>
            <select id="subject" class="form-select">
                <option value="physics">Physics</option>
                <option value="chemistry">Chemistry</option>
                <option value="biology">Biology</option>
            </select>
        </div>
        {% endif %}

        <div class="mb-3">
            <textarea id="prompt" class="form-control" placeholder="{{ placeholder }}"></textarea>
        </div>
        <button class="btn btn-primary mb-4" onclick="sendPrompt()">Submit</button>

        <h2>Response:</h2>
        <div id="response" class="border rounded p-3 bg-white mb-4">Waiting for input...</div>

        <h3>Save Chapter</h3>
        <div class="input-group mb-3">
            <input type="text" id="filename" class="form-control" placeholder="Enter file name (without extension)" />
            <button class="btn btn-success" onclick="saveToFile()">Save</button>
        </div>
        <pre id="save-status" class="text-success"></pre>
    </div>

    <script>
        function sendPrompt() {
            const responseLog = document.getElementById('response');
            const prompt = document.getElementById('prompt').value;
            const subject = document.getElementById('subject') ? document.getElementById('subject').value : "";
            let endpoint = window.location.search.includes("quiz") ? "/quiz" :
                        window.location.search.includes("doubt") ? "/doubt" : "/generate";

            // Create container for this prompt+response
            const entryDiv = document.createElement("div");
            entryDiv.style.marginBottom = "20px";
            entryDiv.style.borderBottom = "1px solid #ccc";
            entryDiv.style.paddingBottom = "10px";

            // Add prompt text
            const promptEl = document.createElement("div");
            promptEl.textContent = "Prompt: " + prompt;
            promptEl.style.fontWeight = "bold";
            entryDiv.appendChild(promptEl);

            // Add placeholder for response text
            const responseEl = document.createElement("div");
            responseEl.textContent = "Generating Response. Please Be Patient.";
            entryDiv.appendChild(responseEl);

            // Append this block to the response log
            responseLog.insertBefore(entryDiv, responseLog.firstChild);

            fetch(`${endpoint}?subject=${subject}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt: prompt })
            })
            .then(response => response.json())
            .then(data => {
                responseEl.innerHTML = data.response || data.error || "No response.";
                console.log("📝 Response text:", data.response);
            })
            .catch(err => {
                responseEl.innerHTML = "Error: " + err;
            });
        }


        function saveToFile() {
        const content = document.getElementById('response').innerHTML;
        const subject = document.getElementById('subject') ? document.getElementById('subject').value : "general";
        const filename = document.getElementById('filename').value;

        if (!filename || !content || content === "Waiting for input...") {
            document.getElementById('save-status').innerHTML = "Error: Please enter a filename and generate content first.";
            return;
        }

        fetch("/save", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ subject: subject, filename: filename, content: content })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('save-status').innerHTML = data.message || data.error;
        })
        .catch(err => {
            document.getElementById('save-status').innerHTML = "Error: " + err;
        });
    }
    </script>
</body>
</html>
"""

FILE_LIST_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Saved Files</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light py-4">
    <div class="container">
        <h1>Saved Files</h1>

        {% for subject, file_list in files.items() %}
            <div class="mb-4">
                <h3>{{ subject.title() }}</h3>
                <ul class="list-group">
                    {% for file in file_list %}
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        <a href="/view?subject={{ subject }}&file={{ file }}">{{ file }}</a>
                        <span class="text-danger" style="cursor:pointer;" onclick="deleteFile('{{ subject }}', '{{ file }}')">🗑️</span>
                    </li>
                    {% endfor %}
                </ul>
            </div>
        {% endfor %}
    </div>
    <script>
        function deleteFile(subject, filename) {
            if (!confirm(`Delete ${filename}?`)) return;
            fetch("/delete", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ subject: subject, filename: filename })
            })
            .then(res => res.json())
            .then(data => {
                alert(data.message || data.error);
                location.reload();
            });
        }
    </script>
</body>
</html>
"""

FILE_VIEW_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>View: {{ filename }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body, html {
            margin: 0;
            padding: 0;
            height: 100%;
        }

        #notes-container {
            display: flex;
            height: 100vh;
            overflow: hidden;
        }

        #notes {
            width: 300px;
            min-width: 150px;
            max-width: 50%;
            background: #f8f9fa;
            padding: 20px;
            overflow-y: auto;
            resize: none;
        }

        #resizer {
            width: 10px; /* Wider for easier dragging */
            cursor: ew-resize;
            background: #adb5bd;
        }

        #file-content {
            flex-grow: 1;
            padding: 20px;
            overflow-y: auto;
            background: #fff;
        }

        iframe {
            width: 100%;
            height: 90vh;
            border: none;
        }
    </style>
</head>
<body>
    <div id="notes-container">
        <div id="notes">
            <h4>Notes</h4>
            <textarea id="note-area" class="form-control mb-3" placeholder="Write your notes here..." rows="10"></textarea>
            <input type="text" id="note-filename" class="form-control mb-2" placeholder="Enter note filename (e.g. notes1.txt)" />
            <button class="btn btn-success w-100" onclick="saveNotes()">Save Notes</button>
            <div id="save-status" class="mt-2 text-success small"></div>
        </div>
        <div id="resizer"></div>

        <div id="file-content">
            <h2>{{ filename }}</h2>
            {% if pdf_url %}
                <iframe src="{{ pdf_url }}"></iframe>
            {% else %}
                <div class="bg-white p-3 border rounded">{{ content|safe }}</div>
            {% endif %}
        </div>
    </div>

    <script>
        const resizer = document.getElementById('resizer');
        const notesPanel = document.getElementById('notes');

        let isResizing = false;

        resizer.addEventListener('mousedown', function(e) {
            isResizing = true;
            document.body.style.cursor = 'ew-resize';
            e.preventDefault(); // Prevent text selection
        });

        document.addEventListener('mousemove', function(e) {
            if (!isResizing) return;
            const newWidth = e.clientX;
            if (newWidth > 150 && newWidth < window.innerWidth * 0.5) {
                notesPanel.style.width = newWidth + 'px';
            }
        });

        document.addEventListener('mouseup', function(e) {
            if (isResizing) {
                isResizing = false;
                document.body.style.cursor = 'default';
            }
        });

        function saveNotes() {
            const noteContent = document.getElementById("note-area").value;
            const noteFilename = document.getElementById("note-filename").value.trim();
            const subject = new URLSearchParams(window.location.search).get("subject") || "general";

            if (!noteContent || !noteFilename) {
                document.getElementById("save-status").innerText = "Please provide both note content and a filename.";
                return;
            }

            fetch("/save_notes", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    content: noteContent,
                    filename: noteFilename,
                    subject: subject
                })
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById("save-status").innerText = data.message || data.error;
            })
            .catch(err => {
                document.getElementById("save-status").innerText = "Error saving notes: " + err;
            });
        }
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    page_type = request.args.get("")
    if 'quiz' in request.url:
        return render_template_string(BASE_TEMPLATE, title="Quiz Generator", show_subject=True, placeholder="Enter chapter or topic to generate a quiz...")
    elif 'doubt' in request.url:
        return render_template_string(BASE_TEMPLATE, title="Doubt Solver", show_subject=False, placeholder="Enter your doubt/question here...")
    else:
        return render_template_string(BASE_TEMPLATE, title="Textbook Chapter Generator", show_subject=True, placeholder="Enter your topic/question...")

@app.route("/generate", methods=["POST"])
def generate():
    return handle_request("chapter")

@app.route("/quiz", methods=["POST"])
def generate_quiz():
    return handle_request("quiz")

@app.route("/doubt", methods=["POST"])
def solve_doubt():
    return handle_request("doubt")

@app.route("/files")
def list_files():
    base_dir = "saved"
    file_data = {}

    for root, dirs, files in os.walk(base_dir):
        subject = os.path.relpath(root, base_dir)
        if subject == ".":
            subject = "general"
        file_data[subject] = [f for f in files if f.endswith(".txt") or f.endswith(".pdf") or f.endswith(".html")]

    return render_template_string(FILE_LIST_TEMPLATE, files=file_data)

@app.route("/delete", methods=["POST"])
def delete_file():
    data = request.get_json()
    subject = data.get("subject")
    filename = data.get("filename")

    if not subject or not filename:
        return jsonify({"error": "Missing subject or filename"}), 400

    path = os.path.join("saved", subject, filename)
    if not os.path.exists(path):
        return jsonify({"error": "File does not exist"}), 404

    try:
        os.remove(path)
        return jsonify({"message": "File deleted successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/view")
def view_file():
    filename = request.args.get("file")
    subject = request.args.get("subject", "general")

    if not filename:
        return "Missing filename", 400

    if subject == ".":
        subject = "general"

    path = os.path.join("saved", subject, filename)
    if not os.path.exists(path):
        return f"File not found: {path}", 404

    # If it's a PDF, just send the path to the template
    if filename.lower().endswith(".pdf"):
        file_url = f"/static/{subject}/{filename}"
        return render_template_string(FILE_VIEW_TEMPLATE, filename=filename, content=None, pdf_url=file_url)

    # Else it's text
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return render_template_string(FILE_VIEW_TEMPLATE, filename=filename, content=content, pdf_url=None)
    except Exception as e:
        return f"Failed to read file: {str(e)}", 500

@app.route('/static/<subject>/<filename>')
def serve_saved_file(subject, filename):
    return send_from_directory(os.path.join('saved', subject), filename)

@app.route("/save_notes", methods=["POST"])
def save_notes():
    data = request.get_json()
    subject = data.get("subject", "general").strip().lower()
    filename = data.get("filename", "").strip()
    content = data.get("content", "")

    if not filename or not content:
        return jsonify({"error": "Missing filename or content"}), 400

    # Ensure subject folder exists
    folder_path = os.path.join("saved", subject)
    os.makedirs(folder_path, exist_ok=True)

    # Ensure .txt extension
    if not filename.endswith(".txt"):
        filename += ".txt"

    full_path = os.path.join(folder_path, filename)

    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return jsonify({"message": f"Notes saved successfully to {filename}."})
    except Exception as e:
        return jsonify({"error": f"Failed to save notes: {str(e)}"}), 500


def handle_request(mode):
    data = request.get_json()
    subject = request.args.get("subject", "general")
    prompt = data.get("prompt", "")

    if not prompt:
        return jsonify({"error": "Empty prompt"}), 400

    if mode == "chapter":
        full_prompt = f"Generate a textbook chapter for subject: {subject}\nPrompt: {prompt}"
    elif mode == "quiz":
        full_prompt = f"Create a quiz with answers for subject: {subject}\nTopic: {prompt}"
    elif mode == "doubt":
        full_prompt = f"Answer the following student doubt in a detailed and simple manner:\n{prompt}"
    else:
        return jsonify({"error": "Invalid mode"}), 400

    try:
        response_text = send_to_backend(full_prompt)
        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def fix_utf8_misinterpretation(text):
    try:
        return text.encode("latin1").decode("utf-8")
    except Exception:
        return text

def send_to_backend(prompt):
    HOST = '127.0.0.1'
    PORT = 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(prompt.encode('utf-8'))

        response_data = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            response_data += chunk

    # Step 1: decode JSON as UTF-8
    decoded_json = response_data.decode("utf-8")
    data = json.loads(decoded_json)

    # Step 2: extract the raw HTML-like string
    raw = data.get("responses", [""])[0]

    # Step 3: decode Unicode escape sequences like \u003C
    first_pass = raw.encode('utf-8').decode('unicode_escape')

    # Step 4: Fix mis-decoded UTF-8 characters (like emojis or ⋅)
    corrected_encoding = first_pass.encode('latin1').decode('utf-8')

    # Step 5: Unescape HTML entities (e.g., &lt; → <)
    final_html = html.unescape(corrected_encoding)

    # Optional: strip data-* attributes if you don't need them
    final_html = re.sub(r'\sdata-[a-zA-Z\-]+="[^"]*"', '', final_html)

    return final_html

if __name__ == "__main__":

    @app.route("/save", methods=["POST"])
    def save_file():
        data = request.get_json()
        subject = data.get("subject", "general").lower()
        filename = data.get("filename", "").strip()
        content = data.get("content", "")

        if not filename or not content:
            return jsonify({"error": "Missing filename or content"}), 400

        # Since content is already the inner HTML of the div, save it directly
        save_dir = os.path.join("saved", subject)
        os.makedirs(save_dir, exist_ok=True)
        full_path = os.path.join(save_dir, f"{filename}.html")

        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)  # save the HTML snippet directly
            return jsonify({"message": f"Saved successfully to {full_path}"})
        except Exception as e:
            return jsonify({"error": f"Failed to save: {str(e)}"}), 500



    app.run(debug=True, port=5000)