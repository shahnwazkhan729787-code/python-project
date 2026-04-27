import cv2
import dlib
import numpy as np
from imutils import face_utils
from scipy.spatial import distance as dist
import datetime
import time

# Constants for EAR thresholds and head pose distraction angle limits
EAR_THRESHOLD = 0.25
EAR_CONSEC_FRAMES = 15
HEAD_POSE_YAW_LIMIT = 15
HEAD_POSE_PITCH_LIMIT = 15

# Load dlib face detector and facial landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

# Landmark indices for eyes
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

def get_head_pose(shape, frame_size=(480, 640)):
    model_points = np.array([
        (0.0, 0.0, 0.0),             # Nose tip
        (0.0, -330.0, -65.0),        # Chin
        (-225.0, 170.0, -135.0),     # Left eye left corner
        (225.0, 170.0, -135.0),      # Right eye right corner
        (-150.0, -150.0, -125.0),    # Left mouth corner
        (150.0, -150.0, -125.0)      # Right mouth corner
    ])

    image_points = np.array([
        shape[30],    # Nose tip
        shape[8],     # Chin
        shape[36],    # Left eye left corner
        shape[45],    # Right eye right corner
        shape[48],    # Left Mouth corner
        shape[54]     # Right mouth corner
    ], dtype="double")

    focal_length = frame_size[1]
    center = (frame_size[1]/2, frame_size[0]/2)
    camera_matrix = np.array(
        [[focal_length, 0, center[0]],
         [0, focal_length, center[1]],
         [0, 0, 1]], dtype="double"
    )
    dist_coeffs = np.zeros((4,1)) 

    success, rotation_vector, translation_vector = cv2.solvePnP(
        model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)
    
    rotation_mat, _ = cv2.Rodrigues(rotation_vector)
    pose_mat = cv2.hconcat((rotation_mat, translation_vector))
    _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(pose_mat)

    pitch, yaw, roll = euler_angles.flatten()
    return pitch, yaw, roll

