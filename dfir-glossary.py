#!/usr/bin/env python3

import sys
import sqlite3
import csv
import warnings
import os
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QLineEdit,
    QTableView,
    QTextEdit,
    QPushButton,
    QHeaderView,
    QMessageBox,
    QDialog,
    QFormLayout,
    QStyle,
    QMenu,
    QAbstractItemView,
)
from PyQt6.QtGui import (
    QStandardItemModel,
    QStandardItem,
    QFocusEvent,
    QKeySequence,
)
from PyQt6.QtCore import Qt

warnings.filterwarnings("ignore", category=DeprecationWarning)
__version__ = "1.0.0"
__appname__ = f"DFIR Glossary v{__version__}"
__checked__ = False


class SearchLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.placeholder = "Search all terms and definitions..."
        self.setPlaceholderText(self.placeholder)
        self.update()

    def focusInEvent(self, event: QFocusEvent):
        if self.placeholderText() == self.placeholder:
            self.setPlaceholderText("")
        super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent):
        if not self.text():
            self.setPlaceholderText(self.placeholder)
        super().focusOutEvent(event)


class GlossaryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.loadData()
        self.checked_ids = set()
        style = self.style()
        dialog_icon = style.standardIcon(
            QStyle.StandardPixmap.SP_FileDialogDetailedView
        )
        self.setWindowIcon(dialog_icon)

    def initUI(self):
        self.setWindowTitle(__appname__)
        self.setFixedSize(800, 500)
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        self.search_bar = SearchLineEdit()
        self.search_bar.setPlaceholderText("Search all terms and definitions...")
        self.search_bar.textChanged.connect(self.search)
        self.clear_search_button = QPushButton()
        self.clear_search_button.clicked.connect(self.clear_search)
        self.clear_search_button.setToolTip("Clear Search")
        style = self.clear_search_button.style()
        clear_icon = style.standardIcon(QStyle.StandardPixmap.SP_TrashIcon)
        self.clear_search_button.setIcon(clear_icon)
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(self.clear_search_button)
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectItems)
        self.table_view.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
        self.table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.contextMenu = ContextMenu(self.table_view)
        self.table_view.customContextMenuRequested.connect(
            self.contextMenu.show_context_menu
        )
        self.definition_display = QTextEdit()
        self.definition_display.setReadOnly(True)
        self.export_button = QPushButton("Export Selected Terms")
        self.table_view.verticalHeader().setVisible(False)
        self.add_button = QPushButton()
        self.add_button.clicked.connect(self.add_term)
        self.add_button.setToolTip("Add Term")
        style = self.add_button.style()
        add_icon = style.standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder)
        self.add_button.setIcon(add_icon)
        self.remove_button = QPushButton()
        self.remove_button.clicked.connect(self.remove_terms)
        self.remove_button.setToolTip("Remove Selected Terms")
        style = self.remove_button.style()
        remove_icon = style.standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton)
        self.remove_button.setIcon(remove_icon)
        self.select_deselect_button = QPushButton()
        self.select_deselect_button.clicked.connect(self.select_deselect)
        self.select_deselect_button.setToolTip("Select / Deselect All")
        style = self.select_deselect_button.style()
        sel_des_icon = style.standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton)
        self.select_deselect_button.setIcon(sel_des_icon)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.select_deselect_button)
        button_layout.addStretch(1)
        button_layout.addWidget(self.export_button)

        layout = QVBoxLayout()
        layout.addLayout(search_layout)
        layout.addWidget(self.table_view)
        layout.addWidget(self.definition_display)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.table_view.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.model = QStandardItemModel()
        self.table_view.setModel(self.model)
        self.model.setSortRole(Qt.ItemDataRole.DisplayRole)

        self.table_view.setSortingEnabled(True)
        self.table_view.clicked.connect(self.display_definition)
        self.export_button.clicked.connect(self.export_selected)
        self.restore_placeholder()
        if getattr(sys, "frozen", False):
            self.current_path = os.path.dirname(sys.executable)
        else:
            self.current_path = os.path.dirname(os.path.abspath(__file__))

    def clear_placeholder(self):
        if self.search_bar.placeholderText():
            self.search_bar.setPlaceholderText("")

    def restore_placeholder(self):
        if not self.search_bar.text():
            self.search_bar.setPlaceholderText("Search all terms and definitions...")

    def clear_search(self):
        self.search_bar.clear()
        self.restore_placeholder()

    def loadData(self):
        try:
            db_path = os.path.join(self.current_path, "glossdb.sqlite")
            if not os.path.exists(db_path):
                QMessageBox.critical(
                    self,
                    "Database Error",
                    f"The glossdb.sqlite database cannot be found at {db_path}.\n\nPlease make sure it exists, and if it does not, you can download an updated copy from https://github.com/digitalsleuth/dfir-glossary",
                )
                sys.exit(1)
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, term, definition, source FROM glossary")
            data = cursor.fetchall()
            conn.close()
            self.model.setHorizontalHeaderLabels(["Term", "Definition", "Source"])
            for row_index, row_data in enumerate(data):
                try:
                    term_id = int(row_data[0]) if row_data[0] is not None else 0
                    term = str(row_data[1]) if row_data[1] is not None else ""
                    definition = str(row_data[2]) if row_data[2] is not None else ""
                    source = str(row_data[3]) if row_data[3] is not None else ""
                    term_item = QStandardItem(term)
                    term_item.setCheckable(True)
                    term_item.setEditable(False)
                    self.model.setItem(row_index, 0, term_item)
                    definition_item = QStandardItem(definition)
                    definition_item.setEditable(False)
                    self.model.setItem(row_index, 1, definition_item)
                    source_item = QStandardItem(source)
                    source_item.setEditable(False)
                    self.model.setItem(row_index, 2, source_item)
                    term_item.setData(term_id, Qt.ItemDataRole.UserRole)
                except (ValueError, TypeError) as e:
                    QMessageBox.critical(
                        self, "Data Error", f"Error processing row {row_index}: {e}"
                    )
                    return
            self.table_view.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch
            )
            self.table_view.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        except sqlite3.Error as e:
            QMessageBox.critical(
                self, "Database Error", f"Error connecting to database: {e}"
            )

    def search(self, text):
        self.model.setRowCount(0)
        conn = sqlite3.connect(os.path.join(self.current_path, "glossdb.sqlite"))
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, term, definition, source FROM glossary WHERE term LIKE ? OR definition LIKE ?",
            ("%" + text + "%", "%" + text + "%"),
        )
        data = cursor.fetchall()
        conn.close()

        for row_index, row_data in enumerate(data):
            term_item = QStandardItem(row_data[1])
            term_item.setCheckable(True)
            term_item.setEditable(False)
            if row_data[0] in self.checked_ids:
                term_item.setCheckState(Qt.CheckState.Checked)
            self.model.setItem(row_index, 0, term_item)
            definition_item = QStandardItem(row_data[2])
            definition_item.setEditable(False)
            self.model.setItem(row_index, 1, definition_item)
            source_item = QStandardItem(row_data[3])
            source_item.setEditable(False)
            self.model.setItem(row_index, 2, source_item)
            term_item.setData(row_data[0], Qt.ItemDataRole.UserRole)

    def select_all(self):
        global __checked__
        for row in range(self.model.rowCount()):
            item = self.model.item(row, 0)
            if item:
                item.setCheckState(Qt.CheckState.Checked)
                self.checked_ids.add(item.data(Qt.ItemDataRole.UserRole))
                __checked__ = True

    def deselect_all(self):
        global __checked__
        for row in range(self.model.rowCount()):
            item = self.model.item(row, 0)
            if item:
                item.setCheckState(Qt.CheckState.Unchecked)
                self.checked_ids.discard(item.data(Qt.ItemDataRole.UserRole))
                __checked__ = False

    def select_deselect(self):
        #global __checked__
        if __checked__:
            self.deselect_all()
        else:
            self.select_all()

    def display_definition(self, index):
        term_index = index.row()
        column = index.column()

        term_item = self.model.item(term_index, 0)
        term_text = term_item.text()
        term_id = term_item.data(Qt.ItemDataRole.UserRole)
        definition_item = self.model.item(term_index, 1)
        source_item = self.model.item(term_index, 2)
        if term_item.checkState() == Qt.CheckState.Checked:
            self.checked_ids.add(term_id)
        else:
            self.checked_ids.discard(term_id)
        self.definition_display.setText(
            f"{term_item.text()}\n\n{definition_item.text()}\n\n{source_item.text()}"
        )

    def export_selected(self):
        try:
            if self.checked_ids:
                output_file, _ = QFileDialog.getOpenFileName(
                    self,
                    "Select output file",
                    "",
                    "csv Files (*.csv)",
                )
                if output_file:
                    with open(
                        output_file, "w", newline="", encoding="utf-8"
                    ) as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(["Term", "Definition", "Source"])
                        conn = sqlite3.connect(
                            os.path.join(self.current_path, "glossdb.sqlite")
                        )
                        cursor = conn.cursor()
                        for term_id in self.checked_ids:
                            cursor.execute(
                                "SELECT term, definition, source FROM glossary WHERE id = ?",
                                (term_id,),
                            )
                            result = cursor.fetchone()
                            if result:
                                writer.writerow(result)
                        conn.close()
                    QMessageBox.information(
                        self, "Export", "Terms exported successfully!"
                    )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def add_term(self):
        dialog = AddTermDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            term, definition, source = dialog.get_term_data()
            conn = sqlite3.connect(os.path.join(self.current_path, "glossdb.sqlite"))
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO glossary (term, definition, source) VALUES (?, ?, ?)",
                (term, definition, source),
            )
            conn.commit()
            conn.close()
            self.loadData()

    def remove_terms(self):
        if not self.checked_ids:
            return
        conn = sqlite3.connect(os.path.join(self.current_path, "glossdb.sqlite"))
        cursor = conn.cursor()
        for index in reversed(sorted(self.checked_ids)):
            cursor.execute("DELETE FROM glossary WHERE id = ?", (index,))
            self.model.removeRow(index)
        conn.commit()
        conn.close()
        self.checked_ids.clear()
        self.loadData()


