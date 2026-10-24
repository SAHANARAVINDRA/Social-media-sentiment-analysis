import numpy as np
import cv2
from tensorflow.keras.models import load_model

# Load trained emotion model
model = load_model("emotion_model.keras")

# Emotion labels
emotion_labels = [
    "angry",
    "disgust",
    "fear",
    "happy",
    "neutral",
    "sad",
    "surprise"
]

# Map emotion to sentiment
emotion_to_sentiment = {
    "happy": "Positive",
    "surprise": "Positive",

    "angry": "Negative",
    "disgust": "Negative",
    "fear": "Negative",
    "sad": "Negative",

    "neutral": "Neutral"
}


def predict_emotion(image_path):

    # Read image
    img = cv2.imread(image_path)

    if img is None:
        return {
            "emotion": "unknown",
            "sentiment": "Neutral",
            "confidence": 0
        }

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Resize according to model input
    gray = cv2.resize(gray, (48, 48))

    # Normalize
    gray = gray.astype("float32") / 255.0

    # Reshape
    gray = np.reshape(gray, (1, 48, 48, 1))

    # Prediction
    prediction = model.predict(gray, verbose=0)

    # Get highest probability
    emotion_index = np.argmax(prediction)

    emotion = emotion_labels[emotion_index]

    # Confidence
    confidence = float(prediction[0][emotion_index]) * 100

    # Convert emotion to sentiment
    sentiment = emotion_to_sentiment.get(
        emotion,
        "Neutral"
    )

    return {
        "emotion": emotion,
        "sentiment": sentiment,
        "confidence": round(confidence, 2)
    }


# Test
if __name__ == "__main__":

    result = predict_emotion("test.jpg")

    print("Predicted Emotion :", result["emotion"])
    print("Sentiment         :", result["sentiment"])
    print("Confidence        :", str(result["confidence"]) + "%")