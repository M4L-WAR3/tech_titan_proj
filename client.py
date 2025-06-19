from flask import Flask, render_template_string, request, jsonify, send_from_directory
import socket
import os

app = Flask(__name__)

BASE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 30px; background-color: #f9f9f9; }
        .container { max-width: 800px; margin: auto; }
        textarea { width: 100%; height: 100px; font-size: 1em; margin-bottom: 10px; }
        button { padding: 10px 20px; font-size: 1em; }
        pre { background: #eee; padding: 15px; white-space: pre-wrap; border-radius: 5px; }
        select { font-size: 1em; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ title }}</h1>
        {% if show_subject %}
        <label for="subject">Choose subject:</label>
        <select id="subject">
            <option value="physics">Physics</option>
            <option value="chemistry">Chemistry</option>
            <option value="biology">Biology</option>
        </select>
        {% endif %}
        <br>
        <textarea id="prompt" placeholder="{{ placeholder }}"></textarea><br>
        <button onclick="sendPrompt()">Submit</button>

        <h2>Response:</h2>
        <pre id="response">Waiting for input...</pre>

        <h3>Save Chapter</h3>
        <input type="text" id="filename" placeholder="Enter file name (without extension)" style="width: 70%; padding: 8px;" />
        <button onclick="saveToFile()">Save</button>
        <pre id="save-status"></pre>
    </div>

    <script>
        function sendPrompt() {
            const prompt = document.getElementById('prompt').value;
            const subject = document.getElementById('subject') ? document.getElementById('subject').value : "";
            let endpoint = window.location.search.includes("quiz") ? "/quiz" :
                           window.location.search.includes("doubt") ? "/doubt" : "/generate";

            fetch(`${endpoint}?subject=${subject}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt: prompt })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('response').innerText = data.response || data.error;
            })
            .catch(err => {
                document.getElementById('response').innerText = "Error: " + err;
            });
        }

        function saveToFile() {
        const content = document.getElementById('response').innerText;
        const subject = document.getElementById('subject') ? document.getElementById('subject').value : "general";
        const filename = document.getElementById('filename').value;

        if (!filename || !content || content === "Waiting for input...") {
            document.getElementById('save-status').innerText = "Error: Please enter a filename and generate content first.";
            return;
        }

        fetch("/save", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ subject: subject, filename: filename, content: content })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('save-status').innerText = data.message || data.error;
        })
        .catch(err => {
            document.getElementById('save-status').innerText = "Error: " + err;
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
    <style>
        body { font-family: Arial; padding: 20px; }
        ul { list-style: none; }
        li { margin: 5px 0; }
        .delete-button { margin-left: 10px; color: red; cursor: pointer; }
    </style>
</head>
<body>
    <h1>Saved Files</h1>
    {% for subject, file_list in files.items() %}
        <h3>{{ subject.title() }}</h3>
        <ul>
            {% for file in file_list %}
                <li>
                    <a href="/view?subject={{ subject }}&file={{ file }}">{{ file }}</a>
                    <span class="delete-button" onclick="deleteFile('{{ subject }}', '{{ file }}')">🗑️</span>
                </li>
            {% endfor %}
        </ul>
    {% endfor %}
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
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            height: 100vh;
            display: flex;
            overflow: hidden;
        }

        #notes-container {
            display: flex;
            flex-direction: row;
            width: 25%;
            min-width: 150px;
            max-width: 50%;
            border-right: 2px solid #ccc;
            position: relative;
        }

        #notes {
            flex-grow: 1;
            padding: 10px;
            overflow: auto;
            background: #f0f0f0;
        }

        #resizer {
            width: 5px;
            cursor: ew-resize;
            background: #ccc;
        }

        #file-content {
            flex-grow: 1;
            padding: 20px;
            overflow: auto;
            background: #fff;
        }

        textarea {
            width: 100%;
            height: 90%;
            resize: none;
        }

        iframe {
            width: 100%;
            height: 90vh;
            border: none;
        }
        pre {
        white-space: pre-wrap;
        word-wrap: break-word;
        background: #f8f8f8;
        padding: 10px;
        border-radius: 4px;
    }
    </style>
</head>
<body>
    <div id="notes-container">
        <div id="notes">
            <h3>Notes</h3>
            <textarea id="note-area" placeholder="Write your notes here..."></textarea>
            <input type="text" id="note-filename" placeholder="Enter note filename (e.g. notes1.txt)" style="width: 100%; margin-top: 10px;" />
            <button onclick="saveNotes()" style="margin-top: 5px;">Save Notes</button>
            <div id="save-status" style="margin-top: 10px; font-size: 0.9em; color: green;"></div>
        </div>
        <div id="resizer"></div>
    </div>

    <div id="file-content">
        <h2>{{ filename }}</h2>
        {% if pdf_url %}
            <iframe src="{{ pdf_url }}"></iframe>
        {% else %}
            <pre>{{ content }}</pre>
        {% endif %}
    </div>

    <script>
        const resizer = document.getElementById('resizer');
        const container = document.getElementById('notes-container');

        let isResizing = false;

        resizer.addEventListener('mousedown', function(e) {
            isResizing = true;
            document.body.style.cursor = 'ew-resize';
        });

        document.addEventListener('mousemove', function(e) {
            if (!isResizing) return;
            const newWidth = e.clientX;
            if (newWidth > 150 && newWidth < window.innerWidth * 0.5) {
                container.style.width = newWidth + 'px';
            }
        });

        document.addEventListener('mouseup', function(e) {
            isResizing = false;
            document.body.style.cursor = 'default';
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
        file_data[subject] = [f for f in files if f.endswith(".txt") or f.endswith(".pdf")]

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

def send_to_backend(prompt):
    print(f"Prompt sent to backend: {prompt}")
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

    return response_data.decode('utf-8')

if __name__ == "__main__":

    @app.route("/save", methods=["POST"])
    def save_file():
        data = request.get_json()
        subject = data.get("subject", "general").lower()
        filename = data.get("filename", "").strip()
        content = data.get("content", "")

        if not filename or not content:
            return jsonify({"error": "Missing filename or content"}), 400

        # Create subject folder if it doesn't exist
        save_dir = os.path.join("saved", subject)
        os.makedirs(save_dir, exist_ok=True)

        # Save the file as a .txt
        full_path = os.path.join(save_dir, f"{filename}.txt")

        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            return jsonify({"message": f"Saved successfully to {full_path}"})
        except Exception as e:
            return jsonify({"error": f"Failed to save: {str(e)}"}), 500

    app.run(debug=True, port=5000)