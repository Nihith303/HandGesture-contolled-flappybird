import cv2
import mediapipe as mp

def handgesture_setup():
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
    mp_draw = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(0)
    return (cap, hands, mp_draw)

def is_hand_closed(landmarks):
    closed = (
        landmarks[8].y > landmarks[6].y and  
        landmarks[12].y > landmarks[10].y and  
        landmarks[16].y > landmarks[14].y and  
        landmarks[20].y > landmarks[18].y  
    )
    return closed

def generate_results(cap, hands):
    success, img = cap.read()
    if success:
        img = cv2.flip(img, 1)  
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = hands.process(img_rgb)
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                if is_hand_closed(hand_landmarks.landmark):
                    return True
    return False






# # Initialize MediaPipe and OpenCV
# mp_hands = mp.solutions.hands
# mp_drawing = mp.solutions.drawing_utils

# # Set up webcam
# cap = cv2.VideoCapture(0)

# # Initialize MediaPipe Hands
# with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break

#         # Flip the image horizontally for a mirror-like effect
#         frame = cv2.flip(frame, 1)

#         # Convert the BGR image to RGB
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#         # Process the frame and detect hands
#         result = hands.process(rgb_frame)

#         if result.multi_hand_landmarks:
#             for hand_landmarks in result.multi_hand_landmarks:
#                 # Draw the hand landmarks on the image
#                 mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

#                 # Get the coordinates of the thumb tip and index finger tip
#                 thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
#                 index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

#                 # Calculate the Euclidean distance between the thumb tip and index finger tip
#                 distance = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5

#                 # Determine if the hand is open or closed based on the distance
#                 if distance > 0.05:  # Adjust this threshold based on your camera setup
#                     status = "Hand Open"
#                 else:
#                     status = "Hand Closed"

#                 # Display the status on the frame
#                 cv2.putText(frame, status, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

#         # Display the frame
#         cv2.imshow('Hand Open/Close Detection', frame)

#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

# # Release resources
# cap.release()
# cv2.destroyAllWindows()
