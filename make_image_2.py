import cv2 as cv
import numpy as np

# 1. Create a blank white piece of paper
img = np.ones((400, 800, 3), dtype=np.uint8) * 255

# 2. Write the Doctor's notes
cv.putText(img, 'Rx:', (30, 80), cv.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)

# The new medicine from the mock DB
cv.putText(img, 'Zifi 200', (120, 180),
           cv.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 4)

# The Dosage Line!
cv.putText(img, 'Take 1 Tab twice daily after food',
           (120, 260), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

# Signature
cv.putText(img, 'Sign: Dr. Gupta', (500, 350),
           cv.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 150), 2)

# 3. Save it
file_name = 'test_zifi.jpg'
cv.imwrite(file_name, img)

print(f"Success! {file_name} has been generated.")
