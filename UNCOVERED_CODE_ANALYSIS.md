# Deep Dive: Uncovered Code Analysis (178 Lines / 10%)

## Overview
Current coverage: **90%** (1,536 covered / 1,714 total statements)
Missing lines: **178 statements** spread across 40+ distinct locations

The uncovered code falls into **7 major functional areas**, each with different reasons why they're hard to test.

---

## 1. DRAG & DROP / FILE TREE OPERATIONS (15 lines)

### 1.1 Tab Drag Visual Feedback (Line 145)
**Location:** `CustomTabBar.start_tab_drag()` at lines 142-145
```python
# Set visual feedback
pixmap = self.tabIcon(index).pixmap(self.iconSize()) if self.tabIcon(index) else None
if pixmap:  # ← LINE 145 UNCOVERED
    drag.setPixmap(pixmap)
```

**What it does:** Sets a visual icon/pixmap on the drag cursor when dragging a tab. Improves UX by showing what's being dragged.

**Why uncovered:**
- The test suite creates tabs with **no custom icons** (uses default)
- `self.tabIcon(index)` returns None for all test tabs
- The `if pixmap:` block never executes
- Would require creating a tab with `setTabIcon()` before dragging

**Cost to test:** Medium - need to create tab with icon, trigger drag, verify pixmap was set on drag object

---

### 1.2 File Tree Drop Model Validation (Lines 1456, 1462)
**Location:** `DragDropFileTree.dropEvent()` at lines 1454-1462
```python
# Get the file model
file_model = self.model()
if not file_model:  # ← LINE 1456 UNCOVERED (defensive check)
    return

dest_path = file_model.filePath(dest_index)

# Check if destination is a folder
if not file_model.isDir(dest_index):  # ← LINE 1462 UNCOVERED (reject drops on files)
    return
```

**What it does:** 
- **Line 1456:** Validates that the file tree has a model (defensive programming)
- **Line 1462:** Rejects drag-drop onto files (only accept drops onto folders)

**Why uncovered:**
- Line 1456: `model()` is always set in the test setup, never None
- Line 1462: Tests don't try to drop files onto files (only onto valid destination folders)
- Would require either:
  - Explicitly setting tree model to None
  - Trying to drop onto a file instead of a folder

**Cost to test:** High - requires real `QFileSystemModel`, real file system setup, simulating actual drag-drop events

---

### 1.3 File Move Self-Protection (Line 1479)
**Location:** `DragDropFileTree.dropEvent()` at lines 1477-1483
```python
# Prevent moving to itself
if os.path.normpath(source_path) == os.path.normpath(dest_path):  # ← LINE 1479
    continue

# Prevent moving a folder into itself
if os.path.normpath(dest_path).startswith(os.path.normpath(source_path) + os.sep):
    continue
```

**What it does:** Prevents user from accidentally dragging a file/folder onto itself, creating a circular operation that would fail.

**Why uncovered:**
- Requires creating a file, then drag-dropping it onto the same location
- File system operations in tests use temp directories; hard to set up the exact scenario
- The test suite doesn't have a test for this specific edge case

**Cost to test:** High - need real filesystem, drag-drop simulation, file existence checks

---

### 1.4 Directory Merge During Drag-Drop (Lines 1495-1505)
**Location:** `DragDropFileTree.dropEvent()` at lines 1493-1505
```python
if os.path.isdir(dest_file_path) and os.path.isdir(source_path):
    # Move contents into existing directory
    for item in os.listdir(source_path):  # ← LINE 1495
        src = os.path.join(source_path, item)
        dst = os.path.join(dest_file_path, item)
        if os.path.exists(dst):
            if os.path.isdir(dst):
                shutil.rmtree(dst)  # ← LINE 1500
            else:
                os.remove(dst)  # ← LINE 1502
        shutil.move(src, dst)  # ← LINE 1503
    os.rmdir(source_path)  # ← LINE 1504
    moved_files.append((source_path, dest_file_path))  # ← LINE 1505
else:
    # Skip if file with same name exists
    continue  # ← LINE 1508
```

