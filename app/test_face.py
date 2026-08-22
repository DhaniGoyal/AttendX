from face_verification import compare_faces

result = compare_faces(
    "../baseline.jpg",
    "../live.jpg"
)

print(result)