from flask import Flask, render_template_string, request, jsonify
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
