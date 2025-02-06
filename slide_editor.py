import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QTextEdit, QListWidget, QFileDialog, QRadioButton, QButtonGroup, QMessageBox
)
from PyQt5.QtCore import Qt

class SlideEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Slide Editor")
        self.setGeometry(100, 100, 800, 600)

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)

        # Slide list on the left
        self.slide_list = QListWidget()
        self.slide_list.itemClicked.connect(self.load_slide_for_editing)
        self.layout.addWidget(self.slide_list)

        # Slide editor on the right
        self.editor_widget = QWidget()
        self.editor_layout = QVBoxLayout(self.editor_widget)

        # Slide type selection
        self.slide_type_label = QLabel("Slide Type:")
        self.editor_layout.addWidget(self.slide_type_label)

        self.slide_type_group = QButtonGroup()
        self.text_radio = QRadioButton("Text")
        self.image_radio = QRadioButton("Image")
        self.quiz_radio = QRadioButton("Quiz")
        self.slide_type_group.addButton(self.text_radio)
        self.slide_type_group.addButton(self.image_radio)
        self.slide_type_group.addButton(self.quiz_radio)
        self.editor_layout.addWidget(self.text_radio)
        self.editor_layout.addWidget(self.image_radio)
        self.editor_layout.addWidget(self.quiz_radio)

        # Title input
        self.title_label = QLabel("Title:")
        self.title_input = QLineEdit()
        self.editor_layout.addWidget(self.title_label)
        self.editor_layout.addWidget(self.title_input)

        # Content input (for text and quiz)
        self.content_label = QLabel("Content:")
        self.content_input = QTextEdit()
        self.editor_layout.addWidget(self.content_label)
        self.editor_layout.addWidget(self.content_input)

        # Image URL input (for image slides)
        self.image_url_label = QLabel("Image URL:")
        self.image_url_input = QLineEdit()
        self.editor_layout.addWidget(self.image_url_label)
        self.editor_layout.addWidget(self.image_url_input)

        # Quiz options input (for quiz slides)
        self.quiz_options_label = QLabel("Quiz Options (one per line):")
        self.quiz_options_input = QTextEdit()
        self.editor_layout.addWidget(self.quiz_options_label)
        self.editor_layout.addWidget(self.quiz_options_input)

        # Buttons
        self.add_slide_button = QPushButton("Add Slide")
        self.add_slide_button.clicked.connect(self.add_slide)
        self.editor_layout.addWidget(self.add_slide_button)

        self.save_button = QPushButton("Save to JSON")
        self.save_button.clicked.connect(self.save_to_json)
        self.editor_layout.addWidget(self.save_button)

        self.import_button = QPushButton("Import JSON")
        self.import_button.clicked.connect(self.import_json)
        self.editor_layout.addWidget(self.import_button)

        # Add editor widget to the main layout
        self.layout.addWidget(self.editor_widget)

        # Data storage
        self.slides = []

    def add_slide(self):
        """Add a new slide based on the selected type."""
        slide_type = None
        if self.text_radio.isChecked():
            slide_type = "text"
        elif self.image_radio.isChecked():
            slide_type = "image"
        elif self.quiz_radio.isChecked():
            slide_type = "quiz"

        if not slide_type:
            QMessageBox.warning(self, "Error", "Please select a slide type.")
            return

        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Error", "Please enter a title.")
            return

        slide = {"type": slide_type, "title": title}

        if slide_type == "text":
            content = self.content_input.toPlainText().strip()
            if not content:
                QMessageBox.warning(self, "Error", "Please enter content.")
                return
            slide["content"] = content

        elif slide_type == "image":
            image_url = self.image_url_input.text().strip()
            if not image_url:
                QMessageBox.warning(self, "Error", "Please enter an image URL.")
                return
            slide["url"] = image_url
            slide["alt"] = "Image"

        elif slide_type == "quiz":
            question = self.content_input.toPlainText().strip()
            if not question:
                QMessageBox.warning(self, "Error", "Please enter a question.")
                return
            options = self.quiz_options_input.toPlainText().strip().split("\n")
            if len(options) < 2:
                QMessageBox.warning(self, "Error", "Please enter at least two quiz options.")
                return
            slide["question"] = question
            slide["options"] = options

        self.slides.append(slide)
        self.update_slide_list()
        self.clear_editor()

    def load_slide_for_editing(self, item):
        """Load a slide into the editor for editing."""
        index = self.slide_list.row(item)
        slide = self.slides[index]

        self.title_input.setText(slide["title"])

        if slide["type"] == "text":
            self.text_radio.setChecked(True)
            self.content_input.setPlainText(slide["content"])
            self.image_url_input.clear()
            self.quiz_options_input.clear()

        elif slide["type"] == "image":
            self.image_radio.setChecked(True)
            self.image_url_input.setText(slide["url"])
            self.content_input.clear()
            self.quiz_options_input.clear()

        elif slide["type"] == "quiz":
            self.quiz_radio.setChecked(True)
            self.content_input.setPlainText(slide["question"])
            self.quiz_options_input.setPlainText("\n".join(slide["options"]))
            self.image_url_input.clear()

    def update_slide_list(self):
        """Update the slide list widget."""
        self.slide_list.clear()
        for slide in self.slides:
            self.slide_list.addItem(f"{slide['type'].capitalize()}: {slide['title']}")

    def clear_editor(self):
        """Clear the editor inputs."""
        self.title_input.clear()
        self.content_input.clear()
        self.image_url_input.clear()
        self.quiz_options_input.clear()

    def save_to_json(self):
        """Save the slides to a JSON file."""
        if not self.slides:
            QMessageBox.warning(self, "Error", "No slides to save.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save JSON", "", "JSON Files (*.json)")
        if file_path:
            with open(file_path, "w") as f:
                json.dump({"slides": self.slides}, f, indent=4)
            QMessageBox.information(self, "Success", "Slides saved successfully!")

    def import_json(self):
        """Import slides from a JSON file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Import JSON", "", "JSON Files (*.json)")
        if file_path:
            with open(file_path, "r") as f:
                data = json.load(f)
                self.slides = data.get("slides", [])
                self.update_slide_list()
            QMessageBox.information(self, "Success", "Slides imported successfully!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SlideEditor()
    window.show()
    sys.exit(app.exec_())
