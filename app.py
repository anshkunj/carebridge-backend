from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "CareBridge API Running 🚀"

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    symptoms = data.get("symptoms", "").lower()
    age = int(data.get("age", 0))

    risk = "Low"
    explanation = "Symptoms appear mild."

    if "chest pain" in symptoms or age > 60:
        risk = "High"
        explanation = "Chest pain or higher age increases serious health risk."
    elif "fever" in symptoms or "cough" in symptoms:
        risk = "Moderate"
        explanation = "Common infection-related symptoms detected."

    return jsonify({
        "risk": risk,
        "explanation": explanation
    })

if __name__ == "__main__":
    app.run(debug=True)