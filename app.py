from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from utils import load_data, find_condition
import anthropic
import base64

app = Flask(__name__)
CORS(app)

data = load_data()
anthropic_client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/reset", methods=["POST"])
def reset():
    from utils import reset_state
    reset_state()
    return jsonify({"status": "ok"})

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")

    condition, info = find_condition(user_input, data)

    if info:
        if info["severity"] == "high":
            response = "⚠️ WARNING: " + info["advice"]
        else:
            response = info["advice"]
    else:
        response = "I'm not sure. Please consult a healthcare professional."

    return jsonify({"response": response,
                    "severity": info["severity"] if info else "low"})

@app.route("/analyze-image", methods=["POST"])
def analyze_image():
    body = request.json
    image_data = body.get("image")      # base64 string, no data-url prefix
    media_type = body.get("mediaType", "image/jpeg")

    if not image_data:
        return jsonify({"error": "No image provided"}), 400

    try:
        message = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": (
                                "You are HealthBot, a helpful medical information assistant. "
                                "Analyze this image carefully from a medical/health perspective. "
                                "Describe what you see (e.g. type of rash, burn, wound, skin condition, etc.), "
                                "suggest what condition it might indicate, and give practical first-aid advice. "
                                "If the image is not medical or health-related, politely say so. "
                                "Always remind the user to consult a real doctor for a proper diagnosis. "
                                "Keep your response clear, empathetic, and concise."
                            )
                        }
                    ],
                }
            ],
        )
        response_text = message.content[0].text
        # Determine severity hint from keywords in the response
        severity = "low"
        high_keywords = ["emergency", "immediately", "urgent", "severe", "hospital", "poison", "dangerous"]
        medium_keywords = ["consult", "doctor", "medical attention", "clinic"]
        lower = response_text.lower()
        if any(k in lower for k in high_keywords):
            severity = "high"
        elif any(k in lower for k in medium_keywords):
            severity = "medium"

        return jsonify({"response": response_text, "severity": severity})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)