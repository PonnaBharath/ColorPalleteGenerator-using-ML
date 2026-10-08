from flask import Flask, render_template, request
import os

from utils.color_extractor import extract_palette
from utils.palette_recommender import recommend_palette
from utils.user_interest_recommender import recommend_by_interest
from utils.emotion_detector import predict_emotion

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# ===============================
# PREFACE PAGE
# ===============================
@app.route("/")
def preface():
    return render_template("preface.html")


# ===============================
# MAIN PAGE
# ===============================
@app.route("/home", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        mode = request.form.get("mode")

        extracted_colors = []
        recommended_palette = []
        tone = None
        tone_percentage = None
        primary_color = None
        emotion_text = None
        recommendation_type = None
        explanation = None
        file_path = None

        # ===========================
        # IMAGE MODE
        # ===========================
        if mode == "image":

            file = request.files.get("image")

            if file and file.filename != "":
                file_path = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    file.filename
                )
                file.save(file_path)

                # Extract dominant colors
                extracted_colors, tone, primary_color, tone_percentage, explanation = extract_palette(file_path)

                # Predict emotion
                emotion = predict_emotion(file_path)

                if emotion:
                    emotion = emotion.lower()   # normalize
                    emotion_text = emotion.title()

                    recommended_palette = recommend_palette(emotion)
                    recommendation_type = "Emotion-Based Palette"

                else:
                    emotion_text = "No Face Detected"

        # ===========================
        # INTEREST MODE
        # ===========================
        elif mode == "interest":

            interest = request.form.get("interest")

            if interest and interest.strip() != "":
                recommended_palette = recommend_by_interest(interest)
                recommendation_type = "Interest-Based Palette"

        return render_template(
            "result.html",
            image_path=file_path,
            extracted_colors=extracted_colors,
            recommended=recommended_palette,
            palette_tone=tone,
            tone_percentage=tone_percentage,
            primary_color=primary_color,
            emotion=emotion_text,
            recommendation_type=recommendation_type,
            ai_explanation=explanation
        )

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)