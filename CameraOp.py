#camera opening 

import cv2

# Try to access the default camera (camera index 0)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Camera could not be opened.")
    exit()

print("Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Error: Frame not read correctly.")
        break

    # Show the video frame
    cv2.imshow('Webcam', frame)

    # Exit when 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close the window
cap.release()
cv2.destroyAllWindows()