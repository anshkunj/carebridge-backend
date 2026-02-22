from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

# PDF Libraries
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics

app = Flask(__name__)
CORS(app)

# ============================
# AI STYLE TRIAGE ENGINE
# ============================

def analyze_health(symptoms, age):

    symptoms = symptoms.lower()
    score = 0

    if "fever" in symptoms: score += 2
    if "cough" in symptoms: score += 2
    if "fatigue" in symptoms: score += 1
    if "headache" in symptoms: score += 1
    if "vomiting" in symptoms: score += 3
    if "dizziness" in symptoms: score += 3

    if "chest pain" in symptoms: score += 5
    if "breathing" in symptoms or "shortness" in symptoms:
        score += 5

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
        advice = "Consult doctor if symptoms persist."

    else:
        risk = "High"
        confidence = 95
        advice = "🚨 Immediate medical attention recommended."

    sustainability_score = max(0, 100 - (score * 10))

    return {
        "risk": risk,
        "confidence": confidence,
        "explanation": advice,
        "sustainability": sustainability_score
    }


# ============================
# PDF REPORT GENERATOR
# ============================

def generate_pdf_report(symptoms, risk, confidence, advice):

    # Register Unicode Medical Font
    pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))

    filename = "medical_report.pdf"

    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("🏥 CareBridge Medical Report", styles["Heading1"]))
    content.append(Spacer(1,12))

    content.append(Paragraph(f"Symptoms: {symptoms}", styles["Normal"]))
    content.append(Spacer(1,12))

    content.append(Paragraph(f"Risk Level: {risk}", styles["Heading2"]))
    content.append(Paragraph(f"Confidence: {confidence}%", styles["Normal"]))
    content.append(Spacer(1,12))

    content.append(Paragraph("Medical Advice:", styles["Heading2"]))
    content.append(Paragraph(advice, styles["Normal"]))

    doc.build(content)

    return filename


# ============================
# API ENDPOINTS
# ============================

@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>CareBridge AI</title>

<style>

body{
margin:0;
display:flex;
justify-content:center;
align-items:center;
height:100vh;
font-family:Segoe UI,sans-serif;
background:linear-gradient(-45deg,#0f172a,#020617,#0ea5e9,#0284c7);
background-size:400% 400%;
animation:gradientMove 12s ease infinite;
color:white;
text-align:center;
}

@keyframes gradientMove{
0%{background-position:0% 50%;}
50%{background-position:100% 50%;}
100%{background-position:0% 50%;}
}

.card{
padding:50px;
border-radius:25px;
backdrop-filter:blur(20px);
background:rgba(0,0,0,0.4);
box-shadow:0 20px 60px rgba(0,0,0,0.6);
}

a{
display:inline-block;
margin-top:25px;
padding:14px 28px;
border-radius:12px;
background:#38bdf8;
color:black;
text-decoration:none;
font-weight:bold;
transition:0.3s;
}

a:hover{
transform:scale(1.05);
background:#0ea5e9;
}

h1{
color:#38bdf8;
}

</style>

</head>

<body>

<div class="card">

<h1>🚑 CareBridge AI Health Analyzer</h1>

<p>
Accessibility First | AI Powered Healthcare Risk Analysis
</p>

<a href="https://YOUR_GITHUB_PAGES_LINK" target="_blank">
🌍 Visit Frontend Application
</a>

</div>

</body>
</html>
"""

@app.route("/analyze", methods=["POST"])
def analyze():

    try:
        data = request.get_json()

        symptoms = data.get("symptoms", "")
        age = int(data.get("age", 0))

        result = analyze_health(symptoms, age)

        # Generate PDF Report
        pdf_file = generate_pdf_report(
            symptoms,
            result["risk"],
            result["confidence"],
            result["explanation"]
        )

        result["report_download"] = pdf_file

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