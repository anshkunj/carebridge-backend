from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
import io
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# -----------------------------
# HEALTH ANALYSIS ENGINE
# -----------------------------

def analyze_health(symptoms, age):

    symptoms = symptoms.lower()
    score = 0
    explanation_list = []

    symptom_weights = {
        "fever": 2,
        "cough": 2,
        "breathing": 5,
        "shortness": 5,
        "chest pain": 8,
        "headache": 1,
        "dizziness": 2,
        "vomiting": 3,
        "fatigue": 1
    }

    for symptom, weight in symptom_weights.items():
        if symptom in symptoms:
            score += weight
            explanation_list.append(f"{symptom.title()} detected")

    if age >= 60:
        score += 4
        explanation_list.append("Senior age risk factor")

    if 0 < age <= 5:
        score += 3
        explanation_list.append("Child age risk factor")

    symptom_tokens = [s.strip() for s in symptoms.split(",")]

    if "chest pain" in symptom_tokens or "emergency" in symptom_tokens:
        return {
            "risk": "EMERGENCY",
            "confidence": 95,
            "explanation": "Seek emergency medical help immediately"
        }

    if score <= 4:
        risk = "Low"
        advice = "Rest, hydrate and monitor symptoms"

    elif score <= 10:
        risk = "Moderate"
        advice = "Consult doctor if symptoms persist"

    else:
        risk = "High"
        advice = "Medical consultation strongly recommended"

    confidence = min(98, 65 + (score * 2.5))

    explanation_text = " | ".join(explanation_list)
    if explanation_text:
        explanation_text += ". "
    explanation_text += advice

    return {
        "risk": risk,
        "confidence": round(confidence, 2),
        "explanation": explanation_text
    }

# -----------------------------
# SUSTAINABILITY ENGINE
# -----------------------------

def calculate_green_score(risk):
    if risk == "Low":
        return 90
    elif risk == "Moderate":
        return 60
    elif risk == "High":
        return 25
    else:
        return 0

def estimate_environmental_impact(risk):
    if risk == "Low":
        return {"co2_saved": 4.5, "paper_saved": 1}
    elif risk == "Moderate":
        return {"co2_saved": 2.0, "paper_saved": 0.5}
    else:
        return {"co2_saved": 0, "paper_saved": 0}

def generate_medical_summary(result):
    risk = result.get("risk", "Unknown")

    if risk == "Low":
        return "Low health risk detected. Preventive care reduces unnecessary hospital visits and environmental impact."

    elif risk == "Moderate":
        return "Moderate risk detected. Early consultation recommended to prevent condition escalation."

    elif risk == "High":
        return "High risk symptoms detected. Immediate medical consultation strongly recommended."

    else:
        return "Emergency symptoms detected. Seek immediate medical help."

# -----------------------------
# ROUTES
# -----------------------------

@app.route("/")
def home():
    return "<h1>🚑 CareBridge Sustainable AI</h1>"

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.json or {}
        symptoms = data.get("symptoms", "")
        age = int(data.get("age", 0))
        result = analyze_health(symptoms, age)
        return jsonify(result)
    except:
        return jsonify({"risk": "Error"}), 500

# -----------------------------
# LEGENDARY REPORT GENERATION
# -----------------------------

@app.route("/generate-report", methods=["POST"])
def generate_report():

    try:
        data = request.get_json(force=True) or {}

        symptoms = data.get("symptoms", "")
        age = int(data.get("age", 0))

        result = analyze_health(symptoms, age)
        summary = generate_medical_summary(result)

        sustainability = estimate_environmental_impact(result["risk"])
        green_score = calculate_green_score(result["risk"])

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer)

        elements = []

        title_style = ParagraphStyle(
            name="title",
            fontSize=24,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#0ea5e9"),
            spaceAfter=20
        )

        normal_style = ParagraphStyle(
            name="normal",
            fontSize=11,
            leading=18
        )

        elements.append(
            Paragraph("🌍 CareBridge Sustainable AI Medical Report", title_style)
        )
        elements.append(Spacer(1, 15))

        table_data = [
            ["Field", "Value"],
            ["Age", str(age)],
            ["Symptoms", symptoms],
            ["Risk Level", result["risk"]],
            ["Confidence", str(result["confidence"]) + "%"],
            ["Green Sustainability Score", f"{green_score}/100"],
            ["Estimated CO₂ Saved", f"{sustainability['co2_saved']} kg"],
            ["Paper Saved", f"{sustainability['paper_saved']} sheet(s)"]
        ]

        table = Table(table_data, colWidths=[200, 300])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0ea5e9")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("GRID", (0,0), (-1,-1), 1, colors.HexColor("#38bdf8")),
            ("PADDING", (0,0), (-1,-1), 10),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 20))

        elements.append(
            Paragraph("🧠 AI Medical Insight", title_style)
        )
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(summary, normal_style))

        elements.append(Spacer(1, 30))
        elements.append(
            Paragraph(
                "This report promotes preventive healthcare and environmental sustainability by reducing unnecessary hospital visits and resource consumption.",
                normal_style
            )
        )

        doc.build(elements)
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="CareBridge_Sustainable_Report.pdf"
        )

    except Exception as e:
        print("Report Error:", str(e))
        return jsonify({"error": "Report generation failed"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)