Command to run coverage: pytest --cov=main

I achieved 96% test coverage

List of uncovered code:

Line 2078-2084  This is the code for closing a file that also triggers closing a view panel when the file also needs saved.  This isn't tested because it is very complex to set up.

Lines 2294-2296  This is an exception handler for catching errors that happen when trying to write to a file.  This could be things like permission error, path not found, or even that the disk is full.  This is hard to test because it is hard to recreate one of those errors.

Lines 2385-2390  This code checks if there are any instances of a file open when it is being deleted and it closes those file.  This is hard to test because it requires a complicated multi view setup.

Line 2498-2517  This code is similar to the code before, but is for when a folder is deleted.  It checks if any file in that folder is opened.  And it is hard to test because it requires a very mature state.

Line 2615  This code checks for different extensions on a file right after it is saved and ensures that the syntax is highlighted.  This is not tested because it requires me to Save As a file and change the file to have a different extension.

Line 2700-2711  This is the code for ensuring everything is saved before allowing the close of the application.  This is untested because it requires a complex state with multiple views and lots of files opened.

Line 2762  This is a small piece of the cursor updating functionality.  This is hard to test because it requires the cursor_label to not exist in order to test.

Line 2792-2793  This is the code for catching an exception when trying to find something.  This isn't tested because it is hard to create an exception when trying to find something.

Line 2996-2998  This is the code that runs when a user chooses to save after trying to close, but the save fails.  This isn't tested because it is really hard to set up this senario.

Line 3006-3010  This is the main function entry point.  This isn't tested because my tests don't actually call the main function.  They create the TextEditor directly.