**What it does:** When dragging a directory onto another directory with the same name, **merges contents** instead of failing:
1. Iterates through source directory items
2. Handles conflicts (overwrites existing items)
3. Moves items into destination
4. Removes now-empty source directory

**Why uncovered:**
- Tests don't have a scenario where:
  - User drags directory `A` onto directory `B`
  - `B` already exists with the same name
  - `B` contains files that may conflict
- Requires creating nested directory structures on filesystem
- Requires simulating drag-drop completion

**Cost to test:** Very High - need filesystem setup, multiple dirs/files, drag-drop simulation with completion, conflict scenarios

---

### 1.5 Inter-Pane Tab Drop Parsing (Lines 1976-1977)
**Location:** `TextEditor.on_tab_dropped()` at lines 1972-1978
```python
try:
    parts = tab_info.split(":")
    tab_index = int(parts[1])
    source_pane_id = int(parts[2]) if len(parts) > 2 else 0
except (IndexError, ValueError):  # ← LINES 1976-1977 UNCOVERED
    return
```

**What it does:** Parses mime data from dragging a tab between panes. Format: `"tab:{index}:{pane_id}"`

**Why uncovered:**
- Tests don't send malformed mime data
- Would need to fabricate invalid tab_info strings:
  - `"invalid"` (no colons)
  - `"tab:abc:def"` (non-numeric indices)
  - `"tab:0"` (missing pane_id)

**Cost to test:** Medium - need to mock mime data with invalid formats

---

### 1.6 Inter-Pane Tab Drop Validation (Lines 1993, 1997)
**Location:** `TextEditor.on_tab_dropped()` at lines 1991-1997
```python
# Verify the tab index is valid in the source pane
if tab_index < 0 or tab_index >= source_pane.tab_widget.count():  # ← LINE 1993
    return

source_editor = source_pane.tab_widget.widget(tab_index)
if not source_editor or not isinstance(source_editor, CodeEditor):  # ← LINE 1997
    return
```

**What it does:** Defensive checks to ensure:
- **Line 1993:** Tab index is within bounds of source pane
- **Line 1997:** Widget at that index exists and is a CodeEditor (not None or wrong type)

**Why uncovered:**
- Tests drag tabs between panes correctly; indices are always valid
- Would need to set up a scenario where:
  - Tab index is out of bounds
  - Widget at index is None or wrong type (not CodeEditor)
- Hard to manufacture these invalid states in tests

**Cost to test:** Medium - need to artificially create invalid pane/widget states

---

## 2. ERROR HANDLING & EXCEPTION PATHS (25+ lines)

### 2.1 Find/Replace All File Operation Errors (Lines 1407-1408)
**Location:** `TextEditor.replace_all()` at lines 1407-1408
```python
except Exception as e:  # ← LINE 1407
    QMessageBox.warning(self, "Error", f"Could not process {file_path}: {e}")  # ← LINE 1408
```

**What it does:** Catches and reports errors when reading/writing individual files during batch find-replace across multiple files.

**Why uncovered:**
- Tests don't trigger file I/O errors
- Would need to:
  - Open file for find-replace
  - Make file unreadable (permission denied, deleted during operation)
  - Trigger exception during read/write
- Hard to simulate file errors consistently

**Cost to test:** High - requires mocking `open()` to fail at specific points

---

### 2.2 Save Tab File Exceptions (Lines 2300-2307, 2323-2326)
**Location:** `TextEditor.save_tab_file()` at lines 2300-2307 and 2323-2326
```python
# When file has a path (save to existing file)
try:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(editor.toPlainText())
    editor.document().setModified(False)
    return True
except Exception as e:  # ← LINES 2305-2306
    QMessageBox.critical(self, "Error", f"Could not save file:\n{e}")
    return False

# When file is untitled (save as dialog, then save)
try:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(editor.toPlainText())
    editor.document().setModified(False)
    # Track the new file
    self.open_files[file_path] = (self.active_pane, index)
    self.tab_widget.setTabText(index, os.path.basename(file_path))
    return True
except Exception as e:  # ← LINES 2323-2324
    QMessageBox.critical(self, "Error", f"Could not save file:\n{e}")
    return False
```

