import cv2
import numpy as np


def compare_faces(baseline_path, live_path):
    baseline = cv2.imread(baseline_path)
    live = cv2.imread(live_path)

    if baseline is None:
        return {
            "success": False,
            "message": "Baseline image not found"
        }

    if live is None:
        return {
            "success": False,
            "message": "Live image not found"
        }

    baseline_gray = cv2.cvtColor(baseline, cv2.COLOR_BGR2GRAY)
    live_gray = cv2.cvtColor(live, cv2.COLOR_BGR2GRAY)

    baseline_gray = cv2.resize(baseline_gray, (200, 200))
    live_gray = cv2.resize(live_gray, (200, 200))

    difference = np.mean(
        np.abs(
            baseline_gray.astype(float) -
            live_gray.astype(float)
        )
    )

    similarity = max(0, 100 - difference)

    if similarity >= 85:
        status = "Present"
    else:
        status = "Proxy Suspected"

    return {
        "success": True,
        "similarity": round(similarity, 2),
        "status": status
    }