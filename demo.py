#!/usr/bin/env python3
# -*-coding: utf-8 -*-

from Lib.window import Window

txt = {
    'top': 'EXCREMENT SEARCH',
    'camera': 'Video capture\n  -  <Escape> Quit\n  -  <Enter> Capture\n  -  <Up>/<Down> white threshold change',
    'status_none': 'get data ...',
    'status_write': 'write'
}

if __name__ == '__main__':
    w = Window(txt, lower=True)
    w.show_frame()
    w.root.mainloop()
