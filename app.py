from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ============================
# AI STYLE TRIAGE ENGINE
# ============================

def analyze_health(symptoms, age):

    symptoms = symptoms.lower()
    score = 0

    # Symptom intelligence scoring
    if "fever" in symptoms: score += 2
    if "cough" in symptoms: score += 2
    if "fatigue" in symptoms: score += 1
    if "headache" in symptoms: score += 1
    if "vomiting" in symptoms: score += 3
    if "dizziness" in symptoms: score += 3

    if "chest pain" in symptoms: score += 5
    if "breathing" in symptoms or "shortness" in symptoms:
        score += 5

    # Age risk factor
    if age >= 60: score += 3
    if age <= 5: score += 2

    # Risk classification
    if score <= 3:
        risk = "Low"
        confidence = 75
        advice = "Rest, hydrate and monitor symptoms."

    elif score <= 7:
        risk = "Moderate"
        confidence = 85
        advice = "Consider consulting doctor if symptoms persist."

    else:
        risk = "High"
        confidence = 95
        advice = "🚨 Immediate medical attention recommended."

    # Sustainability / Health impact score (Unique hackathon feature)
    sustainability_score = max(0, 100 - (score * 10))

    return {
        "risk": risk,
        "confidence": confidence,
        "explanation": advice,
        "sustainability": sustainability_score
    }


# ============================
# API ENDPOINT
# ============================

@app.route("/")
def home():
    return "CareBridge AI Health Engine 🚀"

@app.route("/analyze", methods=["POST"])
def analyze():

    try:
        data = request.get_json()

        symptoms = data.get("symptoms", "")
        age = int(data.get("age", 0))

        result = analyze_health(symptoms, age)

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "risk": "Error",
            "explanation": str(e),
            "confidence": 0,
            "sustainability": 0
        })


# ============================
# RUN SERVER
# ============================

if __name__ == "__main__":
    app.run()