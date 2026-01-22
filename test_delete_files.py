import pytest
from pathlib import Path
from PySide6.QtWidgets import QMessageBox
from main import TextEditor


class TestDeleteFileAndFolder:
    """Tests for deleting files and folders."""
    
    def test_delete_file_removes_from_filesystem(self, qtbot, tmp_path, monkeypatch):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create a test file
        test_file = tmp_path / "test_delete.txt"
        test_file.write_text("content to delete")
        
        # Verify file exists
        assert test_file.exists()
        
        # Mock QMessageBox.question to return Yes
        monkeypatch.setattr(
            "main.QMessageBox.question",
            lambda *args, **kwargs: QMessageBox.Yes
        )
        
        # Delete the file
        window.delete_file_or_folder(str(test_file), is_dir=False)
        
        # Verify file is deleted
        assert not test_file.exists()
    
    def test_delete_folder_removes_from_filesystem(self, qtbot, tmp_path, monkeypatch):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create a test folder with files
        test_folder = tmp_path / "test_delete_folder"
        test_folder.mkdir()
        (test_folder / "file1.txt").write_text("content1")
        (test_folder / "file2.txt").write_text("content2")
        
        # Verify folder exists
        assert test_folder.exists()
        assert test_folder.is_dir()
        
        # Mock QMessageBox.question to return Yes
        monkeypatch.setattr(
            "main.QMessageBox.question",
            lambda *args, **kwargs: QMessageBox.Yes
        )
        
        # Delete the folder
        window.delete_file_or_folder(str(test_folder), is_dir=True)
        
        # Verify folder is deleted
        assert not test_folder.exists()
    
    def test_delete_file_cancellation(self, qtbot, tmp_path, monkeypatch):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create a test file
        test_file = tmp_path / "test_no_delete.txt"
        test_file.write_text("content to keep")
        
        # Verify file exists
        assert test_file.exists()
        
        # Mock QMessageBox.question to return No
        monkeypatch.setattr(
            "main.QMessageBox.question",
            lambda *args, **kwargs: QMessageBox.No
        )
        
        # Try to delete the file (but cancel)
        window.delete_file_or_folder(str(test_file), is_dir=False)
        
        # Verify file still exists (deletion was cancelled)
        assert test_file.exists()
        assert test_file.read_text() == "content to keep"
    
    def test_delete_currently_open_file(self, qtbot, tmp_path, monkeypatch):
        window = TextEditor()
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)
        
        # Create and open a test file
        test_file = tmp_path / "open_file.txt"
        test_file.write_text("open content")
        window.load_file(str(test_file))
        
        # Verify file is open
        assert window.current_file == str(test_file)
        assert "open content" in window.editor.toPlainText()
        
        # Mock QMessageBox.question to return Yes
        monkeypatch.setattr(
            "main.QMessageBox.question",
            lambda *args, **kwargs: QMessageBox.Yes
        )
        
        # Delete the file
        window.delete_file_or_folder(str(test_file), is_dir=False)
        
        # Verify file is deleted
        assert not test_file.exists()
        
        # Verify editor is cleared
        assert window.current_file is None
        assert window.editor.toPlainText() == ""
        assert "Untitled" in window.windowTitle()
