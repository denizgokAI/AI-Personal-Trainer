import cv2
import mediapipe as mp
import time
import math
import numpy as np

# --- SETTINGS ---
mpPose = mp.solutions.pose
pose = mpPose.Pose()

# Select Camera: 0 for Laptop, 1 for External (Iriun etc.)
cap = cv2.VideoCapture(0)

# Set Camera Resolution to HD (1280x720)
cap.set(3, 1280)
cap.set(4, 720)

# --- VARIABLES ---
reps_right = 0  # Rep counter for Right side
reps_left = 0  # Rep counter for Left side
dir = 0  # Direction: 0 (Down/Ext), 1 (Up/Flex)
pTime = 0
is_running = False  # System starts in PAUSED state
current_exercise = "SQUAT"
current_side = "RIGHT"
set_history = []  # Stores completed sets

WINDOW_NAME = "AI Gym Trainer Pro"


# --- UI FUNCTION: GLASSMORPHISM PANEL ---
def draw_glass_panel(img, x, y, w, h, text_lines, color=(0, 255, 0), is_header=True):
    overlay = img.copy()

    # Draw semi-transparent background
    cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 0, 0), cv2.FILLED)
    alpha = 0.5
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

    # Draw border
    cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)

    # Render Text
    for i, line in enumerate(text_lines):
        if is_header and i == 0:
            font_scale = 0.8
            thickness = 2
            y_offset = 35
        else:
            font_scale = 0.6
            thickness = 2
            y_offset = 35 + (i * 30)

        cv2.putText(img, line, (x + 15, y + y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)


# --- ANGLE CALCULATION & SKELETON DRAWING ---
def findAngle(img, p1, p2, p3, lmList, draw=True):
    # Safety check to prevent index errors
    if p1 >= len(lmList) or p2 >= len(lmList) or p3 >= len(lmList):
        return 0

    x1, y1 = lmList[p1][1:]
    x2, y2 = lmList[p2][1:]
    x3, y3 = lmList[p3][1:]

    # Calculate Angle
    angle = math.degrees(math.atan2(y3 - y2, x3 - x2) -
                         math.atan2(y1 - y2, x1 - x2))
    if angle < 0: angle += 360
    if angle > 180: angle = 360 - angle

    # Draw Skeleton Logic
    if draw:
        # Default Color: Gray (When Paused)
        color_line = (150, 150, 150)

        if is_running:
            color_line = (255, 255, 255)  # White (Active)
            threshold_met = False

            # Check Thresholds for Visual Feedback (Green Lines)
            if current_exercise == "SQUAT" and angle < 80: threshold_met = True
            if current_exercise == "CURL" and angle < 50: threshold_met = True  # Threshold set to 50

            if threshold_met: color_line = (0, 255, 0)

        cv2.line(img, (x1, y1), (x2, y2), color_line, 4)
        cv2.line(img, (x3, y3), (x2, y2), color_line, 4)
        cv2.circle(img, (x2, y2), 10, (0, 255, 255), cv2.FILLED)

    return angle


print("AI Gym Trainer: Final Release Loaded...")

# Full Screen Setup
cv2.namedWindow(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    success, img = cap.read()
    if not success: break

    # Resize to Full HD manually for consistent UI placement
    img = cv2.resize(img, (1920, 1080))
    img = cv2.flip(img, 1)  # Mirror Mode for natural user experience

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(imgRGB)
    lmList = []

    h_screen, w_screen, _ = img.shape

    if results.pose_landmarks:
        for id, lm in enumerate(results.pose_landmarks.landmark):
            h, w, c = img.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            lmList.append([id, cx, cy])

        if len(lmList) != 0:
            angle = 0

            # --- INTELLIGENT SIDE SELECTION ---
            # Corrects the "Mirror Paradox" by swapping Left/Right landmarks
            if current_exercise == "SQUAT":
                target_min, target_max = 80, 160
                if current_side == "RIGHT":
                    idx_1, idx_2, idx_3 = 23, 25, 27  # User sees Right -> Data uses Left
                else:
                    idx_1, idx_2, idx_3 = 24, 26, 28

            elif current_exercise == "CURL":
                # Updated Threshold: 50 degrees for better form
                target_min, target_max = 50, 160
                if current_side == "RIGHT":
                    idx_1, idx_2, idx_3 = 11, 13, 15  # User sees Right -> Data uses Left
                else:
                    idx_1, idx_2, idx_3 = 12, 14, 16

            # Always draw skeleton (Gray if paused, Colored if active)
            angle = findAngle(img, idx_1, idx_2, idx_3, lmList)

            # --- REP COUNTING LOGIC (Active Only) ---
            if is_running:
                if angle <= target_min:
                    if dir == 0: dir = 1
                if angle >= target_max:
                    if dir == 1:
                        # Increment specific side counter
                        if current_side == "RIGHT":
                            reps_right += 1
                        else:
                            reps_left += 1
                        dir = 0

            # --- DYNAMIC PROGRESS BAR ---
            bar_x = int(w_screen * 0.92)
            bar_top = 100
            bar_bottom = h_screen - 100

            per = np.interp(angle, (target_min, target_max), (100, 0))
            bar = np.interp(angle, (target_min, target_max), (100, bar_bottom))

            # Clamp bar values to stay within UI
            if bar > bar_bottom: bar = bar_bottom
            if bar < bar_top: bar = bar_top

            # Bar Color Logic
            bar_color = (0, 255, 0)  # Green default
            if not is_running:
                bar_color = (100, 100, 100)  # Gray when paused
            elif per >= 100:
                bar_color = (0, 255, 255)  # Yellow when target hit

            # Draw Bar
            cv2.rectangle(img, (bar_x, bar_top), (bar_x + 30, bar_bottom), (50, 50, 50), 3)
            cv2.rectangle(img, (bar_x, int(bar)), (bar_x + 30, bar_bottom), bar_color, cv2.FILLED)
            cv2.putText(img, f'{int(per)}%', (bar_x - 10, bar_top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    # --- UI PANELS ---

    # 1. INFO PANEL: Shows active side reps + Total summary
    current_reps = reps_right if current_side == "RIGHT" else reps_left

    info_lines = [
        current_exercise,
        f"SIDE: {current_side}",
        f"REPS: {current_reps}",
        f"(Total: L:{reps_left} R:{reps_right})"
    ]
    draw_glass_panel(img, 50, 50, 350, 180, info_lines, color=(255, 100, 0))

    # 2. HISTORY PANEL
    history_lines = ["HISTORY"]
    if not set_history:
        history_lines.append("No sets yet")
    else:
        for idx, set_data in enumerate(set_history[-5:]):
            # Format: "1. SQ | L:15 R:12"
            ex_short = set_data['mode'][:2]
            l_rep = set_data['left']
            r_rep = set_data['right']
            history_lines.append(f"{idx + 1}. {ex_short} | L:{l_rep} R:{r_rep}")

    draw_glass_panel(img, 50, 250, 350, 240, history_lines, color=(0, 200, 255))

    # 3. CONTROLS GUIDE (Bottom Right)
    controls_x = w_screen - 350
    controls_y = h_screen - 320

    controls_lines = [
        "CONTROLS",
        "s : Start / Pause",
        "m : Mode (Squat/Curl)",
        "t : Side (L / R)",
        "f : Finish Set",
        "r : Reset All",
        "q : Quit App"
    ]
    draw_glass_panel(img, controls_x, controls_y, 300, 270, controls_lines, color=(200, 200, 200))

    # 4. STATUS INDICATOR (Bottom Left)
    status_text = "ACTIVE" if is_running else "PAUSED (Skeleton Visible)"
    color_status = (0, 255, 0) if is_running else (150, 150, 150)

    cv2.putText(img, f"STATUS: {status_text}", (50, h_screen - 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color_status, 2, cv2.LINE_AA)

    # FPS Counter
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (w_screen - 150, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2, cv2.LINE_AA)

    cv2.imshow(WINDOW_NAME, img)

    # --- KEYBOARD INPUT HANDLER ---
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        is_running = not is_running
    elif key == ord('m'):
        # Reset counters when switching exercise mode
        reps_right = 0
        reps_left = 0
        dir = 0
        current_exercise = "CURL" if current_exercise == "SQUAT" else "SQUAT"

    elif key == ord('t'):
        # Switch tracking side WITHOUT resetting counters
        dir = 0
        current_side = "LEFT" if current_side == "RIGHT" else "RIGHT"

    elif key == ord('f'):
        # Finish Set: Save to history and reset
        if reps_right > 0 or reps_left > 0:
            set_history.append({
                "mode": current_exercise,
                "left": reps_left,
                "right": reps_right
            })
            reps_right = 0
            reps_left = 0
            dir = 0

    elif key == ord('r'):
        # Hard Reset
        reps_right = 0
        reps_left = 0
        set_history = []
        dir = 0

cap.release()
cv2.destroyAllWindows()