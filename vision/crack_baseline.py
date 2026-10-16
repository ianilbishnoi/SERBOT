"""Edge-detection baseline for cracks (paper [2] compares its CNN against Canny/Sobel).
Usage: python vision/crack_baseline.py wall.jpg
"""
import sys
import cv2

img = cv2.imread(sys.argv[1])
gray = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (5, 5), 0)
edges = cv2.Canny(gray, 50, 150)
ratio = edges.astype(bool).mean()
print(f"edge pixel ratio = {ratio:.4f}  ->  {'possible crack' if ratio > 0.02 else 'no crack'} (tune threshold)")
cv2.imwrite("crack_edges.png", edges)