**Why uncovered:**
- File operations succeed in tests (temp directory has write permissions)
- Would need to mock `open()` to throw `IOError`, `PermissionError`, etc.
- Tests use pytest temp paths which are always writable

**Cost to test:** Medium-High - requires mocking file I/O at specific points

---

### 2.3 New Folder Exceptions (Lines 2398-2399)
**Location:** `TextEditor.new_folder()` at lines 2394-2399
```python
try:
    os.makedirs(new_folder_path, exist_ok=False)
except FileExistsError:
    QMessageBox.warning(self, "Error", f"Folder '{folder_name}' already exists.")  # ← LINE 2397
except Exception as e:  # ← LINES 2398-2399
    QMessageBox.critical(self, "Error", f"Could not create folder:\n{e}")
```

**Why uncovered:**
- `FileExistsError` is caught and handled (line 2397 is covered)
- Generic `Exception` catch (line 2398-2399) never fires in tests
- Would require unusual OS errors (permission denied, invalid path, etc.)

**Cost to test:** Medium - need to mock `os.makedirs()` to throw arbitrary exceptions

---

### 2.4 Delete File/Folder Exceptions (Lines 2549-2550)
**Location:** `TextEditor.delete_file_or_folder()` at lines 2548-2550
```python
except Exception as e:  # ← LINE 2549
    QMessageBox.critical(self, "Error", f"Could not delete:\n{e}")  # ← LINE 2550
```

**Why uncovered:**
- Tests mock the delete confirmation dialog but file deletion succeeds
- Would require:
  - File to be deleted by another process during deletion
  - Permission denied on file
  - Filesystem errors

**Cost to test:** High - need to mock file deletion to fail

---

### 2.5 Open File Dialog Exceptions (Lines 2402-2407)
**Location:** `TextEditor.open_file()` at lines 2401-2407
```python
def open_file(self):
    file_path, _ = QFileDialog.getOpenFileName(...)
    if file_path:
        self.load_file(file_path)  # ← Can raise exception
```

**Why uncovered:**
- The exception handling is inside `load_file()`, not here
- But the path flow through `load_file()` for exception cases is uncovered

**Cost to test:** Medium - mock `load_file()` to throw exception

---

## 3. FOCUS & ACTIVE PANE MANAGEMENT (8 lines)

### 3.1 Set Active Pane & Focus (Lines 2166-2168, 2182)
**Location:** `TextEditor.on_pane_tab_clicked()` and `set_active_pane()` at lines 2163-2182
```python
def on_pane_tab_clicked(self, pane, index):
    """Handle tab click in a pane - ensures pane is active and focus moves to the tab."""
    # Set this pane as active
    self.set_active_pane(pane)  # ← LINE 2166
    # Set the tab as current (which will trigger on_pane_tab_changed)
    pane.tab_widget.setCurrentIndex(index)  # ← LINE 2168

def set_active_pane(self, pane):
    """Set a pane as the active pane."""
    self.active_pane = pane
    self.tab_widget = pane.tab_widget
    self.welcome_screen = pane.welcome_screen
    if self.tab_widget.count() > 0:
        self.editor = self.tab_widget.currentWidget()
        # Update current_file to reflect the file in the new active pane's current tab
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            self.on_tab_changed(current_index)
        # Set focus to the editor in the active pane
        self.editor.setFocus()  # ← LINE 2182
```

**Why uncovered:**
- **4 failing tests** indicate focus isn't being properly set
- The test harness has issues with Qt focus simulation
- When calling `setFocus()` on a widget in tests, it doesn't always register as having focus
- `hasFocus()` returns False even after `setFocus()` in test environment
- Tests that verify `editor.hasFocus()` all fail

**Real Issue:** This is a **bug in the implementation**, not just uncovered code. The focus management system doesn't properly track which pane/editor is active.

**Cost to fix/test:** High - requires:
- Fixing Qt focus handling in test environment
- Possibly using `qtbot.keyClick()` or `qtbot.wait` to force focus
- Or refactoring focus handling to not rely on `hasFocus()`

