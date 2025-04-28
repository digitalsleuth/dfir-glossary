#!/usr/bin/env python3

import sys
import sqlite3
import csv
import warnings
import os
import base64
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFileDialog,
    QLineEdit,
    QTableView,
    QTextEdit,
    QPushButton,
    QHeaderView,
    QMessageBox,
    QDialog,
    QFormLayout,
    QMenu,
    QLabel,
)
from PyQt6.QtGui import (
    QIcon,
    QPixmap,
    QStandardItemModel,
    QStandardItem,
    QFocusEvent,
    QKeySequence,
)
from PyQt6.QtCore import Qt, QModelIndex
from pytablericons import TablerIcons, OutlineIcon

warnings.filterwarnings("ignore", category=DeprecationWarning)
__version__ = "1.0.0"
__appname__ = f"DFIR Glossary v{__version__}"
__date__ = "2025-04-27"
__checked__ = False
__source__ = "https://github.com/digitalsleuth/dfir-glossary"
__author__ = "Corey Forman (digitalsleuth)"
__fingerprint__ = """
AAABAAIAMDAAAAEAIACoJQAAJgAAABAQAAABACAAaAQAAM4lAAAoAAAAMAAAAGAAAAABACAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAC9hGcXr4JvPgAAAAAAAAAAwoJYDrZ+V2qwgWEDAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAC/hGd/uIRsVgAAAAC9gmJPqH1n/Zp8bn+hh4UBwYBUH7N6UPCnelWY
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAMWKcAy+h29Juot5BQAAAAC/hGV7s4Bm+6t/aaGpgW4KpX1o
VpZ4ZfaReGaGAAAAALB7UUCjdk74nHdRcwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMOGajm7g2n3sIFt4KmB
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
"""


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
        self.initUi()
        self.db_path = os.path.join(self.current_path, "glossary.sqlite")
        self.load_data()
        self.app_icon = QIcon(
            TablerIcons.load(
                OutlineIcon.VOCABULARY, color="#1644b9", stroke_width=2
            ).toqpixmap()
        )
        self.setWindowIcon(self.app_icon)

    def initUi(self):
        self.setWindowTitle(__appname__)
        self.setFixedSize(800, 500)
        self.checked_ids = set()
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        self.x = (screen_geometry.width() - self.width()) // 2
        self.y = (screen_geometry.height() - self.height()) // 2
        self.move(self.x, self.y)
        self.search_bar = SearchLineEdit()
        self.search_bar.setPlaceholderText("Search all terms and definitions...")
        self.search_bar.textChanged.connect(self.search)
        self.clear_search_button = QPushButton()
        self.clear_search_button.clicked.connect(self.clear_search)
        self.clear_search_button.setToolTip("Clear Search")
        clear_icon = QIcon(
            TablerIcons.load(
                OutlineIcon.COPY_X, color="#923232", size=24, stroke_width=2,
            ).toqpixmap()
        )
        self.clear_search_button.setIcon(clear_icon)
        self.about_button = QPushButton()
        self.about_button.clicked.connect(self._about)
        self.about_button.setToolTip("About")
        about_icon = QIcon(
            TablerIcons.load(
                OutlineIcon.QUESTION_MARK, color="#1644b9", stroke_width=2
            ).toqpixmap()
        )
        self.about_button.setIcon(about_icon)
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(self.clear_search_button)
        search_layout.addWidget(self.about_button)
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectItems)
        self.table_view.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
        self.table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.contextMenu = ContextMenu(
            self.table_view, self.checked_ids, self.edit_term
        )
        self.table_view.customContextMenuRequested.connect(
            self.contextMenu.show_context_menu
        )
        self.table_view.doubleClicked.connect(self.double_click)
        self.definition_display = QTextEdit()
        self.definition_display.setReadOnly(True)
        self.export_button = QPushButton("Export Selected Terms")
        self.table_view.verticalHeader().setVisible(False)
        self.add_button = QPushButton()
        self.add_button.clicked.connect(self.add_term)
        self.add_button.setToolTip("Add Term")
        add_icon = TablerIcons.load(
            OutlineIcon.LIBRARY_PLUS, color="#2ab33b", size=24, stroke_width=2
        )
        self.add_button.setIcon(QIcon(add_icon.toqpixmap()))
        self.remove_button = QPushButton()
        self.remove_button.clicked.connect(self.remove_term)
        self.remove_button.setToolTip("Remove Selected Terms")
        remove_icon = TablerIcons.load(
            OutlineIcon.LIBRARY_MINUS, color="#923232", size=24, stroke_width=2
        )
        self.remove_button.setIcon(QIcon(remove_icon.toqpixmap()))
        self.select_deselect_button = QPushButton()
        self.select_deselect_button.clicked.connect(self.select_deselect)
        self.select_deselect_button.setToolTip("Select All")
        check_icon = TablerIcons.load(
            OutlineIcon.SELECT_ALL, color="#1644b9", size=24, stroke_width=2
        )
        self.pix_check = QIcon(check_icon.toqpixmap())
        uncheck_icon = TablerIcons.load(
            OutlineIcon.DESELECT, color="#923232", size=24, stroke_width=2
        )
        self.pix_uncheck = QIcon(uncheck_icon.toqpixmap())
        self.select_deselect_button.setIcon(self.pix_check)
        self.edit_button = QPushButton()
        self.edit_button.clicked.connect(self.edit_term)
        self
        edit_icon = TablerIcons.load(
            OutlineIcon.EDIT, color="#833d9a", size=24, stroke_width=2
        )
        self.edit_button.setIcon(QIcon(edit_icon.toqpixmap()))
        self.edit_button.setEnabled(False)
        self.edit_button.setToolTip("Edit")
        self.term_count = QLabel()
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.select_deselect_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.term_count)
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

    def _about(self):
        self.about_window = AboutWindow(self)
        self.about_window.setWindowFlags(
            self.about_window.windowFlags() & ~Qt.WindowType.WindowMinMaxButtonsHint
        )
        githubLink = f'<a href="{__source__}">View the source on GitHub</a>'
        self.about_window.setWindowTitle("About")
        self.about_window.aboutLabel.setText(
            f"Version: {__appname__}\nLast Updated: {__date__}\nAuthor: {__author__}"
        )
        self.about_window.urlLabel.setOpenExternalLinks(True)
        self.about_window.urlLabel.setText(githubLink)
        self.logo = QPixmap()
        self.logo.loadFromData(base64.b64decode(__fingerprint__))
        self.about_window.logoLabel.setPixmap(self.logo)
        self.about_window.logoLabel.resize(20, 20)
        about_width = self.about_window.width()
        about_height = self.about_window.height()
        self.about_window.move(
            self.x + (about_width // 4), self.y + (about_height // 4)
        )
        self.about_window.show()

    def double_click(self, index: QModelIndex):
        column = index.column()
        if column != 0:
            self.edit_term()

    def clear_placeholder(self):
        if self.search_bar.placeholderText():
            self.search_bar.setPlaceholderText("")

    def restore_placeholder(self):
        if not self.search_bar.text():
            self.search_bar.setPlaceholderText("Search all terms and definitions...")

    def clear_search(self):
        self.search_bar.clear()
        self.restore_placeholder()

    def load_data(self):
        if not os.path.exists(self.db_path):
            QMessageBox.critical(
                self,
                "Database Error",
                f"The database cannot be found at {self.db_path}.\n\nPlease make sure it exists, and if it does not, you can download an updated copy from https://github.com/digitalsleuth/dfir-glossary",
            )
            sys.exit(1)
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, term, definition, source FROM glossary")
            data = cursor.fetchall()
            conn.close()
            self.model.setHorizontalHeaderLabels(["Term", "Definition", "Source"])
        except sqlite3.Error as e:
            QMessageBox.critical(
                self, "Database Error", f"Error connecting to database: {e}"
            )
        for row_index, row_data in enumerate(data):
            term_id = int(row_data[0]) if row_data[0] is not None else 0
            term = str(row_data[1]) if row_data[1] is not None else ""
            definition = str(row_data[2]) if row_data[2] is not None else ""
            source = str(row_data[3]) if row_data[3] is not None else ""
            term_item = QStandardItem(term)
            term_item.setCheckable(True)
            term_item.setEditable(False)
            definition_item = QStandardItem(definition)
            definition_item.setEditable(False)
            source_item = QStandardItem(source)
            source_item.setEditable(False)
            try:
                self.model.setItem(row_index, 0, term_item)
                self.model.setItem(row_index, 1, definition_item)
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
        self.term_count.setText(f"{len(data)} terms loaded")

    def search(self, text):
        self.model.setRowCount(0)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, term, definition, source FROM glossary WHERE term LIKE ? OR definition LIKE ?",
            ("%" + text + "%", "%" + text + "%"),
        )
        data = cursor.fetchall()
        conn.close()
        self.term_count.setText(f"{len(data)} terms loaded")
        for row_index, row_data in enumerate(data):
            term_item = QStandardItem(row_data[1])
            term_item.setCheckable(True)
            term_item.setEditable(False)
            if row_data[1] in self.checked_ids:
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
            term = item.text()
            if item:
                item.setCheckState(Qt.CheckState.Checked)
                self.checked_ids.add(term)
                __checked__ = True
        self.select_deselect_button.setIcon(self.pix_uncheck)
        self.select_deselect_button.setToolTip("Deselect All")

    def deselect_all(self):
        global __checked__
        for row in range(self.model.rowCount()):
            item = self.model.item(row, 0)
            term = item.text()
            if item:
                item.setCheckState(Qt.CheckState.Unchecked)
                self.checked_ids.discard(term)
                __checked__ = False
        self.select_deselect_button.setIcon(self.pix_check)
        self.select_deselect_button.setToolTip("Select All")

    def select_deselect(self):
        if __checked__:
            self.deselect_all()
        else:
            self.select_all()

    def display_definition(self, index):
        term_index = index.row()
        column = index.column()
        display_text = ""
        term_item = self.model.item(term_index, 0)
        term_text = term_item.text()
        definition_item = self.model.item(term_index, 1)
        source_item = self.model.item(term_index, 2)
        if column == 0:
            display_text = f"{term_item.text()}\n\n{definition_item.text()}\n\n{source_item.text()}"
            self.edit_button.setEnabled(False)
        elif column == 1:
            display_text = definition_item.text()
            self.edit_button.setEnabled(True)
        elif column == 2:
            display_text = source_item.text()
            self.edit_button.setEnabled(True)
        if term_item.checkState() == Qt.CheckState.Checked:
            self.checked_ids.add(term_text)
        else:
            self.checked_ids.discard(term_text)
        self.definition_display.setText(display_text)

    def export_selected(self):
        output_file = None
        exported_terms = []
        if self.checked_ids:
            output_file, _ = QFileDialog.getSaveFileName(
                self,
                "Select output file",
                "",
                "CSV File (*.csv)",
            )
        if output_file:
            try:
                with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["Term", "Definition", "Source"])
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    for term in self.checked_ids:
                        cursor.execute(
                            "SELECT term, definition, source FROM glossary WHERE term = ?",
                            (term,),
                        )
                        result = cursor.fetchone()
                        exported_terms.append(result)
                    conn.close()
                    output = sorted(exported_terms, key=lambda x: x[0].casefold())
                    for term in output:
                        writer.writerow(term)
                QMessageBox.information(self, "Export", "Terms exported successfully!")
            except sqlite3.OperationalError as exc:
                QMessageBox.critical(
                    self,
                    "SQLite3 Error",
                    f"Unable to read the SQLite database:\n\n{exc}",
                )
                return
            except (FileNotFoundError, PermissionError) as exc:
                QMessageBox.critical(
                    self,
                    "File not found",
                    f"Unable to open or create the selected CSV file:\n\n{exc}",
                )
            except csv.Error as exc:
                QMessageBox.critical(
                    self,
                    "CSV Writer Error",
                    f"Unable to write to the selected CSV file:\n\n{exc}",
                )
                return
            except Exception as exc:
                QMessageBox.critical(self, "Error", f"An error occurred: {exc}")
                return
        else:
            return

    def add_term(self):
        dialog = AddTermDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            term, definition, source = dialog.get_term_data()
            if not term:
                QMessageBox.critical(
                    self,
                    "Term required",
                    "The 'Term' field cannot be empty.\n\nPlease enter a value in the 'Term' field.\t",
                )
                return
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1 from glossary WHERE term = ? LIMIT 1", (term,))
            exists = cursor.fetchone()
            if exists:
                QMessageBox.critical(
                    self,
                    "Term exists",
                    f"The term {term} already exists in the database.\n\nConsider searching for the term and editing the definition or source as necessary.\t",
                )
                return
            try:
                cursor.execute(
                    "INSERT INTO glossary (term, definition, source) VALUES (?, ?, ?)",
                    (term, definition, source),
                )
                conn.commit()
                conn.close()
                self.load_data()
            except sqlite3.OperationalError as exc:
                QMessageBox.critical(
                    self,
                    "Unable to add term",
                    f"Unable to add term {term} to the database due to an SQLite3 error:\n\n{exc}",
                )
                return

    def remove_term(self):
        if not self.checked_ids:
            return
        choice = QMessageBox.warning(
            self,
            "Confirm deletion",
            f"Are you sure you want to delete {len(self.checked_ids)} terms?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if choice == QMessageBox.StandardButton.No:
            return
        checked_rows = []
        for row in range(self.model.rowCount()):
            index = self.model.index(row, 0)
            if (
                self.model.data(index, Qt.ItemDataRole.CheckStateRole)
                == Qt.CheckState.Checked
            ):
                checked_rows.append(row)
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            for index in reversed(sorted(self.checked_ids)):
                cursor.execute("DELETE FROM glossary WHERE term = ?", (index,))
            conn.commit()
            conn.close()
        except sqlite3.OperationalError as exc:
            QMessageBox.critical(
                self,
                "Unable to remove term",
                f"Unable to remove the selected terms due to the following SQLite 3 error:\n\n{exc}",
            )
            return
        for row in checked_rows:
            self.model.removeRow(row)
        self.checked_ids.clear()
        self.load_data()

    def edit_term(self):
        selection_model = self.table_view.selectionModel()
        current_index = selection_model.currentIndex()
        self.selected_column = current_index.column()
        if self.selected_column == 0:
            return
        self.selected_row = current_index.row()
        self.cell_text = self.model.data(current_index, Qt.ItemDataRole.DisplayRole)
        columns = {1: "definition", 2: "source"}
        column = columns[self.selected_column]
        self.term_item = self.model.item(self.selected_row, 0)
        self.term_text = self.term_item.text()
        dialog = EditDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            text = dialog.get_term_data()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 from glossary WHERE term = ? LIMIT 1", (self.term_text,)
            )
            exists = cursor.fetchone()
            if exists:
                sql = f"UPDATE glossary SET {column} = '{text}' WHERE term = '{self.term_text}'"
                try:
                    self.model.setData(current_index, text, Qt.ItemDataRole.DisplayRole)
                    cursor.execute(sql)
                    conn.commit()
                    conn.close()
                    self.load_data()
                except sqlite3.OperationalError as exc:
                    self.model.setData(
                        current_index, self.cell_text, Qt.ItemDataRole.DisplayRole
                    )
                    QMessageBox.critical(
                        self,
                        f"Unable to change {column}",
                        f"Unable to change the {column} to '{text}':\n\n{exc}\n\nRestoring {column} to {self.cell_text}",
                    )
                    self.load_data()
                    return


