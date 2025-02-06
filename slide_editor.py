import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QLabel, QLineEdit, QTextEdit, QListWidget, QListWidgetItem,
    QFileDialog, QMessageBox, QInputDialog, QStackedWidget, QDialog, QScrollArea
)
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QIcon

class SlideEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Natural Bonds Editor")
        self.setGeometry(100, 100, 1200, 800)
        self.slides = []
        self.current_slide_index = -1

        # Main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # Slide list panel
        self.slide_list = QListWidget()
        self.slide_list.setDragDropMode(QListWidget.InternalMove)
        self.slide_list.setMinimumWidth(250)
        self.slide_list.itemClicked.connect(self.load_slide)
        self.slide_list.model().rowsMoved.connect(self.reorder_slides)
        layout.addWidget(self.slide_list)

        # Slide editing panel
        self.editor_stack = QStackedWidget()
        self.create_editors()
        layout.addWidget(self.editor_stack, 1)

        # Toolbar
        toolbar = self.addToolBar("Main")
        toolbar.addAction(QIcon(":file-new.svg"), "New", self.new_file)
        toolbar.addAction(QIcon(":file-open.svg"), "Open", self.open_file)
        toolbar.addAction(QIcon(":file-save.svg"), "Save", self.save_file)
        toolbar.addSeparator()
        toolbar.addAction(QIcon(":add.svg"), "Add Slide", self.add_slide_dialog)
        toolbar.addAction(QIcon(":remove.svg"), "Remove Slide", self.remove_slide)

    def create_editors(self):
        # Text Slide Editor
        text_editor = QWidget()
        text_layout = QVBoxLayout(text_editor)
        self.text_title = QLineEdit()
        self.text_content = QTextEdit()
        text_layout.addWidget(QLabel("Title:"))
        text_layout.addWidget(self.text_title)
        text_layout.addWidget(QLabel("Content (HTML allowed):"))
        text_layout.addWidget(self.text_content)
        self.editor_stack.addWidget(text_editor)

        # Image Slide Editor
        image_editor = QWidget()
        image_layout = QVBoxLayout(image_editor)
        self.image_title = QLineEdit()
        self.image_url = QLineEdit()
        self.image_alt = QLineEdit()
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_image)
        image_layout.addWidget(QLabel("Title:"))
        image_layout.addWidget(self.image_title)
        image_layout.addWidget(QLabel("Image URL:"))
        image_layout.addWidget(self.image_url)
        image_layout.addWidget(browse_btn)
        image_layout.addWidget(QLabel("Alt Text:"))
        image_layout.addWidget(self.image_alt)
        self.editor_stack.addWidget(image_editor)

        # Quiz Slide Editor
        quiz_editor = QWidget()
        quiz_layout = QVBoxLayout(quiz_editor)
        self.quiz_title = QLineEdit()
        self.quiz_question = QTextEdit()
        self.quiz_options = QListWidget()
        self.quiz_options.setDragDropMode(QListWidget.InternalMove)
        add_option_btn = QPushButton("Add Option")
        add_option_btn.clicked.connect(self.add_quiz_option)
        remove_option_btn = QPushButton("Remove Selected")
        remove_option_btn.clicked.connect(self.remove_quiz_option)
        quiz_layout.addWidget(QLabel("Title:"))
        quiz_layout.addWidget(self.quiz_title)
        quiz_layout.addWidget(QLabel("Question:"))
        quiz_layout.addWidget(self.quiz_question)
        quiz_layout.addWidget(QLabel("Options:"))
        quiz_layout.addWidget(self.quiz_options)
        quiz_layout.addWidget(add_option_btn)
        quiz_layout.addWidget(remove_option_btn)
        self.editor_stack.addWidget(quiz_editor)

    def add_slide_dialog(self):
        types = ["Text", "Image", "Quiz"]
        slide_type, ok = QInputDialog.getItem(
            self, "Add Slide", "Select slide type:", types, 0, False
        )
        if ok and slide_type:
            self.add_slide(slide_type.lower())

    def add_slide(self, slide_type):
        slide = {"type": slide_type}
        if slide_type == "text":
            slide.update({
                "title": "New Text Slide",
                "content": "Enter your content here"
            })
        elif slide_type == "image":
            slide.update({
                "title": "New Image Slide",
                "url": "",
                "alt": ""
            })
        elif slide_type == "quiz":
            slide.update({
                "title": "New Quiz Slide",
                "question": "Enter your question",
                "options": []
            })
        
        self.slides.append(slide)
        item = QListWidgetItem(slide["title"])
        item.setData(Qt.UserRole, len(self.slides)-1)
        self.slide_list.addItem(item)
        self.slide_list.setCurrentItem(item)
        self.load_slide(item)

    def load_slide(self, item):
        self.current_slide_index = item.data(Qt.UserRole)
        slide = self.slides[self.current_slide_index]
        
        if slide["type"] == "text":
            self.text_title.setText(slide.get("title", ""))
            self.text_content.setPlainText(slide.get("content", ""))
            self.editor_stack.setCurrentIndex(0)
        elif slide["type"] == "image":
            self.image_title.setText(slide.get("title", ""))
            self.image_url.setText(slide.get("url", ""))
            self.image_alt.setText(slide.get("alt", ""))
            self.editor_stack.setCurrentIndex(1)
        elif slide["type"] == "quiz":
            self.quiz_title.setText(slide.get("title", ""))
            self.quiz_question.setPlainText(slide.get("question", ""))
            self.quiz_options.clear()
            self.quiz_options.addItems(slide.get("options", []))
            self.editor_stack.setCurrentIndex(2)

    def save_current_slide(self):
        if self.current_slide_index == -1:
            return
            
        slide = self.slides[self.current_slide_index]
        if slide["type"] == "text":
            slide["title"] = self.text_title.text()
            slide["content"] = self.text_content.toPlainText()
        elif slide["type"] == "image":
            slide["title"] = self.image_title.text()
            slide["url"] = self.image_url.text()
            slide["alt"] = self.image_alt.text()
        elif slide["type"] == "quiz":
            slide["title"] = self.quiz_title.text()
            slide["question"] = self.quiz_question.toPlainText()
            slide["options"] = [
                self.quiz_options.item(i).text() 
                for i in range(self.quiz_options.count())
            ]
        
        self.slide_list.currentItem().setText(slide["title"])

    def reorder_slides(self):
        new_order = []
        for i in range(self.slide_list.count()):
            index = self.slide_list.item(i).data(Qt.UserRole)
            new_order.append(self.slides[index])
        self.slides = new_order
        for i in range(self.slide_list.count()):
            self.slide_list.item(i).setData(Qt.UserRole, i)

    def add_quiz_option(self):
        text, ok = QInputDialog.getText(self, "Add Option", "Enter option text:")
        if ok and text:
            self.quiz_options.addItem(text)
            self.save_current_slide()

    def remove_quiz_option(self):
        row = self.quiz_options.currentRow()
        if row >= 0:
            self.quiz_options.takeItem(row)
            self.save_current_slide()

    def browse_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg)"
        )
        if path:
            self.image_url.setText(path)
            self.save_current_slide()

    def new_file(self):
        self.slides = []
        self.slide_list.clear()
        self.current_slide_index = -1

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Presentation", "", "JSON Files (*.json)"
        )
        if path:
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    self.slides = data.get("slides", [])
                    self.slide_list.clear()
                    for i, slide in enumerate(self.slides):
                        item = QListWidgetItem(slide.get("title", "Untitled"))
                        item.setData(Qt.UserRole, i)
                        self.slide_list.addItem(item)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")

    def save_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Presentation", "", "JSON Files (*.json)"
        )
        if path:
            self.save_current_slide()
            try:
                with open(path, "w") as f:
                    json.dump({"slides": self.slides}, f, indent=2)
                QMessageBox.information(self, "Success", "File saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")

    def remove_slide(self):
        row = self.slide_list.currentRow()
        if row >= 0:
            self.slide_list.takeItem(row)
            del self.slides[row]
            for i in range(row, self.slide_list.count()):
                self.slide_list.item(i).setData(Qt.UserRole, i)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SlideEditor()
    window.show()
    sys.exit(app.exec_())
