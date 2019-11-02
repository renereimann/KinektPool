import cv2
import numpy as np
while True:
        image = cv2.imread("test.png")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        print(type(gray))
        print(np.shape(gray))
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 10, np.array([]), 100, 30, 1, 30)
        if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                for (x, y, r) in circles:
                        cv2.circle(image, (x, y), r, (0, 255, 0), 4)
                        cv2.rectangle(image, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1) 
                cv2.imshow("output", image)
        if cv2.waitKey(1) == ord('q'):
            break
cv2.destroyAllWindows()
