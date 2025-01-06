import sys
import cv2

cap = cv2.VideoCapture(0)

num = 0

while cap.isOpened():

    succes, img = cap.read()

    k = cv2.waitKey(5)

    if k == ord('q'): # wait for 'q' key to exit
        sys.exit()
    elif k == ord('s'): # wait for 's' key to save frame
        cv2.imwrite(f'images/img{str(num)}.png', img)
        print("image saved!")
        num += 1

    cv2.imshow('Img',img)

# Release and destroy all windows before termination
cap.release()

cv2.destroyAllWindows()
