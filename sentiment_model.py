import re
import cv2
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pytesseract
#from tensorflow.keras.models import load_model

#model = load_model("emotion_model.h5")

emotion_labels = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def analyze_image_sentiment(image_path):

    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) == 0:
        return "No Face Detected"

    x, y, w, h = faces[0]

    face = gray[y:y+h, x:x+w]
    face = cv2.resize(face, (48, 48))
    face = face / 255.0
    face = np.reshape(face, (1, 48, 48, 1))

    prediction = model.predict(face)
    emotion_index = np.argmax(prediction)
    emotion = emotion_labels[emotion_index]

    if emotion == "happy":
        return "Positive"
    elif emotion == "neutral":
        return "Neutral"
    else:
        return "Negative"
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

analyzer = SentimentIntensityAnalyzer()
def analyze_image_type(image_path):
    img = cv2.imread(image_path)

    # Detect text using OCR
    extracted_text = pytesseract.image_to_string(img)
    if len(extracted_text.strip()) > 15:
        return "Contains Text / Letters"

    # Load pre-trained face detector
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) > 0:
        return "Contains Human Face"

    return "Contains Object / Other Content"

# --------------------------------------
# TEXT SENTIMENT FUNCTIONS
# --------------------------------------

def contains_kannada(text):
    return bool(re.search(r'[\u0C80-\u0CFF]', text))


def predict_sentiment(text):

    if contains_kannada(text):
        positive_words = ["ಚೆನ್ನಾಗಿದೆ", "ಅದ್ಭುತ", "ಸಂತೋಷ", "ಮೆಚ್ಚುಗೆ", "ಸೂಪರ್"]
        negative_words = ["ಕೆಟ್ಟ", "ದುಃಖ", "ಕೋಪ", "ಬೇಸರ"]

        for word in positive_words:
            if word in text:
                return "Positive"

        for word in negative_words:
            if word in text:
                return "Negative"

        return "Neutral"

    else:
        score = analyzer.polarity_scores(text)
        compound = score["compound"]

        if compound >= 0.05:
            return "Positive"
        elif compound <= -0.05:
            return "Negative"
        else:
            return "Neutral"


def analyze_post_and_comments(post, comments):

    positive = 0
    negative = 0
    neutral = 0

    all_texts = [post] + comments

    for text in all_texts:
        sentiment = predict_sentiment(text)

        if sentiment == "Positive":
            positive += 1
        elif sentiment == "Negative":
            negative += 1
        else:
            neutral += 1

    if positive > negative and positive > neutral:
        overall = "Positive"
    elif negative > positive and negative > neutral:
        overall = "Negative"
    else:
        overall = "Neutral"

    return overall, positive, negative, neutral


# --------------------------------------
# REAL IMAGE EMOTION CLASSIFICATION
# (OpenCV Only – No TensorFlow, No FER)
# --------------------------------------

# --------------------------------------
# REAL IMAGE EMOTION CLASSIFICATION
# (OpenCV Only – With Emojis)
# --------------------------------------

def analyze_image_sentiment(image_path):
    try:
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        smile_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_smile.xml"
        )

        img = cv2.imread(image_path)

        if img is None:
            return "Neutral 😐"

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=5
        )

        # No face detected
        if len(faces) == 0:
            return "Neutral 😐"

        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]

            smiles = smile_cascade.detectMultiScale(
                roi_gray,
                scaleFactor=1.7,
                minNeighbors=20
            )

            # Smile detected
            if len(smiles) > 0:
                return "Positive 😊"

        # Face detected but no smile
        return "Negative 😢"

    except Exception:
        return "Neutral 😐"
# CAMERA CAPTURE FUNCTION
# --------------------------------------



    # CAMERA FUNCTION  ← PASTE HERE
def capture_image_from_camera(save_path="captured_post.jpg"):
    try:
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Camera not accessible")
            return None

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            cv2.imshow("Press SPACE to Capture | ESC to Exit", frame)

            key = cv2.waitKey(1)

            if key % 256 == 27:
                break

            elif key % 256 == 32:
                cv2.imwrite(save_path, frame)
                break

        cap.release()
        cv2.destroyAllWindows()

        return save_path

    except Exception as e:
        print("Camera error:", e)
        return None