class ContextMenu:

    def __init__(self, tbl_view, checked_ids, edit_term):
        self.tbl_view = tbl_view
        self.checked_ids = checked_ids
        self.edit_term = edit_term

    def show_context_menu(self, pos):
        context_menu = QMenu(self.tbl_view)
        selection_model = self.tbl_view.selectionModel()
        current_index = selection_model.currentIndex()
        selected_column = current_index.column()
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
        edit_event = context_menu.addAction("Edit")
        edit_event.setShortcut(QKeySequence("Ctrl+E"))
        edit_event.setShortcutVisibleInContextMenu(True)
        edit_event.triggered.connect(self.edit_term)
        if selected_column == 0:
            edit_event.setEnabled(False)
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
                term = model.index(row, 0).data()
                model.setData(index, check_state, Qt.ItemDataRole.CheckStateRole)
                if check_state == Qt.CheckState.Checked:
                    self.checked_ids.add(term)
                else:
                    self.checked_ids.discard(term)


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


class EditDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        column = parent.selected_column
        columns = {0: "Term", 1: "Definition", 2: "Source"}
        label = columns[column]
        self.setWindowTitle(f"Edit {label}")
        self.setFixedSize(400, 200)
        text = parent.cell_text
        layout = QFormLayout()
        self.item_edit = QTextEdit()
        self.item_edit.resize(self.size())
        self.item_edit.setText(text)
        layout.addRow(f"{label}:", self.item_edit)

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
        return self.item_edit.toPlainText()


class AboutWindow(QDialog):
    """Sets the structure for the About window"""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout()
        self.aboutLabel = QLabel()
        self.urlLabel = QLabel()
        self.logoLabel = QLabel()
        spacer = QLabel()
        layout.addWidget(self.aboutLabel, 0, 0)
        layout.addWidget(spacer, 0, 1)
        layout.addWidget(self.urlLabel, 1, 0)
        layout.addWidget(self.logoLabel, 0, 2)
        self.setFixedHeight(100)
        self.setFixedWidth(350)
        self.setLayout(layout)


def main():
    app = QApplication([__appname__, "windows:darkmode=2"])
    window = GlossaryApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
