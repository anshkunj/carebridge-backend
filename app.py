from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "CareBridge AI Running 🚀"

@app.route("/analyze", methods=["POST"])
def analyze():

    data = request.get_json()

    symptoms = data.get("symptoms","").lower()
    age = int(data.get("age",0))

    score = 0

    # Intelligence scoring
    if "fever" in symptoms: score += 2
    if "cough" in symptoms: score += 2
    if "chest pain" in symptoms: score += 5
    if "breathing" in symptoms: score += 5
    if "vomiting" in symptoms: score += 3
    if age > 60: score += 3

    # Risk logic
    if score <= 3:
        risk = "Low"
        confidence = 75
        hospital = "No emergency visit required"

    elif score <= 7:
        risk = "Moderate"
        confidence = 85
        hospital = "Visit clinic if symptoms persist"

    else:
        risk = "High"
        confidence = 95
        hospital = "🚨 Visit emergency hospital immediately"

    sustainability_score = max(0, 100 - score*10)

    return jsonify({
        "risk": risk,
        "confidence": confidence,
        "hospital": hospital,
        "sustainability": sustainability_score,
        "report": "AI based health triage analysis completed."
    })

if __name__ == "__main__":
    app.run()