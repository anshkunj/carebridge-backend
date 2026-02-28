from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
import os
from functools import wraps

# -----------------------------
# App Setup
# -----------------------------
app = Flask(__name__)
CORS(app)

# Rate limiting middleware (Security bonus)
limiter = Limiter(get_remote_address, app=app)

# Load HuggingFace Token securely
from dotenv import load_dotenv
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

# -----------------------------
# Request Validation Middleware
# -----------------------------
def validate_request(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        data = request.json

        if not data or "symptoms" not in data:
            return jsonify({
                "error": "Invalid request payload"
            }), 400

        return f(*args, **kwargs)

    return wrapper


# -----------------------------
# AI Explanation Generator
# -----------------------------
def generate_ai_explanation(symptoms, risk):

    if not HF_TOKEN:
        return "AI explanation unavailable."

    prompt = f"""
    Symptoms: {symptoms}
    Risk Level: {risk}

    Give 2 line simple medical advice.
    """

    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
            headers={"Authorization": f"Bearer {HF_TOKEN}"},
            json={"inputs": prompt}
        )

        return response.json()[0]["generated_text"]

    except:
        return "Monitor symptoms and consult doctor if needed."


# -----------------------------
# Health Analysis Engine
# -----------------------------
def analyze_health(symptoms, age):

    symptoms = symptoms.lower()

    score = 0
    emergency = False

    critical_keywords = [
        "chest pain",
        "shortness of breath",
        "breathing difficulty",
        "unconscious",
        "severe bleeding",
        "heart pain"
    ]

    moderate_keywords = [
        "fever",
        "cough",
        "cold",
        "headache"
    ]

    for word in critical_keywords:
        if word in symptoms:
            score += 6
            emergency = True

    for word in moderate_keywords:
        if word in symptoms:
            score += 2

    try:
        age = int(age)

        if age >= 60:
            score += 3
        if age <= 5:
            score += 2

    except:
        age = 0

    if score <= 3:
        risk = "Low"
        advice = "Home care and hydration recommended"

    elif score <= 7:
        risk = "Moderate"
        advice = "Monitor symptoms closely"

    else:
        risk = "High"
        advice = "Seek medical attention immediately"

    confidence = min(97, 65 + score * 3)

    ai_explanation = generate_ai_explanation(symptoms, risk)

    return {
        "risk": risk,
        "confidence": confidence,
        "explanation": advice,
        "ai_explanation": ai_explanation,
        "emergency": emergency,
        "sustainability_text": "Avoid unnecessary hospital visits to reduce healthcare burden."
    }


# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def landing():

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CareBridge AI</title>

        <style>
            body{
                margin:0;
                height:100vh;
                display:flex;
                justify-content:center;
                align-items:center;
                background:linear-gradient(135deg,#0f172a,#020617);
                color:white;
                font-family:Segoe UI,sans-serif;
                text-align:center;
                animation:fadeIn 1.5s ease;
            }

            .box{
                padding:40px;
                border-radius:25px;
                background:rgba(255,255,255,0.05);
                backdrop-filter:blur(20px);
                box-shadow:0 20px 60px rgba(0,0,0,.5);
            }

            a{
                display:inline-block;
                margin-top:20px;
                padding:14px 30px;
                background:#38bdf8;
                color:black;
                text-decoration:none;
                border-radius:12px;
                font-weight:bold;
            }

            a:hover{
                transform:scale(1.05);
            }

            @keyframes fadeIn{
                from{opacity:0; transform:translateY(20px);}
                to{opacity:1; transform:translateY(0);}
            }

        </style>
    </head>

    <body>

        <div class="box">
            <h1>🚑 CareBridge AI</h1>
            <p>Accessibility First Health Risk Analyzer</p>

            <a href="https://anshkunj.github.io/Carebridge-AI">
                🌍 Open CareBridge Frontend
            </a>
        </div>

    </body>
    </html>
    """
@app.route("/analyze", methods=["POST"])
@limiter.limit("10 per minute")
@validate_request
def analyze():

    data = request.json

    result = analyze_health(
        data.get("symptoms", ""),
        data.get("age", 0)
    )

    return jsonify(result)


# -----------------------------
# Run Server
# -----------------------------
if __name__ == "__main__":
    app.run()
