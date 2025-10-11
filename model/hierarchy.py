"""
Code hierarchy model — lists functions/classes live from current script.
"""
import ast, os
from PySide6 import QtGui, QtCore, QtWidgets

class CodeHierarchyModel(QtGui.QStandardItemModel):
    FILE_ROLE = QtCore.Qt.UserRole + 1
    LINE_ROLE = QtCore.Qt.UserRole + 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalHeaderLabels(["Outline"])
        self.file_path = None

    def build_from_code(self, code: str, file_path="<memory>"):
        self.clear()
        self.setHorizontalHeaderLabels(["Outline"])
        self.file_path = file_path
        try:
            tree = ast.parse(code)
        except Exception:
            return
        root = self.invisibleRootItem()
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                it = QtGui.QStandardItem(f"def {node.name}()")
                it.setData(file_path, self.FILE_ROLE)
                it.setData(node.lineno, self.LINE_ROLE)
                root.appendRow(it)
            elif isinstance(node, ast.ClassDef):
                cit = QtGui.QStandardItem(f"class {node.name}")
                cit.setData(file_path, self.FILE_ROLE)
                cit.setData(node.lineno, self.LINE_ROLE)
                root.appendRow(cit)

    def attach_to_editor(self, editor):
        editor.textChanged.connect(lambda: self._update_from_editor(editor))

    def _update_from_editor(self, editor):
        code = editor.toPlainText()
        self.build_from_code(code, getattr(editor, "filePath", "<unsaved>"))
