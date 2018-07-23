#!/usr/bin/env python3
# -*-coding: utf-8 -*-

import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk

from Lib.video import VideoCap
import Tools.func as F


class Window:
    def __init__(self, txt, width=640, height=480, lower=False, out_path='./data'):
        self.txt = txt
        self.cap = VideoCap(0, width=width, height=height, lower=lower)
        print(self.cap.status())
        self.root = tk.Tk()
        self.root.bind('<Escape>', lambda e: self.root.quit())
        self.root.bind('<Up>', lambda e: self.cap.white_th_up())
        self.root.bind('<Down>', lambda e: self.cap.white_th_dw())
        self.root.title(txt['top'])

        tk.Label(text=txt['camera'], justify='left').grid(row=0, column=0)

        self.lmain = tk.Label(self.root)
        self.lmain.grid(row=1, column=0)

        self.status_txt = tk.StringVar()
        self.status_txt.set(txt['status_none'])
        tk.Label(self.root, textvariable=self.status_txt).grid(row=2, column=0)

        self.num = 0
        self.out_path = out_path

    def _cv2pillow(self, img):
        cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        return ImageTk.PhotoImage(image=img)

    def show_frame(self, delay=20):
        self.cap.read()
        if self.num > 10:
            self.changeLabel(0)
            self.write()
        else:
            self.changeLabel(1)

        imgtk = self._cv2pillow(self.cap.imgs())
        self.lmain.imgtk = imgtk
        self.lmain.configure(image=imgtk)
        self.lmain.after(delay, self.show_frame)
        self.num += 1

    def write(self):
        self.cap.getRectAndColor()
        path = F.getFilePath(self.out_path, 'param', '.txt')
        trueVal = (140, 70, 70)
        with open(path, 'w') as f:
            f.write(str(trueVal) + '\n')
            f.write(str(self.cap.ave_color) + '\n')
            f.write(str(self.cap.exc_shape) + '\n')

        self.num = 0

    def chechk_color(self, color):
        print(trueVal, color)
        diff_pow = [(i - j)**2 for i, j in zip(trueVal, color)]
        return np.max([1, np.sum(diff_pow)**0.5])

    def changeLabel(self, num):
        if num == 0:
            self.status_txt.set(self.txt['status_write'])
        else:
            self.status_txt.set(self.txt['status_none'])