class ContextMenu:

    def __init__(self, tbl_view):
        self.tbl_view = tbl_view

    def show_context_menu(self, pos):
        context_menu = QMenu(self.tbl_view)
        copy_event = context_menu.addAction("Copy")
        copy_event.setShortcut(QKeySequence("Ctrl+C"))
        copy_event.setShortcutVisibleInContextMenu(True)
        copy_event.triggered.connect(self.copy)
        select_event = context_menu.addAction("Select")
        select_event.setShortcut(QKeySequence("Ctrl+S"))
        select_event.setShortcutVisibleInContextMenu(True)
        select_event.triggered.connect(self.select)
        deselect_event = context_menu.addAction("Deselect")
        deselect_event.setShortcut(QKeySequence("Ctrl+D"))
        deselect_event.setShortcutVisibleInContextMenu(True)
        deselect_event.triggered.connect(self.deselect)
        context_menu.exec(self.tbl_view.mapToGlobal(pos))

    def copy(self):
        selected_indexes = self.tbl_view.selectionModel().selectedIndexes()
        if selected_indexes:
            selected_items_by_row = {}
            for index in selected_indexes:
                row = index.row()
                if row not in selected_items_by_row:
                    selected_items_by_row[row] = []
                selected_items_by_row[row].append(index)

            clipboard_text = ""
            for row in sorted(selected_items_by_row.keys()):
                row_data = []
                for index in sorted(
                    selected_items_by_row[row], key=lambda idx: idx.column()
                ):
                    model = self.tbl_view.model()
                    if model:
                        data = model.data(index)
                        row_data.append(str(data) if data is not None else "")
                clipboard_text += "\t".join(row_data) + "\n"

            clipboard = QApplication.clipboard()
            clipboard.setText(clipboard_text.rstrip("\n"))

    def select(self):
        self._set_checkbox_state(Qt.CheckState.Checked)

    def deselect(self):
        self._set_checkbox_state(Qt.CheckState.Unchecked)

    def _set_checkbox_state(self, check_state):
        selection_model = self.tbl_view.selectionModel()
        selected_indexes = selection_model.selectedIndexes()
        selected_rows = {index.row() for index in selected_indexes}
        checkbox_column = 0
        model = self.tbl_view.model()
        if model:
            for row in selected_rows:
                index = model.index(row, checkbox_column)
                model.setData(index, check_state, Qt.ItemDataRole.CheckStateRole)        


class AddTermDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Term")
        layout = QFormLayout()
        self.term_edit = QLineEdit()
        self.definition_edit = QTextEdit()
        self.source_edit = QLineEdit()
        self.definition_edit.setFixedHeight(self.term_edit.sizeHint().height() * 3)

        layout.addRow("Term:", self.term_edit)
        layout.addRow("Definition:", self.definition_edit)
        layout.addRow("Source:", self.source_edit)

        buttons = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)

        layout.addRow(buttons)
        self.setLayout(layout)

    def get_term_data(self):
        return (
            self.term_edit.text(),
            self.definition_edit.toPlainText(),
            self.source_edit.text(),
        )


def main():
    app = QApplication([__appname__, "windows:darkmode=2"])
    app.setStyle("Fusion")
    window = GlossaryApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