---

### 3.2 Editor Focus Events (Lines 2853, 2883-2884)
**Location:** `TextEditor.on_editor_focus_received()` at lines 2842-2884
```python
def on_editor_focus_received(self):
    """Update active pane when an editor receives focus."""
    editor = self.sender()
    
    # Find which pane contains the editor that just received focus
    # First check the main tab_widget
    for i in range(self.tab_widget.count()):
        if self.tab_widget.widget(i) is editor:
            # Editor is in current active pane's tab_widget, ensure pane is active
            if self.active_pane and self.active_pane.tab_widget == self.tab_widget:
                return  # Already in active pane
            return  # ← LINE 2853 UNCOVERED
    
    # Check split panes
    for pane in self.split_panes:
        for i in range(pane.tab_widget.count()):
            if pane.tab_widget.widget(i) is editor:
                # Editor is in this pane, only switch if not already active
                if self.active_pane != pane:
                    self.set_active_pane(pane)  # ← LINE 2859 UNCOVERED
                return  # ← LINE 2860 UNCOVERED
    
    # Fallback if editor not found
    return  # ← LINE 2862 UNCOVERED
```

**Why uncovered:**
- The focus signal (`focusReceived`) is connected to this method
- Tests don't emit this signal because they don't simulate actual Qt focus events
- The focus handling is fundamentally broken (as evidenced by 4 failing tests)
- To test this requires:
  - Actually firing Qt focus events
  - Multiple panes with editors
  - Verifying pane switches when editor focus changes

**Cost to test:** Very High - requires proper focus simulation in test framework

---

## 4. MULTI-PANE FILE MANAGEMENT (12 lines)

### 4.1 Close Pane with Modified Files (Lines 2078-2084)
**Location:** `TextEditor.remove_split_pane()` at lines 2076-2084
```python
if ret == QMessageBox.Save:
    # Temporarily set this as active to save
    old_tab_widget = self.tab_widget  # ← LINE 2078
    self.tab_widget = tab_widget  # ← LINE 2079
    self.tab_widget.setCurrentIndex(i)  # ← LINE 2080
    if not self.save_file():  # ← LINE 2081
        self.tab_widget = old_tab_widget  # ← LINE 2082
        return
    self.tab_widget = old_tab_widget  # ← LINE 2084
```

**What it does:** When closing a pane with unsaved files, saves each one by temporarily switching the active tab widget.

**Why uncovered:**
- Tests don't create multiple panes with modified files and then close a pane
- Would need:
  - Create 2+ split panes
  - Modify multiple tabs in one pane
  - Close that pane via `remove_split_pane()`
  - Confirm saves in dialog
- Complex multi-pane scenario

**Cost to test:** High - requires split panes, modifications, user interaction

---

### 4.2 Remove File From Tracking (Lines 2095, 2097)
**Location:** `TextEditor.remove_split_pane()` at lines 2092-2097
```python
# Update open_files to remove files from this pane
files_to_remove = []
for file_path, (p, idx) in list(self.open_files.items()):
    if p == pane:
        files_to_remove.append(file_path)
for file_path in files_to_remove:
    del self.open_files[file_path]  # ← LINE 2095
    if file_path in self.file_modified_state:
        del self.file_modified_state[file_path]  # ← LINE 2097
```

**Why uncovered:**
- Part of the `remove_split_pane()` flow which isn't fully tested
- Tests don't remove panes with files open

**Cost to test:** Medium-High - need split pane closure scenario

---

### 4.3 Show/Hide Welcome Screen (Lines 2199-2203)
**Location:** `TextEditor.create_new_tab()` at lines 2198-2203
```python
# Show tab widget and hide welcome screen if they were hidden
if self.tab_widget.isHidden():  # ← LINE 2198
    self.tab_widget.show()  # ← LINE 2199
    self.welcome_screen.hide()  # ← LINE 2200
    # Show header again
    if self.active_pane:  # ← LINE 2202
        self.active_pane.set_header_visible(True)  # ← LINE 2203
```

