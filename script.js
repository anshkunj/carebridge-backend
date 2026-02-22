const form = document.getElementById("healthForm");

form.addEventListener("submit", async e=>{
e.preventDefault();

const symptoms = document.getElementById("symptoms").value;
const age = document.getElementById("age").value;

const res = await fetch("https://carebridge-backend-ro4e.onrender.com/analyze",{
method:"POST",
headers:{ "Content-Type":"application/json" },
body:JSON.stringify({symptoms,age})
});

const data = await res.json();

document.getElementById("riskText").innerText =
"Risk : " + data.risk + " | Confidence : " + data.confidence + "%";

let width = data.risk==="Low"?30:
data.risk==="Moderate"?60:90;

document.getElementById("riskBar").style.width = width + "%";

document.getElementById("report").innerText =
data.explanation;
});

/* Theme */
function toggleTheme(){
document.body.classList.toggle("light-theme");
}

/* Text */
function toggleText(){
document.body.classList.toggle("large-text");
}

/* Voice */
function startVoice(){
const speech = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
speech.start();

speech.onresult = e=>{
document.getElementById("symptoms").value =
e.results[0][0].transcript;
};
}
