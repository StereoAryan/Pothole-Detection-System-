# Pothole-Detection-System-

The Pothole Detection System is an AI-powered computer vision application designed to automatically detect potholes in road surfaces using YOLOv8 and OpenCV. The system aims to assist in road condition monitoring by identifying potholes from images and video streams, reducing the need for completely manual inspection.

The project uses a custom-trained YOLOv8 object detection model to locate potholes and generate bounding boxes around detected regions. The primary trained model used for the final system is best.pt, which contains the finalized model weights used for pothole detection. The best1.pt file included in the repository represents an experimental/trial model and is not used by the final detection pipeline.

🔍 Key Features
AI-based pothole detection using YOLOv8.
Real-time detection from video/camera input.
Detection of multiple potholes within a single frame.
Bounding boxes and confidence scores for detected potholes.
Image and video-based road analysis.
OpenCV-based computer vision processing.
Custom-trained model specifically designed for pothole detection.
User-friendly interface for running the detection system.
Git LFS support for storing large YOLO model weights.
🧠 Model

The final system uses:

YOLOv8 → Custom-trained pothole detection model → best.pt

best.pt is the primary model used by the application. best1.pt was retained in the repository as a trial/experimental model from the development and testing phase and is not part of the final detection pipeline.

🛠️ Technologies Used
Python
YOLOv8 / Ultralytics
OpenCV
PyTorch
Computer Vision
Git & Git LFS
🎯 Objective

The main objective of the project is to demonstrate how deep learning and computer vision can be applied to automated road-condition monitoring. By automatically detecting potholes from visual data, the system can potentially support road inspection, maintenance planning, and development of intelligent transportation infrastructure.

This project was developed as an academic/engineering project with an emphasis on object detection, model training, computer vision, and real-time inference.

📁 Repository Contents
Pothole-Detection-System/
│
├── best.pt
├── best1.pt
├── main2.py
├── Pothole_Detection_Project_Analysis.docx
├── .gitignore
└── .gitattributes

Note: best.pt is the final model used by the system. best1.pt is an experimental/trial model retained for reference and comparison. Both model files are managed using Git LFS due to their large size.
