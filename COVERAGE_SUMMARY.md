# Code Coverage Summary: 144 Uncovered Lines (92% Coverage)

## Coverage Report Overview
- **Total statements:** 1714
- **Covered:** 1570
- **Uncovered:** 144 (8%)
- **Coverage:** 92%

## Uncovered Lines Breakdown

### Line 1456 - DragDropFileTree.dropEvent()
- `if not file_model:` - Condition for when `self.model()` returns None during drag/drop

### Lines 1499-1502 - Directory merge logic in DragDropFileTree.dropEvent()
- Nested directory merge when both source and destination are directories
- `if os.path.isdir(dst):` - Condition for cleaning up existing destination files

### Line 1997 - Early return in on_tab_dropped()
- `if not source_editor or not isinstance(source_editor, CodeEditor): return`

### Lines 2078-2084 - Unsaved changes warning in close_split_pane()
- Save confirmation dialogs and save flow (requires user interaction)

### Line 2095 - Closing split pane with unsaved changes
- `pane_info < self.tab_widget.count()` legacy format handling

### Lines 2097-2101 - Split pane closure continuation
- Index updates after tab removal in legacy format

### Lines 2199-2203 - Creating new tabs logic
- `if self.active_pane:` header visibility updates
- Untitled document tracking

### Lines 2239-2241 - Tab change handler legacy format
- `elif pane_info == index:` legacy open_files format handling

### Lines 2294-2296 - Saving specific tab files
- Legacy format checking in `save_tab_file()`

### Lines 2302-2304 - Exception handling in tab save
- `except Exception as e:` branches

### Lines 2339-2343 - Remove tab legacy format
- Legacy format handling in `remove_tab()`

### Lines 2352-2353 - Tab index updates for legacy format
- `elif pane_info > index:` legacy format index adjustment

### Lines 2375-2377 - save_current_file() and save_file_as()
- Alternative return paths (when using save-as)

### Lines 2402-2407 - File operations exception handling
- `except Exception as e:` in `new_folder()`, `open_file()`, etc.

### Lines 2425-2446 - Find/replace and language features
- Multi-file search dialog, find/replace functionality
- Language selection menu (rarely tested in automated tests)

### Lines 2484-2485 - File rename on move
- `except Exception as e:` in `on_files_moved()`

### Lines 2501-2509 - Tab content after file move
- Tab state updates when files are moved in file tree

### Lines 2518-2544 - File drop operations
- Destination cleanup and file move exception handling

### Lines 2555-2556 - Invalid index handling
- `if not index.isValid(): return` in context menu

### Lines 2560-2606 - File deletion logic
- Complex file/directory deletion with confirmation dialogs
- Exception handling for delete operations

### Lines 2660-2662 - Tab label updates for moved files (legacy format)

### Lines 2676-2684 - File already open detection (legacy format path)

### Line 2706 - File load fallback for open files in different panes

### Lines 2791-2802 - Close event and unsaved changes handling
- Pytest-specific environment checks during shutdown
- Multiple condition branches for handling modified documents

### Line 2853 - Early return in on_editor_focus_received()

### Lines 2883-2884 - Multi-file search dialog initialization

### Lines 3087-3089 - Save failures during close event

### Lines 3097-3101 - Application entry point (main() function)

## Summary by Category

### 1. Legacy Format Handling (~15 lines)
Old `open_files` format compatibility code paths. These exist for backward compatibility with older file tracking structures.

### 2. Exception Handling (~20 lines)
`except` blocks in file operations (save, open, delete, etc.). Hard to test without simulating actual I/O errors.

### 3. User Dialogs (~40 lines)
Unsaved changes confirmations, save-as dialogs, and user interaction flows. Require interactive testing or complex mock setups.

### 4. File Operations (~30 lines)
Drag/drop, move, delete, rename operations. Complex interactions with the file system that require careful test setup.

### 5. GUI/UX Features (~20 lines)
Multi-file search, language menu, tooltips, and visual feedback. Often UI-specific and harder to automate.

### 6. Edge Cases (~20 lines)
Invalid indices, empty panes, focus events, model state checks. Boundary conditions that are difficult to trigger reliably.

### 7. Application Entry (~5 lines)
`main()` function and startup code. Not tested as part of unit tests (app is started differently in tests).

## Coverage Analysis

### High Priority for Testing
1. **File deletion logic** (lines 2560-2606) - Complex with multiple conditions
2. **File move/rename** (lines 2484-2509, 2518-2544) - Core file tree functionality
3. **Exception handling** in critical paths - File I/O operations

### Lower Priority
1. **Legacy format handling** - Backward compatibility code, less critical
2. **Application entry point** - Tested through integration tests, not unit tests
3. **GUI tooltips and visual feedback** - Non-functional code paths

### Notes
- 92% coverage is quite good for a GUI application
- Many uncovered lines are exception handlers, which are difficult to test without real errors
- User dialog paths require interactive testing or sophisticated mocking
- The application is well-tested in core functionality (file editing, tab management, split views)