def draw_overlay(frame, status_dict, ear, pitch, yaw):
    # Draw the productivity monitor overlay like screenshot

    # Semi-transparent panel
    overlay = frame.copy()
    panel_height = 140
    panel_width = 380
    alpha = 0.6
    cv2.rectangle(overlay, (5, 5), (5+panel_width, 5+panel_height), (50, 50, 50), -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    x_start = 15
    y_start = 25
    line_height = 20
    color_active = (0, 255, 0)    # Green
    color_inactive = (0, 165, 255) # Orange

    # Title
    cv2.putText(frame, "PRODUCTIVITY MONITOR", (x_start, y_start - 10), cv2.FONT_HERSHEY_DUPLEX, 0.6, color_active, 1)

    # Face detected or not
    face_status = "YES" if status_dict['face_detected'] else "NO"
    cv2.putText(frame, f"Face detected? {face_status}", (x_start, y_start), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color_active if status_dict['face_detected'] else color_inactive, 1)

    # Head Viewed
    head_status = "YES" if status_dict['head_facing'] else "NO"
    cv2.putText(frame, f"Head viewed? {head_status}", (x_start, y_start + line_height), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color_active if status_dict['head_facing'] else color_inactive, 1)

    # Eyes Open
    eyes_status = "YES" if status_dict['eyes_open'] else "NO"
    cv2.putText(frame, f"Eyes opened? {eyes_status}", (x_start, y_start + 2*line_height), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color_active if status_dict['eyes_open'] else color_inactive, 1)

    # EAR score
    cv2.putText(frame, f"Eye Aspect Ratio (EAR): {ear:.2f}", (x_start, y_start + 3*line_height), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_active, 1)
    # Head pose pitch/yaw
    cv2.putText(frame, f"Head pose(pitch/yaw): {pitch:.1f}, {yaw:.1f}", (x_start, y_start + 4*line_height), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_active, 1)

    # STATUS
    status_color = (0, 255, 0) if status_dict['focused'] else (0, 165, 255)
    status_text = "ATTENTIVE" if status_dict['focused'] else "DISTRACTED"
    cv2.putText(frame, f"STATUS: {status_text}", (x_start, y_start + 5*line_height + 5), cv2.FONT_HERSHEY_DUPLEX, 0.7, status_color, 2)

    # Session info lines
    session_duration = status_dict['session_duration']
    attentive_time = status_dict['attentive_time']
    distracted_time = status_dict['distracted_time']
    attention_score = 0.0 if session_duration == 0 else (attentive_time / session_duration) * 100

    info_x = 420
    info_y = 40
    info_line_height = 25

    session_str = str(datetime.timedelta(seconds=int(session_duration)))
    attentive_str = str(datetime.timedelta(seconds=int(attentive_time)))
    distracted_str = str(datetime.timedelta(seconds=int(distracted_time)))

    cv2.putText(frame, f"Session: {session_str}", (info_x, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(frame, f"Attentive time: {attentive_str}", (info_x, info_y + info_line_height), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
    cv2.putText(frame, f"Distracted time: {distracted_str}", (info_x, info_y + 2*info_line_height), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,165,255), 2)
    cv2.putText(frame, f"Attention Score: {attention_score:.1f}%", (info_x, info_y + 3*info_line_height), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)


def main():
    print("[INFO] Starting FlowMode-like Productivity Monitor")
    print("Instructions:")
    print(" - Press 's' to Start Tracking")
    print(" - Press 'c' to Calibrate (look at camera NORMAL position)")
    print(" - Press 'q' to Stop/Quit")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Cannot access webcam")
        return

    session_active = False
    calibration_done = False
    calibration_yaw = 0.0
    calibration_pitch = 0.0

    closed_eyes_frames = 0
    session_start_time = None
    attentive_time = 0
    distracted_time = 0

    status_dict = {
        'face_detected': False,
        'head_facing': False,
        'eyes_open': False,
        'focused': False,
        'session_duration': 0,
        'attentive_time': 0,
        'distracted_time': 0
    }

    font = cv2.FONT_HERSHEY_SIMPLEX

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Can't receive frame, exiting")
            break

        frame = cv2.resize(frame, (1024, 576)) # widescreen for overlay info
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        if session_active and session_start_time is None:
            session_start_time = time.time()

        face_detected = False
        eyes_open = False
        head_facing = False
        ear = 0.0
        pitch = 0.0
        yaw = 0.0

        for face in faces:
            face_detected = True
            shape = predictor(gray, face)
            shape = face_utils.shape_to_np(shape)

            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]

            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)
            ear = (leftEAR + rightEAR) / 2.0
            eyes_open = ear > EAR_THRESHOLD

            pitch, yaw, roll = get_head_pose(shape, frame_size=frame.shape[:2])

            # Determine if head is facing reasonably calibrated position +/- tolerance
            if calibration_done:
                yaw_diff = abs(yaw - calibration_yaw)
                pitch_diff = abs(pitch - calibration_pitch)
                head_facing = (yaw_diff < HEAD_POSE_YAW_LIMIT) and (pitch_diff < HEAD_POSE_PITCH_LIMIT)
            else:
                # Before calibration, don't declare head facing
                head_facing = False

            # Draw facial landmarks on eyes for visualization
            cv2.polylines(frame, [leftEye], True, (0, 255, 0), 1)
            cv2.polylines(frame, [rightEye], True, (0, 255, 0), 1)

            # Draw face rectangle
            x, y, w, h = face.left(), face.top(), face.width(), face.height()
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            break # Process only first face
        
        # Determine focus/distraction status - require calibration for meaningful results
        if session_active and calibration_done:
            if face_detected and head_facing and eyes_open:
                focused = True
            else:
                focused = False
        else:
            focused = False

        # Update session timers and counters
        if session_active and session_start_time is not None:
            elapsed = time.time() - session_start_time
            status_dict['session_duration'] = elapsed

            if focused:
                attentive_time += 1/30  # assuming ~30 FPS
            else:
                distracted_time += 1/30
            
            status_dict['attentive_time'] = attentive_time
            status_dict['distracted_time'] = distracted_time

        # Update status dictionary for overlay
        status_dict.update({
            'face_detected': face_detected,
            'head_facing': head_facing,
            'eyes_open': eyes_open,
            'focused': focused,
            'ear': ear,
            'pitch': pitch,
            'yaw': yaw
        })

        # Draw overlays like screenshot
        draw_overlay(frame, status_dict, ear, pitch, yaw)

        # Draw control instructions on frame
        controls_text = "Controls: [S] Start  [C] Calibrate  [Q] Stop/Quit"
        cv2.putText(frame, controls_text, (10, frame.shape[0]-10), font, 0.6, (200, 200, 200), 2)

        # Show session and calibration status bars
        if session_active:
            status_msg = "Tracking Active"
            status_color = (0, 180, 0)
        else:
            status_msg = "Tracking Inactive"
            status_color = (0, 0, 255)

        if calibration_done:
            calib_msg = "Calibration Done"
            calib_color = (0, 180, 0)
        else:
            calib_msg = "Calibration Needed (Press 'C')"
            calib_color = (0, 165, 255)

        # Display status bars
        cv2.rectangle(frame, (10, 5), (frame.shape[1]-10, 25), (40, 40, 40), -1)
        cv2.putText(frame, status_msg, (10, 20), font, 0.7, status_color, 2)
        cv2.putText(frame, calib_msg, (400, 20), font, 0.7, calib_color, 2)

        # Show frame
        cv2.imshow("FlowMode - Productivity Monitor", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("[INFO] Quitting...")
            break
        elif key == ord('s'):
            session_active = True
            session_start_time = time.time()
            attentive_time = 0
            distracted_time = 0
            print("[INFO] Tracking started.")
        elif key == ord('c'):
            if face_detected:
                calibration_yaw = yaw
                calibration_pitch = pitch
                calibration_done = True
                print(f"[INFO] Calibration done. Yaw: {calibration_yaw:.1f}, Pitch: {calibration_pitch:.1f}")
            else:
                print("[WARNING] Can't calibrate. Face not detected.")

    cap.release()
    cv2.destroyAllWindows()

    # Session summary
    if session_active:
        session_time = status_dict['session_duration']
        att_time = status_dict['attentive_time']
        dist_time = status_dict['distracted_time']
        attention_score = att_time / session_time * 100 if session_time > 0 else 0.0
        print("\nSession Summary:")
        print(f"Total Time: {str(datetime.timedelta(seconds=int(session_time)))}")
        print(f"Attentive Time: {str(datetime.timedelta(seconds=int(att_time)))}")
        print(f"Distracted Time: {str(datetime.timedelta(seconds=int(dist_time)))}")
        print(f"Attention Score: {attention_score:.1f}%")

if __name__ == "__main__":
    main()