#! python3
# mcb.pyw - Saves and loads pieces of text to the clipboard.
# Usage: py.exe mcb.pyw save <keyword> - Saves clipboard to keyword.
#        py.exe mcb.pyw delete <keyword> - delete keyword from shelve.
#        py.exe mcb.pyw <keyword> - loads keyword to clipboard.
#        py.exe mcb.pyw list - loads all keywords to clipboard.
#        py.exe mcb.pyw delete - delete all keyword.

import shelve, pyperclip, sys
mcbShelf = shelve.open('mcb')
# Save clipboard comtent.
if len(sys.argv) == 3:
    if sys.argv[1].lower() == 'save':
        mcbShelf[sys.argv[2]] = pyperclip.paste()
    if sys.argv[1].lower() == 'delete':
        del mcbShelf[sys.argv[2]]
# List key words and load contents.
if len(sys.argv) == 2:
    if sys.argv[1].lower() == 'list':
        pyperclip.copy(list(mcbShelf.keys()))
    elif sys.argv[1].lower() == 'delete':
        mcbShelf.clear()
    elif sys.argv[1] in mcbShelf:
        pyperclip.copy(mcbShelf[sys.argv[1]])
mcbShelf.close()