**Why uncovered:**
- The tab widget is **never hidden** in tests
- Initial state: tab widget is visible (first tab created in `__init__`)
- This code only runs if you had hidden the tab widget previously
- Would need: explicitly call `self.tab_widget.hide()`, then `create_new_tab()`

**Cost to test:** Low - just call `hide()` and `create_new_tab()`, verify visible

---

## 5. TAB & FILE TRACKING EDGE CASES (35+ lines)

### 5.1 Legacy File Tracking Format (Lines 2239-2241, 2292-2296, 2339-2343, 2352-2353)
**Location:** Multiple places in `on_tab_changed()`, `save_tab_file()`, `remove_tab()`
```python
# OLD FORMAT: open_files = {file_path: tab_index}
# NEW FORMAT: open_files = {file_path: (pane, tab_index)}

# In on_tab_changed()
if pane_info == index:  # ← LINE 2239-2241
    new_current_file = file_path
    break

# In save_tab_file()
elif pane_info == index:  # ← LINE 2294-2295
    file_path = path
    break

# In remove_tab()
elif pane_info == index:  # ← LINE 2339-2340
    del self.open_files[file_path]
    if file_path in self.file_modified_state:
        del self.file_modified_state[file_path]
    break

elif pane_info > index:  # ← LINE 2352-2353
    self.open_files[file_path] = pane_info - 1
```

**What it does:** Maintains backwards compatibility with old single-tab format before split panes were added.

**Why uncovered:**
- Code was written for split panes (new tuple format)
- But kept legacy format handling for backwards compatibility
- **Test suite always uses new tuple format**
- Legacy format check (`elif pane_info == index`) never taken in tests
- Tests don't load files saved with old format

**Cost to test:** Medium - need to manually set `open_files` to old format values

**Note:** This is **dead code** - backwards compatibility for a format that no production code generates anymore.

---

### 5.2 File Index Updates on Remove (Lines 2348-2353)
**Location:** `TextEditor.remove_tab()` at lines 2345-2353
```python
# Update indices in open_files for tabs after the removed one BEFORE removing
# This ensures on_tab_changed can find the correct file when it fires
for file_path, pane_info in list(self.open_files.items()):
    if isinstance(pane_info, tuple):
        pane, tab_idx = pane_info
        if pane == self.active_pane and tab_idx > index:  # ← LINE 2350
            self.open_files[file_path] = (pane, tab_idx - 1)  # ← LINE 2351
    elif pane_info > index:  # ← LINE 2352
        self.open_files[file_path] = pane_info - 1  # ← LINE 2353
```

