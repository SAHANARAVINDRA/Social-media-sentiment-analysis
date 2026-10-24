import cv2
import numpy as np
from tensorflow.keras.models import load_model

# Load trained model
model = load_model("emotion_model.h5")  # change to .keras if needed

# Emotion labels (must match FER2013 order)
emotion_labels = ['angry','disgust','fear','happy','neutral','sad','surprise']

# Load Haar Cascade face detector
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

# Load image
img = cv2.imread("test.jpg")  # Put your image name here
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Detect face
faces = face_cascade.detectMultiScale(gray, 1.3, 5)

for (x, y, w, h) in faces:
    face = gray[y:y+h, x:x+w]
    face = cv2.resize(face, (48, 48))
    face = face / 255.0
    face = np.reshape(face, (1, 48, 48, 1))

    prediction = model.predict(face)
    emotion = emotion_labels[np.argmax(prediction)]

    print("Predicted Emotion:", emotion)

    # Draw result on image
    cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
    cv2.putText(img, emotion, (x, y-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)

cv2.imshow("Result", img)
cv2.waitKey(0)
cv2.destroyAllWindows()