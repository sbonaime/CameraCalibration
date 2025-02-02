import glob
import pickle
import numpy as np
import cv2 as cv



####### FIND CHESSBOARD CORNERS - OBJECT POINTS AND IMAGE POINTS #######

CHESSBOARDSIZE = (10,7)
SIZE_OF_CHESSBOARD_SQUARES_MM = 24


# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)


# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((CHESSBOARDSIZE[0] * CHESSBOARDSIZE[1], 3), np.float32)
objp[:,:2] = np.mgrid[0:CHESSBOARDSIZE[0],0:CHESSBOARDSIZE[1]].T.reshape(-1,2)

objp = objp * SIZE_OF_CHESSBOARD_SQUARES_MM


# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.


images = glob.glob('./images/*.png')

for image in images:
    img = cv.imread(image)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, CHESSBOARDSIZE, None)

    # If found, add object points, image points (after refining them)
    if ret :
        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners)

        # Draw and display the corners
        cv.drawChessboardCorners(img, CHESSBOARDSIZE, corners2, ret)
        cv.imshow('img', img)
        cv.waitKey(100)


cv.destroyAllWindows()


############## CALIBRATION #############################################

ret, cameraMatrix, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

# Save the camera calibration result for later use (we won't worry about rvecs / tvecs)
with  open( "calibration.pkl", "wb" ) as calibration:
    pickle.dump((cameraMatrix, dist), calibration)

with  open( "cameraMatrix.pkl", "wb" ) as cammatrix:
    pickle.dump(cameraMatrix, cammatrix)

with  open( "dist.pkl", "wb" ) as distpkl:
    pickle.dump(dist, distpkl)


############## UNDISTORTION ############################################

img = cv.imread('./images/img1.png')
h,  w = img.shape[:2]
newCameraMatrix, roi = cv.getOptimalNewCameraMatrix(cameraMatrix, dist, (w,h), 1, (w,h))



# Undistort
dst = cv.undistort(img, cameraMatrix, dist, None, newCameraMatrix)

# crop the image
x, y, w, h = roi
dst = dst[y:y+h, x:x+w]
cv.imwrite('undistort_caliResult1.png', dst)



# Undistort with Remapping
mapx, mapy = cv.initUndistortRectifyMap(cameraMatrix, dist, None, newCameraMatrix, (w,h), 5)
dst = cv.remap(img, mapx, mapy, cv.INTER_LINEAR)

# crop the image
x, y, w, h = roi
dst = dst[y:y+h, x:x+w]
cv.imwrite('initUndistortRectifyMap_caliResult2.png', dst)




# Reprojection Error
mean_error = 0

for i, obj in enumerate(objpoints):
    imgpoints2, _ = cv.projectPoints(obj, rvecs[i], tvecs[i], cameraMatrix, dist)
    error = cv.norm(imgpoints[i], imgpoints2, cv.NORM_L2)/len(imgpoints2)
    mean_error += error

print(f"total error: {mean_error / len(objpoints)}")
