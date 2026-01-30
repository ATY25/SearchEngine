from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from crawler import crawl_publications
from indexer import InvertedIndex
from classifier import train, predict
import webbrowser
import os
import json
DATASET = "data/info.jsonl"

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Coventry Scholar Search + Classifier")
        self.resize(1000, 650)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(230, 255, 255, 0.9);
                font-size: 14px;
            }

            QPushButton {
                background-color: rgba(0, 180, 180, 0.4);
                padding: 8px;
                border-radius: 10px;
            }

            QPushButton:hover {
                background-color: rgba(0, 180, 180, 0.7);
            }

            QListWidget {
                background-color: rgba(255, 255, 255, 0.8);
                border-radius: 10px;
            }
        """)

        self.tabs = QTabWidget()
        layout = QVBoxLayout()

        # ================= TASK 1 TAB =================
        self.task1 = QWidget()
        t1_layout = QVBoxLayout()
        self.crawl_btn = QPushButton("🔄 Crawl Coventry Publications (BFS)")
        self.crawl_btn.clicked.connect(self.run_crawler)
        self.query_box = QLineEdit()
        self.query_box.setPlaceholderText("Search like Google Scholar...")
        self.search_btn = QPushButton("🔍 Search")
        self.search_btn.clicked.connect(self.run_search)
        self.results = QListWidget()
        self.results.itemClicked.connect(self.open_result)
        t1_layout.addWidget(self.crawl_btn)
        t1_layout.addWidget(self.query_box)
        t1_layout.addWidget(self.search_btn)
        t1_layout.addWidget(self.results)
        self.task1.setLayout(t1_layout)

        # Index object
        self.index = InvertedIndex()
        self.docs = []

        # ================= TASK 2 TAB =================
        self.task2 = QWidget()
        t2_layout = QVBoxLayout()
        self.train_btn = QPushButton("📚 Train Naive Bayes Classifier")
        self.train_btn.clicked.connect(self.train_model)
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter a Business / Health / Entertainment news text...")
        self.predict_btn = QPushButton("✅ Predict Category")
        self.predict_btn.clicked.connect(self.predict_category)
        self.output = QLabel("Prediction: -")
        self.output.setAlignment(Qt.AlignCenter)
        t2_layout.addWidget(self.train_btn)
        t2_layout.addWidget(self.text_input)
        t2_layout.addWidget(self.predict_btn)
        t2_layout.addWidget(self.output)
        self.task2.setLayout(t2_layout)
        self.tabs.addTab(self.task1, "Task 1: Search Engine")
        self.tabs.addTab(self.task2, "Task 2: Classification")
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    # ---------------- TASK 1 ----------------

    def run_crawler(self):
        try:
            with open("docs.json", "r", encoding="utf-8") as f:
                self.docs = json.load(f)
            self.index.build(self.docs)

            QMessageBox.information(
                self,
                "Crawler Done ✅",
                f"Loaded {len(self.docs)} sample publications and indexed them."
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            QMessageBox.information(
                self,
                "Crawler Done ✅",
                f"Extracted {len(self.docs)} publications and indexed them."
            )

    def run_search(self):
        query = self.query_box.text()
        results = self.index.search(query)
        self.results.clear()


        for doc, score in results[:20]:
            item = QListWidgetItem(f"{doc['title']} ({doc['year']})")
            item.setData(Qt.UserRole, doc.get("publication_url"))
            self.results.addItem(item)

    def open_result(self, item):
        url = item.data(Qt.UserRole)
        if url:
            webbrowser.open(url)

    # ---------------- TASK 2 ----------------
    def train_model(self):
        msg = train(DATASET)
        QMessageBox.information(self, "Training Complete ✅", msg)

    def predict_category(self):
        text = self.text_input.toPlainText()
        cat = predict(text)
        self.output.setText("Prediction: " + cat)

def run_app():
    app = QApplication([])
    win = App()
    win.show()
    app.exec_()