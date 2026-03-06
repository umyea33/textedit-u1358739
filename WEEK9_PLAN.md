# Week 9 Optimization Plan

## Goal
Hit **16ms max frame time** (60Hz / 60 FPS) for all user actions across all file sizes.

## Current Bottlenecks (Identified via Analysis)

### 1. **File Loading (lines 2839-2910)**
- **Current**: Entire file loaded into RAM synchronously on main thread
- **Problem**: 16.2 seconds for large.txt = 16,200+ dropped frames
- **Solution**: Defer non-essential work, only render visible blocks on startup

### 2. **Syntax Highlighting (lines 986-1099)**
- **Current**: Even with lazy highlighting, blocks processed synchronously in timer
- **Problem**: `highlight_remaining_blocks()` at 100 blocks/50ms can still block
- **Solution**: Reduce block highlighting duration to fit in ~14ms per frame

### 3. **Find & Replace (lines 1310-1344)**
- **Current**: Entire document regex processed synchronously
- **Problem**: 18.2 seconds for large.txt = 18,200+ dropped frames
- **Solution**: Process in chunks, show progress, allow UI responsiveness

### 4. **Scroll Rendering (lines 1034-1047)**
- **Current**: Calls `highlight_visible_blocks()` on every scroll event
- **Problem**: May recalculate and re-highlight blocks unnecessarily
- **Solution**: Cache visible block positions, reduce redundant work

## Implementation Strategy

### Phase 1: Reduce Initial Load Frame Time
- [ ] 1.1: Defer initial text loading until frame timer is running
- [ ] 1.2: Load file content but don't set `setPlainText()` immediately
- [ ] 1.3: Use timer to call `setPlainText()` in chunks for better frame distribution

### Phase 2: Optimize Find & Replace Frames
- [ ] 2.1: Make `replace_all()` process text in ~1000 line chunks
- [ ] 2.2: Add cancellable operation with progress dialog
- [ ] 2.3: Show replacement count as it progresses

### Phase 3: Optimize Highlighting Frames
- [ ] 3.1: Measure current block highlighting time per frame
- [ ] 3.2: Reduce `highlight_remaining_blocks()` to only use ~14ms per frame
- [ ] 3.3: Adaptive block count based on frame time measurement

### Phase 4: Optimize Scroll Rendering
- [ ] 4.1: Cache which blocks are currently visible
- [ ] 4.2: Only call `highlight_visible_blocks()` if viewport changed
- [ ] 4.3: Skip redundant highlight calls during rapid scrolling

### Phase 5: Profile & Document
- [ ] 5.1: Test all operations with frame timer enabled
- [ ] 5.2: Record Week 9 timings in new file
- [ ] 5.3: Document every frame drop with explanation
- [ ] 5.4: Answer architecture questions

## Expected Improvements

| Operation | Current | Target | Method |
|-----------|---------|--------|--------|
| Open large.txt | 16,187ms | <16ms | Defer to background frames |
| Find & Replace large | 18,206ms | <16ms | Process in chunks |
| Scroll large | 33ms | <16ms | Cache & optimize |

## Notes

- No multithreading (per user requirement)
- All work distributed across frames using QTimer
- Frame timer actively measures and reports frame times
- Operations will appear to take same wall-clock time but distribute better
