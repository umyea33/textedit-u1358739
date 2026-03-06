"""
Profile timing operations to identify bottlenecks.

Run with: python profile_timing.py
"""
import os
import sys
import time
import cProfile
import pstats
from io import StringIO
from pathlib import Path

# Add parent directory to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QTextCursor
from main import TextEditor, FindReplaceDialog


def profile_operation(name, operation_func):
    """Profile an operation and print results."""
    print(f"\n{'='*70}")
    print(f"Profiling: {name}")
    print(f"{'='*70}")
    
    # Create profiler
    profiler = cProfile.Profile()
    
    # Run operation
    profiler.enable()
    result = operation_func()
    profiler.disable()
    
    # Print stats
    s = StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(20)  # Top 20 functions
    print(s.getvalue())
    
    return result


def profile_file_opening():
    """Profile file opening operation."""
    def operation():
        editor = TextEditor()
        editor.show()
        QApplication.processEvents()
        time.sleep(0.1)
        
        editor.load_file("small.txt")
        
        # Wait for loading
        timeout = time.time() + 30
        while time.time() < timeout:
            QApplication.processEvents()
            time.sleep(0.001)
            if not hasattr(editor.editor, '_load_chunks') and \
               (not hasattr(editor.editor, '_pending_file_load') or 
                editor.editor._pending_file_load is None):
                break
        
        editor.close()
        return editor
    
    return profile_operation("File Opening (small.txt)", operation)


def profile_scrolling():
    """Profile scrolling operation."""
    def operation():
        editor = TextEditor()
        editor.show()
        QApplication.processEvents()
        
        editor.load_file("small.txt")
        
        # Wait for loading
        timeout = time.time() + 30
        while time.time() < timeout:
            QApplication.processEvents()
            time.sleep(0.001)
            if not hasattr(editor.editor, '_load_chunks') and \
               (not hasattr(editor.editor, '_pending_file_load') or 
                editor.editor._pending_file_load is None):
                break
        
        # Profile scrolling
        for _ in range(20):
            cursor = editor.editor.textCursor()
            cursor.movePosition(QTextCursor.Down)
            editor.editor.setTextCursor(cursor)
            QApplication.processEvents()
            time.sleep(0.01)
        
        editor.close()
        return editor
    
    return profile_operation("Scrolling (small.txt)", operation)


def profile_find_replace():
    """Profile find and replace operation."""
    def operation():
        editor = TextEditor()
        editor.show()
        QApplication.processEvents()
        
        editor.load_file("small.txt")
        
        # Wait for loading
        timeout = time.time() + 30
        while time.time() < timeout:
            QApplication.processEvents()
            time.sleep(0.001)
            if not hasattr(editor.editor, '_load_chunks') and \
               (not hasattr(editor.editor, '_pending_file_load') or 
                editor.editor._pending_file_load is None):
                break
        
        # Profile find/replace
        find_dialog = FindReplaceDialog(editor.editor, editor)
        find_dialog.show()
        QApplication.processEvents()
        time.sleep(0.1)
        
        find_dialog.find_input.setText("while")
        find_dialog.replace_input.setText("for")
        QApplication.processEvents()
        time.sleep(0.05)
        
        # Profile the replace_all operation
        find_dialog.replace_all()
        
        # Wait for completion
        timeout = time.time() + 30
        while time.time() < timeout:
            QApplication.processEvents()
            time.sleep(0.01)
            if not hasattr(find_dialog, '_replace_state'):
                break
        
        # Handle the dialog that appears
        active_window = QApplication.activeWindow()
        if active_window and active_window != editor:
            # Try to close any dialog
            QTimer.singleShot(500, active_window.close)
        
        QApplication.processEvents()
        
        find_dialog.close()
        editor.close()
        return editor
    
    return profile_operation("Find & Replace (small.txt)", operation)


if __name__ == "__main__":
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    print("Starting profiling...")
    print(f"Working directory: {os.getcwd()}")
    
    try:
        profile_file_opening()
        profile_scrolling()
        profile_find_replace()
    except Exception as e:
        print(f"Error during profiling: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if app:
            app.quit()
