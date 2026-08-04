import sys
import os
import win32com.client
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QFormLayout,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt

class WordMetadataEditorWin32(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file_path = None
        self.word_app = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Word 文档属性管理工具 (PyWin32 版)")
        self.resize(600, 500)

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

        # ---- 第二部分：内置属性表单 ----
        form_widget = QWidget()
        self.form_layout = QFormLayout(form_widget)
        
        # 定义常用的内置属性
        self.inputs = {}
        self.builtin_fields = {
            "Title": "标题 (Title):",
            "Author": "作者 (Author):",
            "Subject": "主题 (Subject):",
            "Keywords": "关键字 (Keywords):",
            "Comments": "备注 (Comments):"
        }
        
        for key, label_text in self.builtin_fields.items():
            self.inputs[key] = QLineEdit()
            self.inputs[key].setEnabled(False)
            self.form_layout.addRow(QLabel(label_text), self.inputs[key])
            
        main_layout.addWidget(form_widget)

        # ---- 第三部分：自定义属性表格 ----
        custom_label = QLabel("自定义属性 (Custom Properties):")
        custom_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        main_layout.addWidget(custom_label)

        self.custom_table = QTableWidget(0, 2)
        self.custom_table.setHorizontalHeaderLabels(["属性名", "属性值"])
        self.custom_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.custom_table.setEnabled(False)
        main_layout.addWidget(self.custom_table)

        # 自定义属性控制按钮
        custom_btn_layout = QHBoxLayout()
        self.btn_add_prop = QPushButton("添加属性")
        self.btn_add_prop.setEnabled(False)
        self.btn_add_prop.clicked.connect(self.add_custom_row)
        
        self.btn_del_prop = QPushButton("删除选中行")
        self.btn_del_prop.setEnabled(False)
        self.btn_del_prop.clicked.connect(self.delete_custom_row)
        
        custom_btn_layout.addWidget(self.btn_add_prop)
        custom_btn_layout.addWidget(self.btn_del_prop)
        custom_btn_layout.addStretch()
        main_layout.addLayout(custom_btn_layout)

        # ---- 第四部分：操作按钮 ----
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("保存修改")
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self.save_metadata)
        
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
            if file_path.lower().endswith(('.doc', '.docx')):
                self.load_word_metadata(file_path)
                break

    # ---- 文件加载与读取 ----
    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 Word 文档", "", "Word Files (*.docx *.doc)"
        )
        if file_path:
            self.load_word_metadata(file_path)

    def load_word_metadata(self, file_path):
        self.current_file_path = os.path.abspath(file_path)
        self.file_label.setText(self.current_file_path)
        
        # 禁用界面，避免加载时操作
        self.set_ui_enabled(False)
        
        try:
            # 启动或连接 Word
            if not self.word_app:
                # 使用 DispatchEx 确保启动独立的后台进程，不干扰用户已打开的 Word
                self.word_app = win32com.client.DispatchEx("Word.Application")
                self.word_app.Visible = False
                self.word_app.DisplayAlerts = False
            
            # 打开文档
            doc = self.word_app.Documents.Open(self.current_file_path)
            
            # 1. 读取内置属性
            builtin_props = doc.BuiltInDocumentProperties
            for key in self.builtin_fields.keys():
                try:
                    val = builtin_props(key).Value
                    self.inputs[key].setText(str(val) if val is not None else "")
                except Exception:
                    self.inputs[key].setText("")

            # 2. 读取自定义属性
            custom_props = doc.CustomDocumentProperties
            self.custom_table.setRowCount(0)
            for prop in custom_props:
                row_position = self.custom_table.rowCount()
                self.custom_table.insertRow(row_position)
                
                # 填充键
                key_item = QTableWidgetItem(prop.Name)
                # 填充值
                try:
                    val_item = QTableWidgetItem(str(prop.Value))
                except Exception:
                    val_item = QTableWidgetItem("")
                
                self.custom_table.setItem(row_position, 0, key_item)
                self.custom_table.setItem(row_position, 1, val_item)

            # 关闭文档，不保存更改（仅作读取）
            doc.Close(SaveChanges=0)
            
            # 启用相关控件
            self.set_ui_enabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存文档属性失败: {str(e)}")
            if self.word_app:
                try:
                    self.word_app.Quit()
                except Exception:
                    pass
                self.word_app = None

    def set_ui_enabled(self, enabled):
        for input_field in self.inputs.values():
            input_field.setEnabled(enabled)
        self.custom_table.setEnabled(enabled)
        self.btn_add_prop.setEnabled(enabled)
        self.btn_del_prop.setEnabled(enabled)
        self.btn_save.setEnabled(enabled)

    # ---- 自定义属性表格操作 ----
    def add_custom_row(self):
        row_position = self.custom_table.rowCount()
        self.custom_table.insertRow(row_position)
        self.custom_table.setItem(row_position, 0, QTableWidgetItem("新属性名"))
        self.custom_table.setItem(row_position, 1, QTableWidgetItem("新属性值"))

    def delete_custom_row(self):
        current_row = self.custom_table.currentRow()
        if current_row >= 0:
            self.custom_table.removeRow(current_row)
        else:
            QMessageBox.warning(self, "提示", "请先在表格中选中要删除的行。")

    # ---- 保存属性修改 ----
    def save_metadata(self):
        if not self.current_file_path or not self.word_app:
            return
            
        try:
            # 重新打开文档以便写入
            doc = self.word_app.Documents.Open(self.current_file_path)
            
            # 1. 保存内置属性
            builtin_props = doc.BuiltInDocumentProperties
            for key in self.builtin_fields.keys():
                try:
                    builtin_props(key).Value = self.inputs[key].text()
                except Exception as e:
                    print(f"写入内置属性 {key} 失败: {e}")

            # 2. 保存自定义属性
            custom_props = doc.CustomDocumentProperties
            
            # 先收集界面上的自定义属性
            ui_custom_props = {}
            for row in range(self.custom_table.rowCount()):
                key_item = self.custom_table.item(row, 0)
                val_item = self.custom_table.item(row, 1)
                if key_item and key_item.text().strip():
                    ui_custom_props[key_item.text().strip()] = val_item.text() if val_item else ""

            # 删除文档中存在但界面上已经被删掉的自定义属性
            existing_names = [prop.Name for prop in custom_props]
            for name in existing_names:
                if name not in ui_custom_props:
                    try:
                        custom_props(name).Delete()
                    except Exception:
                        pass

            # 写入或更新自定义属性
            for name, value in ui_custom_props.items():
                try:
                    # 尝试直接修改
                    custom_props(name).Value = value
                except Exception:
                    # 如果不存在，则新增 (4 代表 msoPropertyTypeString 文本类型)
                    try:
                        custom_props.Add(name, False, 4, value)
                    except Exception as e:
                        print(f"添加自定义属性 {name} 失败: {e}")

            # 保存并关闭
            doc.Save()
            doc.Close(SaveChanges=-1) # wdSaveChanges = -1
            
            QMessageBox.information(self, "成功", "文档属性已成功更新并保存！")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存文档属性失败:{str(e)}")
            
    def closeEvent(self, event):
        # 窗口关闭时，确保退出后台 Word 进程
        if self.word_app:
            try:
                self.word_app.Quit()
            except Exception:
                pass
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = WordMetadataEditorWin32()
    editor.show()
    sys.exit(app.exec())
