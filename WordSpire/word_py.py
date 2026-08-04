import sys
import os
from docx import Document
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QFormLayout
)
from PyQt6.QtCore import Qt


class WordMetadataEditorDocx(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file_path = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Word 文档属性与文件名管理工具")
        self.resize(550, 450)

        # 主部件与布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # ---- 第一部分：文件选择 ----
        file_layout = QHBoxLayout()
        self.file_label = QLineEdit()
        self.file_label.setPlaceholderText("请选择或拖入 Word 文档...")
        self.file_label.setReadOnly(True)

        btn_browse = QPushButton("浏览...")
        btn_browse.clicked.connect(self.open_file_dialog)

        file_layout.addWidget(self.file_label)
        file_layout.addWidget(btn_browse)
        main_layout.addLayout(file_layout)

        # ---- 第二部分：文件名修改 (新功能) ----
        filename_layout = QHBoxLayout()
        filename_layout.addWidget(QLabel("文件名称:"))
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("无需输入 .docx 后缀")
        self.filename_input.setEnabled(False)
        filename_layout.addWidget(self.filename_input)
        main_layout.addLayout(filename_layout)

        # ---- 第三部分：内置属性表单 ----
        form_widget = QWidget()
        self.form_layout = QFormLayout(form_widget)

        self.inputs = {}
        self.builtin_fields = {
            "title": "标题 (Title):",
            "author": "作者 (Author):",
            "subject": "主题 (Subject):",
            "keywords": "关键字 (Keywords):",
            "comments": "备注 (Comments):"
        }

        for key, label_text in self.builtin_fields.items():
            self.inputs[key] = QLineEdit()
            self.inputs[key].setEnabled(False)
            self.form_layout.addRow(QLabel(label_text), self.inputs[key])

        main_layout.addWidget(form_widget)

        # ---- 第四部分：操作按钮 ----
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("保存所有修改 (含文件名)")
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self.save_metadata_and_rename)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_save)
        main_layout.addLayout(btn_layout)

        # 支持拖拽文件
        self.setAcceptDrops(True)

    # ---- 拖拽事件处理 ----
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith('.docx'):
                self.load_word_metadata(file_path)
                break
            elif file_path.lower().endswith('.doc'):
                QMessageBox.warning(self, "提示", "仅支持 .docx 格式。")

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 Word 文档", "", "Word Files (*.docx)"
        )
        if file_path:
            self.load_word_metadata(file_path)

    # ---- 加载文档与属性 ----
    def load_word_metadata(self, file_path):
        self.current_file_path = os.path.abspath(file_path)
        self.file_label.setText(self.current_file_path)

        # 提取当前的文件名（不含路径和扩展名）展示在输入框中
        base_name = os.path.basename(self.current_file_path)
        name_without_ext, _ = os.path.splitext(base_name)
        self.filename_input.setText(name_without_ext)
        self.filename_input.setEnabled(True)

        try:
            doc = Document(self.current_file_path)
            props = doc.core_properties

            # 填充元数据
            self.inputs["title"].setText(props.title or "")
            self.inputs["author"].setText(props.author or "")
            self.inputs["subject"].setText(props.subject or "")
            self.inputs["keywords"].setText(props.keywords or "")
            self.inputs["comments"].setText(props.comments or "")

            # 启用输入和保存
            for input_field in self.inputs.values():
                input_field.setEnabled(True)
            self.btn_save.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法读取文档属性:\n{str(e)}")

    # ---- 保存修改 (保存属性 + 重命名文件) ----
    def save_metadata_and_rename(self):
        if not self.current_file_path:
            return

        # 1. 验证文件名中是否有非法字符
        new_name = self.filename_input.text().strip()
        if not new_name:
            QMessageBox.warning(self, "警告", "文件名不能为空！")
            return

        invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
        if any(char in new_name for char in invalid_chars):
            QMessageBox.warning(self, "警告", '文件名不能包含以下字符: \\ / : * ? " < > |')
            return

        try:
            # 2. 先保存 Word 文档内部属性
            doc = Document(self.current_file_path)
            props = doc.core_properties

            props.title = self.inputs["title"].text()
            props.author = self.inputs["author"].text()
            props.subject = self.inputs["subject"].text()
            props.keywords = self.inputs["keywords"].text()
            props.comments = self.inputs["comments"].text()

            doc.save(self.current_file_path)

            # 3. 再执行物理文件重命名
            directory = os.path.dirname(self.current_file_path)
            new_file_path = os.path.join(directory, f"{new_name}.docx")

            # 如果文件名确实发生了改变，则执行重命名
            if new_file_path != self.current_file_path:
                # 检查新文件名是否已经存在
                if os.path.exists(new_file_path):
                    QMessageBox.warning(self, "警告", "该目录下已存在同名文件，无法重命名！")
                    return

                os.rename(self.current_file_path, new_file_path)
                # 更新当前保存的路径变量
                self.current_file_path = new_file_path
                self.file_label.setText(self.current_file_path)

            QMessageBox.information(self, "成功", "文档属性及文件名已成功更新！")

        except PermissionError:
            QMessageBox.warning(
                self, "保存失败", "无法修改文件！请确保该 Word 文档目前没有被 Word 软件打开。")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败:\n{str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = WordMetadataEditorDocx()
    editor.show()
    sys.exit(app.exec())
