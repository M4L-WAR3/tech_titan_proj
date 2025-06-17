from flask import Flask, render_template_string, request, jsonify
import socket

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Textbook Chapter Generator</title>
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
        <h1>Textbook Chapter Generator</h1>
        <label for="subject">Choose subject:</label>
        <select id="subject">
            <option value="physics">Physics</option>
            <option value="chemistry">Chemistry</option>
            <option value="biology">Biology</option>
        </select>
        <br>
        <textarea id="prompt" placeholder="Enter your topic/question..."></textarea><br>
        <button onclick="sendPrompt()">Generate Chapter</button>

        <h2>Response:</h2>
        <pre id="response">Waiting for input...</pre>
    </div>

    <script>
        function sendPrompt() {
            const subject = document.getElementById('subject').value;
            const prompt = document.getElementById('prompt').value;

            fetch(`/generate?subject=${subject}`, {
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
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    subject = request.args.get("subject", "general")
    prompt = data.get("prompt", "")

    if not prompt:
        return jsonify({"error": "Empty prompt"}), 400

    full_prompt = f"Generate a textbook chapter for subject: {subject}\nPrompt: {prompt}"

    try:
        response_text = send_to_backend(full_prompt)
        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def send_to_backend(prompt):
    print(f"Prompt {prompt} was sent to server!")
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
    app.run(debug=True, port=5000)
