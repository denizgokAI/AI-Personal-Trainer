# AI Personal Trainer 🏋️‍♂️

An advanced Computer Vision application that acts as a real-time personal gym trainer. It uses **MediaPipe Pose Estimation** to track exercises, count reps, and ensure correct form using geometric analysis.


## 🚀 Project Overview
This project leverages **Artificial Intelligence** and **Trigonometry** to analyze human body movements via a webcam feed. Unlike simple motion detectors, it calculates the precise angle between joints (e.g., Hip-Knee-Ankle for squats) to determine if a repetition is valid.

It features a **"Smart Mirror"** system that automatically adjusts left/right logic based on the user's mirrored webcam input.

## ✨ Key Features
- **Real-time Pose Tracking:** Detects 33 body landmarks at 30+ FPS.
- **Multi-Exercise Support:** - **Squats:** Tracks leg depth (Angle < 80°).
  - **Bicep Curls:** Tracks arm flexion (Angle < 60°).
- **Split Set Logic:** Intelligently tracks **Left** and **Right** side reps separately within the same set.
- **Visual Feedback:** - Dynamic progress bars that change color when the target depth is reached.
  - Skeleton overlay for form correction.
- **Modern UI:** Custom-designed "Glassmorphism" transparent panels for statistics and controls.
- **Smart Mirroring:** Solves the "Webcam Flip Paradox" by re-mapping landmark IDs when switching sides.

## 🛠️ Tech Stack
- **Language:** Python 3.x
- **Computer Vision:** OpenCV (`cv2`)
- **AI/ML Model:** MediaPipe Pose
- **Math:** NumPy (Trigonometric calculations)

## 🎮 Controls
The application is designed to be controlled remotely via keyboard, allowing hands-free usage during workouts.

| Key | Function |
| :---: | --- |
| **`s`** | **Start / Pause** (Activates the counter) |
| **`m`** | **Switch Mode** (Squat <-> Curl) |
| **`t`** | **Switch Side** (Left Arm <-> Right Arm) |
| **`f`** | **Finish Set** (Saves current reps to history panel) |
| **`r`** | **Reset** (Clears all data and history) |
| **`q`** | **Quit Application** |

## ⚙️ How It Works (The Engineering Logic)
1.  **Landmark Extraction:** The app extracts coordinates $(x, y)$ for key joints (Shoulder, Elbow, Wrist, Hip, Knee, Ankle).
2.  **Angle Calculation:** It calculates the angle using the arctangent function:
    $$\text{Angle} = |\tan^{-1}(y_3-y_2, x_3-x_2) - \tan^{-1}(y_1-y_2, x_1-x_2)|$$
3.  **State Machine:** - A rep is counted only when the angle crosses the **"Down Threshold"** (e.g., 60°) and returns to the **"Up Threshold"** (e.g., 160°).
    - This prevents half-reps or jittery counting.

## 📦 Installation & Usage

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/AI-Personal-Trainer.git](https://github.com/denizgokAI/AI-Personal-Trainer.git)
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the application:**
    ```bash
    python main.py
    ```

## 🔮 Future Improvements
- [ ] Add "Push-up" and "Plank" modes.
- [ ] Implement a voice feedback system ("Go lower!", "Great job!").
- [ ] Save workout history to a CSV/Database.

---
*Developed by Deniz Gök*