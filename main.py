import threading
import time
import cv2
import mediapipe as mp
import pyautogui
import keyboard

# Initialize MediaPipe Hands and FaceMesh.
mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
mp_drawing = mp.solutions.drawing_utils

def function1():
    global stop_event, switch_event, cap
    cap = cv2.VideoCapture(0)
    while not stop_event.is_set():
        if switch_event.is_set():
            break
        ret, frame = cap.read()
        if not ret:
            break

        # Flip the frame horizontally for a later selfie-view display.
        frame = cv2.flip(frame, 1)

        # Convert the BGR image to RGB.
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame and detect hands and face landmarks.
        hand_results = hands.process(rgb_frame)
        face_results = face_mesh.process(rgb_frame)

        # Draw hand landmarks on the frame.
        if hand_results.multi_hand_landmarks and face_results.multi_face_landmarks:
            hand_landmarks = hand_results.multi_hand_landmarks[0]
            face_landmarks = face_results.multi_face_landmarks[0]

            # Draw hand landmarks.
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Extract landmarks for the thumb and middle fingers.
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

            # Convert normalized coordinates to pixel coordinates.
            h, w, _ = frame.shape
            x_index = int(index_tip.x * w)
            y_index = int(index_tip.y * h)
    
            # Draw circles at the finger tips.
            cv2.circle(frame, (x_index, y_index), 10, (0, 255, 255), -1)

            # Track the mouse cursor with the index finger.
            mouse_x = int(index_tip.x * pyautogui.size().width)
            mouse_y = int(index_tip.y * pyautogui.size().height)
            pyautogui.moveTo(mouse_x, mouse_y, duration=0)

            # Check for left eye landmarks condition.
            # Extract landmarks for left eye.
            if face_landmarks.landmark:
                left_eye_landmark = face_landmarks.landmark[159]

                # Convert normalized coordinates to pixel coordinates.
                left_eye_x = int(left_eye_landmark.x * w)           
                left_eye_y = int(left_eye_landmark.y * h)

                # Draw a circle at the left eye position.
                cv2.circle(frame, (left_eye_x, left_eye_y), 1, (0, 255, 255), -1)

                # Check the condition for left eye click.
                # if face_landmarks.landmark:
                left_eye_y_top = face_landmarks.landmark[154]
                left_eye_y_bottom = face_landmarks.landmark[159]
                if (left_eye_y_top.y - left_eye_y_bottom.y) < 0.004:
                    pyautogui.click()
                    pyautogui.sleep(1)

        # Display the frame.
        cv2.imshow('Hand Tracking', frame)

        # Break the loop if 'q' is pressed.
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture and close windows.
    cap.release()
    cv2.destroyAllWindows()

def function2():
    while not stop_event.is_set():
        if switch_event.is_set():
            break
        print("Running Function 2")
        time.sleep(1)

def run_program():
    global state, stop_event, switch_event
    while True:
        if state:
            switch_event.clear()
            function1()
        else:
            switch_event.clear()
            function2()

def change_state():
    global state, stop_event, switch_event
    while True:
        if keyboard.is_pressed('1'):
            state = True
            # stop_event.set()
            switch_event.set()
            time.sleep(0.1)  # Debounce delay to prevent multiple triggers
        elif keyboard.is_pressed('2'):
            state = False
            # stop_event.set()
            switch_event.set()
            time.sleep(0.1)  # Debounce delay to prevent multiple triggers
        stop_event.clear()

# Define the initial state
state = False

# Define events to control function switching
stop_event = threading.Event()
switch_event = threading.Event()

# Start the program in a separate thread
program_thread = threading.Thread(target=run_program)
program_thread.daemon = True
program_thread.start()

# Run the state change function in the main thread
change_state()