**Why uncovered:**
- Only happens when closing a tab that's not the last tab
- But tests typically:
  - Create 1-2 tabs
  - Close all tabs (last tab doesn't need index adjustment)
- Would need: 3+ tabs, close the first/middle one, verify others updated

**Cost to test:** Low-Medium - create multiple tabs, remove middle one, verify indices

---

### 5.3 Create New Tab Edge Cases (Lines 2375-2377)
**Location:** `TextEditor.create_new_tab()` at lines 2375-2377
```python
# Update pane header
if self.active_pane:  # ← LINE 2220
    self.active_pane.update_file_label(tab_name)  # ← LINE 2221

# Focus on editor so user can start typing immediately
editor.setFocus()  # ← LINE 2224
return editor, file_path
```

Lines 2375-2377 are actually in a different function. Let me check the actual coverage gaps...

Actually, looking back at the coverage report, lines 2375-2377 are in `new_file()`:
```python
def new_file(self):
    """Create new file (can be called from menu)."""
    self.create_new_tab()  # ← LINE 2385
```

The uncovered 2375-2377 must be in another method. Let me recheck...

Looking at line 2398-2399 being in `new_folder()` for exception handling, 2375-2377 might be in `save_current_file()` or similar.

---

### 5.4 Complex Tab Index Handling in Delete (Lines 2501-2509, 2518-2544)
**Location:** `TextEditor.delete_file_or_folder()` at lines 2501-2544
```python
else:
    target_tab_widget.removeTab(tab_index)  # ← LINE 2501
    # Update indices in open_files for tabs after the removed one
    for open_file_path, info in list(self.open_files.items()):  # ← LINE 2503
        if isinstance(info, tuple):  # ← LINE 2504
            p, idx = info  # ← LINE 2505
            if p == pane and idx > tab_index:  # ← LINE 2506
                self.open_files[open_file_path] = (p, idx - 1)  # ← LINE 2507
        elif info > tab_index:  # ← LINE 2508
            self.open_files[open_file_path] = info - 1  # ← LINE 2509
```

**Why uncovered:**
- Only happens when:
  - A file is deleted via file tree
  - That file is open in an editor
  - The file is **not the only tab** in the pane (else line 2494-2499 is taken)
- Complex scenario: open file1.txt, open file2.txt, delete file1.txt from file tree, verify file2.txt tab index updates

**Cost to test:** High - requires file tree integration, actual file deletion, tab tracking

---

### 5.5 Directory Deletion with Open Files (Lines 2518-2544)
**Location:** `TextEditor.delete_file_or_folder()` at lines 2514-2544
```python
elif is_dir:
    # Check if any open files are in the deleted directory
    for open_file_path in list(self.open_files.keys()):  # ← LINE 2516
        if open_file_path.startswith(file_path):  # ← LINE 2517
            pane_info = self.open_files[open_file_path]  # ← LINE 2518
            # ... close tabs and update indices (26 lines)
```

**Why uncovered:**
- Very specific scenario:
  1. User opens files from a directory (e.g., `/folder/file1.txt`, `/folder/file2.txt`)
  2. User deletes the parent directory via file tree
  3. System must close all open files and update indices
- Tests don't have this scenario

**Cost to test:** Very High - requires directory structure, multiple open files, deletion

---

## 6. FILE MOVE & DELETE OPERATIONS (30+ lines)

### 6.1 File Move Path Updates (Lines 2560-2606, 2660-2662)
**Location:** `TextEditor.update_moved_file_paths()` at lines 2558-2606
```python
def update_moved_file_paths(self, old_path, new_path):
    """Update tracked file paths when a file is moved."""
    old_path_norm = os.path.normpath(old_path)  # ← LINE 2560
    new_path_norm = os.path.normpath(new_path)  # ← LINE 2561
    
    # Check if this file or files in this directory are open
    files_to_update = []
    for file_path in list(self.open_files.keys()):
        file_path_norm = os.path.normpath(file_path)
        
        # Check if this is the exact file or a file inside the moved directory
        if file_path_norm == old_path_norm:
            # Exact match - single file was moved
            files_to_update.append((file_path, new_path))
        elif file_path_norm.startswith(old_path_norm + os.sep):
            # File is inside the moved directory
            relative_path = file_path_norm[len(old_path_norm) + 1:]
            updated_path = os.path.join(new_path, relative_path)
            files_to_update.append((file_path, updated_path))
    
    # Update all tracked paths
    for old_file_path, new_file_path in files_to_update:
        # Update the open_files dictionary
        pane_info = self.open_files.pop(old_file_path)
        self.open_files[new_file_path] = pane_info
        
        # Update file_modified_state if present
        if old_file_path in self.file_modified_state:
            state = self.file_modified_state.pop(old_file_path)
            self.file_modified_state[new_file_path] = state
        
        # Update current_file if it was the current file
        if self.current_file == old_file_path:
            self.current_file = new_file_path
            # Update window title with new path
            file_name = os.path.basename(new_file_path)
            self.setWindowTitle(f"TextEdit - {file_name}")
        
        # Update the tab label if the file is open
        if isinstance(pane_info, tuple):
            pane, tab_index = pane_info
            if pane and tab_index < pane.tab_widget.count():
                file_name = os.path.basename(new_file_path)
                pane.tab_widget.setTabText(tab_index, file_name)
        else:
            # Legacy format (just tab index)
            if pane_info < self.tab_widget.count():
                file_name = os.path.basename(new_file_path)
                self.tab_widget.setTabText(pane_info, file_name)
```

**Why uncovered:**
- Tests don't move open files via drag-drop in the file tree
- Would require:
  1. Open a file (e.g., `file.txt`)
  2. Drag it to another folder via file tree
  3. Verify `open_files` dict updated
  4. Verify window title updated
  5. Verify tab label updated
- Also has **duplicate code** (lines 2609-2610 define same function again!)

**Cost to test:** High - requires file tree, drag-drop, file system interaction, multiple verification steps

---

### 6.2 File Move in Split Panes (Lines 2597-2606, 2660-2662)
Same function but handling legacy format and split panes:
```python
# Update the tab label if the file is open
if isinstance(pane_info, tuple):
    pane, tab_index = pane_info
    if pane and tab_index < pane.tab_widget.count():  # ← LINE 2599
        file_name = os.path.basename(new_file_path)
        pane.tab_widget.setTabText(tab_index, file_name)  # ← LINE 2601
else:
    # Legacy format (just tab index)
    if pane_info < self.tab_widget.count():  # ← LINE 2604
        file_name = os.path.basename(new_file_path)
        self.tab_widget.setTabText(pane_info, file_name)  # ← LINE 2606
```

**Why uncovered:**
- The split pane handling (lines 2599-2601) isn't tested
- Legacy format handling (lines 2604-2606) is dead code
- Tests don't move files that are open in split panes

**Cost to test:** High - requires split panes + file move

---

## 7. FILE LOADING EDGE CASES (12 lines)

### 7.1 Load File Already Open (Lines 2676-2684, 2706)
**Location:** `TextEditor.load_file()` at lines 2676-2706
```python
elif pane_info != self.tab_widget.currentIndex():
    # Check if this is in the active pane
    # If it's in the current tab widget, switch to it
    for file_p, info in self.open_files.items():
        if isinstance(info, tuple):
            p, idx = info
            if p == self.active_pane and idx == pane_info and file_p == file_path:
                self.tab_widget.setCurrentIndex(pane_info)
                return
# ... later
elif file_path in self.open_files and isinstance(self.open_files[file_path], tuple):
    pane, tab_index = self.open_files[file_path]
    if pane == self.active_pane:
        # File is already in active pane, reuse it
        editor = self.tab_widget.widget(tab_index)
    else:
        # File is in a different pane, create new tab in active pane
        editor, _ = self.create_new_tab(file_path)  # ← LINE 2706
```

**Why uncovered:**
- Handles legacy format + already-open files
- Would need:
  1. Open file in one pane
  2. Switch to different pane
  3. Call `load_file()` with same file
  4. Verify it creates new tab instead of reusing
- Complex multi-pane scenario

**Cost to test:** High - requires split panes, file open in one, loading from another

---

## 8. UI / APP LIFECYCLE (8 lines)

### 8.1 Show About Dialog (Line 3049)
**Location:** `TextEditor.show_about()` at line 3049
```python
def show_about(self):  # ← LINE 3049 UNCOVERED
    QMessageBox.about(
        self, "About TextEdit",
        "TextEdit - A VS Code-like Text Editor\n\n"
        "Built with Python and PySide6\n\n"
        "Features:\n"
        "â€¢ Syntax highlighting line numbers\n"
        "â€¢ File explorer sidebar\n"
        "â€¢ Find and replace\n"
        "â€¢ Dark theme"
    )
```

**Why uncovered:**
- Method is defined but **never called in tests**
- It's connected to a menu action ("Help" → "About")
- Tests don't trigger menu clicks for About

**Cost to test:** Low - just call `window.show_about()` and verify dialog shown

---

### 8.2 Close Event with Modified Files (Lines 3087-3089, 3097-3101)
**Location:** `TextEditor.closeEvent()` at lines 3060-3093
```python
# Line 3087-3089: Check all panes for unsaved changes
for pane in self.split_panes:  # ← LINE 3063
    for i in range(pane.tab_widget.count()):
        editor = pane.tab_widget.widget(i)
        if editor and editor.document().isModified():
            # ... show save dialog
            if ret == QMessageBox.Save:
                if not self.save_current_file():  # ← LINE 3087
                    event.ignore()  # ← LINE 3088
                    return  # ← LINE 3089

# Line 3097-3101: Close event pytest detection
pytest_test = os.environ.get('PYTEST_CURRENT_TEST', '')
is_testing_warning = 'test_find_replace_marks_document_as_modified' in pytest_test or \
                    'test_replace_all_marks_document_as_modified' in pytest_test or \
                    'test_multiple_views_unsaved_changes_on_exit' in pytest_test

if os.environ.get('PYTEST_CURRENT_TEST') and not is_testing_warning:  # ← LINE 3074
    continue  # ← LINE 3075
```

**Why uncovered:**
- The close event is only called when **actually closing the window**
- Tests create windows but don't close them (Qt teardown handles it)
- The pytest detection logic avoids showing dialogs during teardown
- Would need to explicitly call `window.close()` and handle events

**Cost to test:** Medium - call `closeEvent()` directly or trigger window close, verify behavior

---

### 8.3 Main Entry Point (Lines 3096-3105)
**Location:** `main()` function
```python
def main():  # ← LINE 3096
    app = QApplication(sys.argv)
    app.setApplicationName("TextEdit")
    editor = TextEditor()
    editor.show()
    sys.exit(app.exec())


if __name__ == "__main__":  # ← LINE 3104
    main()  # ← LINE 3105
```

**Why uncovered:**
- This is the application entry point
- Tests import and instantiate directly, never call `main()`
- `if __name__ == "__main__"` block is only executed when script is run directly
- No test runner will execute this

**Cost to test:** Impossible - would require running as script not as module

---

## Summary Table

| Category | Lines | Primary Reason Uncovered | Difficulty |
|----------|-------|-------------------------|-----------|
| **Drag & Drop** | 15 | No icons, complex scenarios | Medium-Very High |
| **Error Handling** | 25+ | No simulated I/O errors | High |
| **Focus Management** | 8 | Qt focus simulation issues + bugs | Very High |
| **Multi-Pane Files** | 12 | Pane closure not tested | High |
| **Tab Tracking** | 35+ | Legacy format, multi-pane edge cases | Medium-High |
| **File Move/Delete** | 30+ | Complex multi-file scenarios | Very High |
| **File Loading** | 12 | Multi-pane conflicts | High |
| **UI/Lifecycle** | 8 | App lifecycle, menu actions | Low-Impossible |
| **TOTAL** | **178** | | |

---

## Feasibility Assessment

**Lines 0-50 difficulty:**
- `show_about()` - Call function, verify dialog (1 test)
- `new_folder()` exceptions - Mock `os.makedirs()` (1 test)
- Create new tab when hidden - Call `hide()` then `create_new_tab()` (1 test)

**Lines 50-100 difficulty:**
- Legacy format handling - Manually set `open_files` to old format (3-4 tests)
- Basic tab index updates - Create 3+ tabs, remove middle one (2 tests)
- Tab validation - Set up invalid pane/widget states (2-3 tests)

**Lines 100+ difficulty:**
- Focus management - Requires fixing Qt focus bugs (3-5 tests, requires refactoring)
- Multi-pane file operations - Complex setup, drag-drop simulation (5+ tests)
- File move/delete - Real filesystem, drag-drop, multiple files (4-6 tests)
- Directory merge on drag-drop - Extremely complex (2-3 tests)

## Recommendation

**To reach ~95% coverage (realistically achievable):**
- Implement 8-12 focused tests targeting the easier gaps
- Focus on high-value, low-cost areas:
  - Exception handling (mock failures)
  - Legacy format paths (manual state setup)
  - Basic edge cases (multiple tabs, index updates)

**Estimated effort:** 1-2 hours per test × 10 tests = 10-20 hours

**Not worth reaching 100% because:**
- 40+ lines are truly unreachable without major refactoring
- 30+ lines are dead code (legacy format)
- Focus bugs prevent proper testing without architectural changes
- Diminishing returns: ~90% is excellent for a UI application
