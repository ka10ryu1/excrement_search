#!/usr/bin/env python3
# -*-coding: utf-8 -*-

import tkinter as tk
import cv2
from PIL import Image, ImageTk

import Tools.imgfunc as I
import Tools.func as F
import Lib.color_trans as C
from Lib.window import Window

white = '                           '

txt = {
    'none':'データなし',
    'top':'EXCREMENT SEARCH',
    'camera':'Video capture (<Escape> Quit, <Enter> Capture)',
    'button':'[あなたの作品を確認してみましょう！]',
    'clear': '[' + white + 'リ セ ッ ト ' + white + ']',
    'c/s':'色/形',
    'total':'総合得点',
    'comment':'コメント'
}


if __name__ == '__main__':
    w = Window(txt)
    w.show_frame()
    w.root.mainloop()

