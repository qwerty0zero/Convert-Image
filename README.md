🖼 Image Converter GUI
A simple drag-and-drop image converter built with Python and PySide6.

This desktop app allows you to convert images into multiple formats (PNG, JPEG, WEBP, AVIF) with optional aspect ratio cropping. Designed to be fast, easy to use, and visually intuitive with progress tracking and quick access to output folders.

✨ Features
✅ Drag-and-drop interface for quick file conversion
📁 Supports multiple output formats: PNG, JPEG, WEBP, AVIF
🔲 Optional aspect ratio cropping (16:9, 4:3, 9:16, 3:4)
🎚 Adjustable quality settings (1–100)
🔄 Progress bar for visual conversion feedback
🧹 One-click clear to delete output files
📂 Open output folder directly from the app    

📦 Requirements
Python 3.7+
pillow
pillow-avif
PySide6

Install dependencies:

pip install -r requirements.txt

🚀 How to Use

Launch the app:
python image_converter.py

Select the desired output formats and aspect ratios (optional).
Set image quality if needed.
Drag image files into the window.
Wait for the conversion to complete — you’ll see progress as it works.
Click 📂 Open Folder to access the output directory.
Converted images will be saved in the converted/ folder, organized by format and aspect ratio.

📷 Supported Formats
.png
.jpg / .jpeg
.webp
.avif

📐 Optional Aspect Ratios
16:9
4:3
9:16
3:4



