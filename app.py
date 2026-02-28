from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import io
import os

app = Flask(__name__)

# Allow frontend access
CORS(app, resources={r"/*": {"origins": "*"}})


# -----------------------------
# HEALTH ANALYSIS ENGINE
# -----------------------------

def analyze_health(symptoms, age):

    symptoms = symptoms.lower()

    score = 0
    explanation_list = []

    # Symptom weights
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

    # Detect symptoms safely
    for symptom, weight in symptom_weights.items():
        if symptom in symptoms:
            score += weight
            explanation_list.append(f"{symptom.title()} detected")

    # Age risk factors
    if age >= 60:
        score += 4
        explanation_list.append("Senior age risk factor")

    if age <= 5 and age > 0:
        score += 3
        explanation_list.append("Child age risk factor")

    # -----------------------------
    # Emergency Overrides
    # -----------------------------

    # More strict detection
    symptom_tokens = [s.strip() for s in symptoms.split(",")]

    if "chest pain" in symptom_tokens or "emergency" in symptom_tokens:
        return {
            "risk": "EMERGENCY",
            "confidence": 95,
            "explanation": "Seek emergency medical help immediately",
            "hospital_map": "https://www.google.com/maps/search/?api=1&query=hospital+near+me"
        }

    # -----------------------------
    # Risk Classification
    # -----------------------------

    if score <= 4:
        risk = "Low"
        advice = "Rest, hydrate and monitor symptoms"
        hospital_link = "https://www.google.com/search?q=home+care+tips"

    elif score <= 10:
        risk = "Moderate"
        advice = "Consult doctor if symptoms persist"
        hospital_link = "https://www.google.com/maps/search/?api=1&query=clinic+near+me"

    else:
        risk = "High"
        advice = "Medical consultation strongly recommended"
        hospital_link = "https://www.google.com/maps/search/?api=1&query=hospital+near+me"

    # Confidence calculation
    confidence = min(98, 65 + (score * 2.5))

    explanation_text = " | ".join(explanation_list)
    if explanation_text:
        explanation_text += ". "

    explanation_text += advice

    return {
        "risk": risk,
        "confidence": round(confidence, 2),
        "explanation": explanation_text,
        "hospital_map": hospital_link
    }


# -----------------------------
# ROUTES
# -----------------------------

@app.route("/")
def home():
    return """
    <html>
    <head>
    <title>CareBridge AI</title>
    </head>

    <body style="
    background:#0f172a;
    color:white;
    height:100vh;
    display:flex;
    justify-content:center;
    align-items:center;
    font-family:sans-serif">

    <div style="text-align:center">
        <h1>🚑 CareBridge AI</h1>
        <p>Accessibility First Health Risk Analyzer</p>

        <a href="https://anshkunj.github.io/Carebridge-AI"
        style="padding:14px 28px;
        background:#38bdf8;
        color:black;
        text-decoration:none;
        border-radius:12px;
        font-weight:bold;
        display:inline-block;
        margin-top:20px">
        Open Frontend 🌍
        </a>
    </div>

    </body>
    </html>
    """


# -----------------------------
# Risk Analysis Endpoint
# -----------------------------

@app.route("/analyze", methods=["POST"])
def analyze():

    try:
        data = request.json or {}

        symptoms = data.get("symptoms", "")
        age = int(data.get("age", 0))

        result = analyze_health(symptoms, age)

        return jsonify(result)

    except Exception:
        return jsonify({
            "risk": "Error",
            "confidence": 0,
            "explanation": "Server processing error"
        }), 500


# -----------------------------
# REPORT GENERATION
# -----------------------------

@app.route("/generate-report", methods=["POST"])
def generate_report():

    try:
        data = request.get_json(force=True) or {}

        symptoms = data.get("symptoms", "")
        age = int(data.get("age", 0))

        result = analyze_health(symptoms, age)

        # -----------------------------
        # PDF Setup
        # -----------------------------

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer)

        from reportlab.lib import colors
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_CENTER

        # -----------------------------
        # Styles
        # -----------------------------

        title_style = ParagraphStyle(
            name="title",
            fontSize=24,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#0ea5e9"),
            spaceAfter=20
        )

        section_style = ParagraphStyle(
            name="section",
            fontSize=14,
            textColor=colors.HexColor("#38bdf8"),
            spaceAfter=12
        )

        normal_style = ParagraphStyle(
            name="normal",
            fontSize=11,
            leading=18
        )

        # -----------------------------
        # Report Elements
        # -----------------------------

        elements = []

        # Title
        elements.append(
            Paragraph("🚑 CareBridge AI Medical Report", title_style)
        )

        elements.append(Spacer(1, 20))

        # -----------------------------
        # Patient Table
        # -----------------------------

        table_data = [
            ["Field", "Details"],
            ["Patient Age", str(age)],
            ["Symptoms", symptoms if symptoms else "Not Provided"],
            ["Risk Level", result.get("risk", "Unknown")],
            ["Confidence Score", str(result.get("confidence", 0)) + "%"]
        ]

        table = Table(table_data, colWidths=[180, 320])

        table.setStyle(TableStyle([

            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0ea5e9")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),

            ("BACKGROUND", (0,1), (-1,-1), colors.HexColor("#0f172a")),
            ("TEXTCOLOR", (0,1), (-1,-1), colors.white),

            ("GRID", (0,0), (-1,-1), 1, colors.HexColor("#38bdf8")),
            ("PADDING", (0,0), (-1,-1), 12),

        ]))

        elements.append(table)

        elements.append(Spacer(1, 25))

        # -----------------------------
        # Medical Assessment
        # -----------------------------

        elements.append(
            Paragraph("🩺 Medical Assessment", section_style)
        )

        elements.append(
            Paragraph(result.get("explanation", ""), normal_style)
        )

        # -----------------------------
        # Emergency Warning
        # -----------------------------

        if result.get("risk") in ["High", "EMERGENCY"]:

            elements.append(Spacer(1, 20))

            emergency_text = """
⚠ High Risk Alert

Immediate medical consultation is strongly recommended.
Visit nearest hospital if symptoms worsen.
"""

            from reportlab.lib.styles import ParagraphStyle

            elements.append(
                Paragraph(
                    emergency_text,
                    ParagraphStyle(
                        name="emergency",
                        fontSize=12,
                        textColor=colors.red,
                        leading=18
                    )
                )
            )

        # -----------------------------
        # Footer
        # -----------------------------

        elements.append(Spacer(1, 40))

        elements.append(
            Paragraph(
                "Powered by CareBridge AI Health Intelligence",
                ParagraphStyle(
                    name="footer",
                    alignment=TA_CENTER,
                    fontSize=9,
                    textColor=colors.grey
                )
            )
        )

        doc.build(elements)

        buffer.seek(0)

        return send_file(
            buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="CareBridge_Medical_Report.pdf"
        )

    except Exception as e:

        print("Report Generation Error:", str(e))

        return jsonify({
            "error": "Report generation failed"
        }), 500

# -----------------------------

if __name__ == "__main__":
    import os
    
    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )