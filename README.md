# gedit-filebrowser-utils

### Select current file
Press (that's tricky) <kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>F</kbd> to select the current file in the file browser panel.

This plugin will:
* Expand its collapsed parent directories (it's asynchronous)
* Scroll the view to make the target row visible
* Set focus on the view

This plugin won't (currently):
* Exit bookmarks view
* Change the root directory so as to make it possible to select the file

### Select parent directory
Press <kbd>Alt</kbd> + <kbd>P</kbd> to jump to parent directory of the currently selected file in the file browser panel.

Currently this plugin won't change the root directory if no parent visible.

