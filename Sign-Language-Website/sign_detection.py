import cv2
import mediapipe as mp
import numpy as np

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

def recognize_sign(landmarks):
    """Recognizes sign language gestures based on landmark positions."""
    if landmarks:
        thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip = landmarks[4], landmarks[8], landmarks[12], landmarks[16], landmarks[20]
        thumb_ip, index_pip, middle_pip, ring_pip, pinky_pip = landmarks[3], landmarks[6], landmarks[10], landmarks[14], landmarks[18]

        # "Hello" → Open palm
        if all(tip[1] < pip[1] for tip, pip in zip([index_tip, middle_tip, ring_tip, pinky_tip], [index_pip, middle_pip, ring_pip, pinky_pip])):
            return "Hello 👋"
        
        # "I Love You" → Thumb, index, and pinky extended
        if thumb_tip[1] < thumb_ip[1] and index_tip[1] < index_pip[1] and pinky_tip[1] < pinky_pip[1] and middle_tip[1] > middle_pip[1] and ring_tip[1] > ring_pip[1]:
            return "I Love You ❤️"
        
        # "Please" → Fingers closed, thumb near index
        if all(tip[1] > pip[1] for tip, pip in zip([index_tip, middle_tip, ring_tip, pinky_tip], [index_pip, middle_pip, ring_pip, pinky_pip])) and thumb_tip[0] < index_tip[0]:
            return "Please 🙏"
        
        # "Sorry" → Fist
        if all(tip[1] > pip[1] for tip, pip in zip([index_tip, middle_tip, ring_tip, pinky_tip], [index_pip, middle_pip, ring_pip, pinky_pip])):
            return "Sorry 🙇"
        
        # "Thank You" → Thumb and index extended, moving out
        if thumb_tip[1] < thumb_ip[1] and index_tip[1] < index_pip[1]:
            return "Thank You 🙏"
        
        # "No" → Index and middle extended, others folded
        if index_tip[1] < index_pip[1] and middle_tip[1] < middle_pip[1] and ring_tip[1] > ring_pip[1] and pinky_tip[1] > pinky_pip[1]:
            return "No ❌"
        
        # **Improved Yes Sign** → Closed fist (fingertips near palm)
        finger_closed = all(abs(tip[1] - pip[1]) < 30 for tip, pip in zip([index_tip, middle_tip, ring_tip, pinky_tip], [index_pip, middle_pip, ring_pip, pinky_pip]))
        if finger_closed and abs(thumb_tip[0] - index_tip[0]) < 40:
            return "Yes ✅"

    return "Unknown"

def generate_frames():
    """Generates video frames with gesture detection."""
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # Process the frame
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                h, w, _ = frame.shape
                landmarks = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks.landmark]
                gesture = recognize_sign(landmarks)
                cv2.putText(frame, f"Sign: {gesture}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Encode the frame
        _, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

    cap.release()
