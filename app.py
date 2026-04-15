from flask import Flask, render_template, request, redirect, url_for, session
import re

app = Flask(__name__)
app.secret_key = "secret123"

# 🔍 Detect prompt attacks
def detect_attack(text):
    patterns = {
        "Prompt Injection": [
            r"ignore (all|previous) instructions",
            r"disregard rules",
            r"override system",
            r"forget previous"
        ],
        "Jailbreak Attempt": [
            r"act as",
            r"pretend to be",
            r"you are no longer",
            r"bypass",
            r"jailbreak"
        ],
        "Malicious Intent": [
            r"hack",
            r"crack password",
            r"password cracking",
            r"bypass security",
            r"exploit",
            r"malware",
            r"virus",
            r"steal data"
        ]
    }

    detected_type = "Safe"
    risk_score = 0
    matched_phrases = []

    for category, pattern_list in patterns.items():
        for pattern in pattern_list:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                matched_phrases.append(match.group())  # ✅ actual matched text
                risk_score += 30

                if detected_type == "Safe":
                    detected_type = category

    # Multiple threats
    if len(matched_phrases) > 1:
        detected_type = "Multiple Threats 🚨"

    # Risk level
    if risk_score == 0:
        risk = "Low ✅"
    elif risk_score < 60:
        risk = "Medium ⚠️"
    else:
        risk = "High 🚨"

    return detected_type, risk, matched_phrases


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":
        text = request.form.get("text", "")

        if text.strip() != "":
            attack_type, risk, matches = detect_attack(text)

            session['text'] = text
            session['attack_type'] = attack_type
            session['risk'] = risk
            session['matches'] = matches

            return redirect(url_for('home'))

    # GET request
    text = session.pop('text', "")
    attack_type = session.pop('attack_type', "")
    risk = session.pop('risk', "")
    matches = session.pop('matches', [])

    return render_template("index.html",
                           text=text,
                           attack_type=attack_type,
                           risk=risk,
                           matches=matches)


if __name__ == "__main__":
    app.run(debug=True)