import sys
import shutil
import pillow_avif
from pathlib import Path
from PIL import Image, features
from PySide6.QtWidgets import (
    QApplication, QLabel, QVBoxLayout, QWidget, QCheckBox,
    QHBoxLayout, QPushButton, QProgressBar, QSpinBox, QFormLayout
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices

SUPPORTED_FORMATS = ['PNG', 'JPEG', 'WEBP', "AVIF"]

ASPECT_RATIOS = {
    "16-9": 16 / 9,
    "4-3": 4 / 3,
    "9-16": 9 / 16,
    "3-4": 3 / 4,
}


class DropLabel(QLabel):
    def __init__(self, get_selected_formats, get_selected_ratios, get_quality, progress_bar, parent=None):
        super().__init__(parent)
        self.get_selected_formats = get_selected_formats
        self.get_selected_ratios = get_selected_ratios
        self.progress_bar = progress_bar
        self.get_quality = get_quality
        self.parent = parent  # Store reference to parent for accessing the open folder button

        self.setText("Перетащи сюда изображения")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 2px dashed #aaa; font-size: 16px;")
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        image_paths = [f for f in files if Path(f).suffix.lower() in [".png", ".jpg", ".jpeg", ".webp", ".avif"]]
        if image_paths:
            self.setText("Конвертирую...")
            self.convert_images(image_paths)
            self.setText("Готово! Перетащи ещё изображения.")
            # Enable the open folder button after conversion
            self.parent.open_folder_button.setEnabled(True)

    def convert_images(self, image_paths):
        selected_formats = self.get_selected_formats()
        selected_ratios = self.get_selected_ratios()
        quality = self.get_quality()
        formats_to_use = selected_formats or SUPPORTED_FORMATS

        total_tasks = len(image_paths) * len(formats_to_use)
        if selected_ratios:
            total_tasks *= len(selected_ratios)

        self.progress_bar.setMaximum(total_tasks)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        progress = 0

        for path in image_paths:
            img = Image.open(path)
            name = Path(path).stem

            for fmt in formats_to_use:
                base_dir = Path("converted") / fmt

                if selected_ratios:
                    for ratio_name, ratio_value in selected_ratios.items():
                        cropped = self.crop_to_aspect(img.copy(), ratio_value)
                        self.save_image(cropped, base_dir / ratio_name, name, fmt, quality)
                        progress += 1
                        self.progress_bar.setValue(progress)

                    # оригинал
                    self.save_image(img.copy(), base_dir / 'base', name, fmt, quality)
                    progress += 1
                    self.progress_bar.setValue(progress)
                else:
                    self.save_image(img, base_dir, name, fmt, quality)
                    progress += 1
                    self.progress_bar.setValue(progress)

        self.progress_bar.setVisible(False)

    def save_image(self, img, out_dir, name, fmt, quality):
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{name}.{fmt.lower()}"

        try:
            img.save(out_path, fmt, quality=quality)
        except Exception as e:
            print(f"Ошибка при сохранении {out_path}: {e}")

    def crop_to_aspect(self, image, target_ratio):
        width, height = image.size
        current_ratio = width / height

        if current_ratio > target_ratio:
            new_width = int(height * target_ratio)
            left = (width - new_width) // 2
            return image.crop((left, 0, left + new_width, height))
        else:
            new_height = int(width / target_ratio)
            top = (height - new_height) // 2
            return image.crop((0, top, width, top + new_height))


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Конвертер изображений")
        self.setMinimumSize(500, 500)

        layout = QVBoxLayout()

        # Форматы
        format_layout = QHBoxLayout()
        self.format_checkboxes = {}
        for fmt in SUPPORTED_FORMATS:
            cb = QCheckBox(fmt)
            self.format_checkboxes[fmt] = cb
            format_layout.addWidget(cb)
        layout.addLayout(format_layout)

        # Соотношения
        ratio_layout = QHBoxLayout()
        self.ratio_checkboxes = {}
        for label in ASPECT_RATIOS:
            cb = QCheckBox(label)
            self.ratio_checkboxes[label] = cb
            ratio_layout.addWidget(cb)
        layout.addLayout(ratio_layout)

        # Качество
        quality_layout = QHBoxLayout()
        quality_label = QLabel("Качество (1–100):")
        self.quality_input = QSpinBox()
        self.quality_input.setRange(1, 100)
        self.quality_input.setValue(81)
        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.quality_input)
        layout.addLayout(quality_layout)

        # Drop-зона
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.drop_label = DropLabel(
            self.get_selected_formats, self.get_selected_ratios,
            self.get_quality, self.progress_bar, self
        )
        layout.addWidget(self.drop_label)
        layout.addWidget(self.progress_bar)

        # Button layout
        button_layout = QHBoxLayout()

        # Кнопка очистки
        self.clear_button = QPushButton("🗑 Очистить всё")
        self.clear_button.clicked.connect(self.clear_output)
        button_layout.addWidget(self.clear_button)

        # Кнопка открытия папки
        self.open_folder_button = QPushButton("📂 Открыть папку")
        self.open_folder_button.clicked.connect(self.open_output_folder)
        self.open_folder_button.setEnabled(False)  # Disabled by default
        button_layout.addWidget(self.open_folder_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_selected_formats(self):
        return [fmt for fmt, cb in self.format_checkboxes.items() if cb.isChecked()]

    def get_selected_ratios(self):
        return {label: ASPECT_RATIOS[label] for label, cb in self.ratio_checkboxes.items() if cb.isChecked()}

    def get_quality(self):
        return self.quality_input.value()

    def clear_output(self):
        output_dir = Path("converted")
        if output_dir.exists():
            shutil.rmtree(output_dir)
        self.drop_label.setText("Очищено! Перетащи сюда изображения")
        self.open_folder_button.setEnabled(False)  # Disable open folder button after clearing

    def open_output_folder(self):
        output_dir = Path("converted")
        if output_dir.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(output_dir.absolute())))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())