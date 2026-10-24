from flask import Flask, render_template, request, redirect, flash, session, url_for, jsonify
from sentiment_model import predict_sentiment, analyze_post_and_comments, analyze_image_sentiment
from database import init_db, register_user, validate_user, add_history, get_history
from werkzeug.utils import secure_filename
from datetime import datetime
import json
import os
import base64
import pytesseract
import cv2
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import instaloader
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
vader = SentimentIntensityAnalyzer()



history_data = []


# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

init_db()


# --------------------------------------------------
# Utility Functions
# --------------------------------------------------

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def load_dataset():
    with open("dataset/posts.json", "r") as f:
        return json.load(f)


# --------------------------------------------------
# Landing Page
# --------------------------------------------------

@app.route("/")
def landing():
    return render_template("home.html")


# --------------------------------------------------
# Authentication
# --------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if register_user(username, password):
            return redirect("/login")
        else:
            return "Username already exists"

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = validate_user(username, password)
        if user:
            session["user"] = username
            return redirect("/platform")
        else:
            return "Invalid credentials"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")



# --------------------------------------------------
# Dashboard
# --------------------------------------------------

@app.route("/platform")
def platform():
    if "user" not in session:
        return redirect("/login")
    return render_template("platform.html")


# --------------------------------------------------
# Text Analyzer
# --------------------------------------------------

@app.route('/analyzer', methods=['GET', 'POST'])
def analyzer():
    result = None
    text = None

    if request.method == 'POST':
        text = request.form.get('text')
        result = predict_sentiment(text)
        save_history("Comment Analysis", text, result)

    return render_template('analyzer.html', result=result, text=text)

from flask import request, jsonify

@app.route('/analyze_instagram', methods=['POST'])
def analyze_instagram():
    try:
        data = request.get_json()

        # ✅ Get shortcode instead of URL
        shortcode = data.get("shortcode")

        if not shortcode:
            return jsonify({"error": "No Instagram shortcode provided"})

        # ⚠️ Since we cannot fetch Instagram caption reliably,
        # simulate or ask user input (temporary solution)

        # Example dummy text (replace later)
        sample_text = "This is an amazing post!"

        # Use your sentiment function
        sentiment = predict_sentiment(sample_text)

        return jsonify({
            "sentiment": sentiment
        })

    except Exception as e:
        return jsonify({"error": str(e)})
# --------------------------------------------------
# Posts Section
# --------------------------------------------------

@app.route("/posts", methods=["GET", "POST"])
def posts():
    if "user" not in session:
        return redirect("/login")

    result = None
    image_filename = None
    extracted_text = None

    if request.method == "POST":

        # IMAGE UPLOAD
        if "image" in request.files and request.files["image"].filename != "":
            image = request.files["image"]

            if allowed_file(image.filename):
                filename = secure_filename(image.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                image.save(filepath)

                image_filename = filename
                result = analyze_image_sentiment(filepath)

        # CAMERA IMAGE
        elif request.form.get("camera_image"):
            camera_data = request.form.get("camera_image")
            header, encoded = camera_data.split(",", 1)
            data = base64.b64decode(encoded)

            filename = "captured_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".jpg"
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

            with open(filepath, "wb") as f:
                f.write(data)

            image_filename = filename
            result = analyze_image_sentiment(filepath)

        # INSTAGRAM LINK
        elif request.form.get("insta_link"):

            link = request.form.get("insta_link").strip()

            if "instagram.com" not in link:
                flash("Invalid Instagram link")
                return redirect("/posts")

            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                response = requests.get(link, headers=headers)
                soup = BeautifulSoup(response.text, "html.parser")

                meta = soup.find("meta", property="og:image")

                if not meta:
                    flash("Unable to extract image")
                    return redirect("/posts")

                image_url = meta["content"]
                img_data = requests.get(image_url).content

                filename = "insta_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".jpg"
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

                with open(filepath, "wb") as f:
                    f.write(img_data)

                image_filename = filename
                result = analyze_image_sentiment(filepath)

            except Exception:
                flash("Error processing Instagram link")
                return redirect("/posts")

        # OCR IMAGE
        elif "comment_image" in request.files and request.files["comment_image"].filename != "":
            comment_image = request.files["comment_image"]

            filename = secure_filename(comment_image.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            comment_image.save(filepath)

            image_filename = filename

            img = cv2.imread(filepath)
            extracted_text = pytesseract.image_to_string(img)

            result = predict_sentiment(extracted_text)

        # SAVE HISTORY
        if result:
            add_history(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Post Analysis",
                "Image / Link / OCR",
                image_filename,
                result
            )

    return render_template(
        "posts.html",
        result=result,
        image=image_filename,
        extracted_text=extracted_text
    )


@app.route("/instagram", methods=["GET", "POST"])
def instagram():
    result = None
    pos = neg = neu = 0
    image_url = None
    post_text = ""
    comments_text = ""

    if request.method == "POST":

        file = request.files["image"]
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        image_url = "/" + filepath

        post_text = request.form["post"]
        comments_text = request.form["comments"]

        comments_list = comments_text.split("\n")

        # Example sentiment logic
        for comment in comments_list:
            sentiment = predict_sentiment(comment)

            if sentiment == "Positive":
                pos += 1
            elif sentiment == "Negative":
                neg += 1
            else:
                neu += 1

        result = "Analysis Completed"

    return render_template(
        "instagram.html",
        result=result,
        pos=pos,
        neg=neg,
        neu=neu,
        image_url=image_url,
        post_text=post_text,
        comments_text=comments_text
    )
# --------------------------------------------------
# Comments Section
# --------------------------------------------------

@app.route("/comments", methods=["GET", "POST"])
def comments():
    if "user" not in session:
        return redirect("/login")

    result = None

    if request.method == "POST":
        text = request.form.get("comment")

        if text and text.strip():
            result = predict_sentiment(text)

            add_history(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Comment Analysis",
                text,
                None,
                result
            )

    return render_template("comments.html", result=result)


# --------------------------------------------------
# History
# --------------------------------------------------

@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/login")

    data = get_history()
    return render_template("history.html", history=data)


# --------------------------------------------------
# Insights
# --------------------------------------------------

@app.route("/insights")
def insights():
    if "user" not in session:
        return redirect("/login")

    db_history = get_history()

    pos = neg = neu = 0

    for row in db_history:
        sentiment = row[4]
        if sentiment.startswith("Positive"):
            pos += 1
        elif sentiment.startswith("Negative"):
            neg += 1
        elif sentiment.startswith("Neutral"):
            neu += 1

    return render_template("insights.html", pos=pos, neg=neg, neu=neu)


# --------------------------------------------------
# About
# --------------------------------------------------

@app.route("/about")
def about():
    return render_template("about.html")


def predict_sentiment(text):
    if not text:
        return "Neutral"

    text = text.strip()

    scores = vader.polarity_scores(text)   # ✅ FIXED HERE
    compound = scores['compound']

    print("TEXT:", text)
    print("SCORE:", scores)

    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    else:
        return "Neutral"
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)