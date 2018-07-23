#!/usr/bin/env python3
# -*-coding: utf-8 -*-

import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk

from Lib.video import VideoCap


class Window:
    def __init__(self, txt, width=640, height=480, lower=False):
        self.txt = txt
        self.cap = VideoCap(0, width=width, height=height, lower=lower)
        print(self.cap.status())
        self.root = tk.Tk()
        self.root.bind('<Escape>', lambda e: self.root.quit())
        self.root.bind('<Up>', lambda e: self.cap.white_th_up())
        self.root.bind('<Down>', lambda e: self.cap.white_th_dw())
        self.root.title(txt['top'])

        tk.Label(text=txt['camera']).grid(row=0, column=0, sticky=tk.W)

        self.lmain = tk.Label(self.root)
        self.lmain.grid(
            row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E
        )

        self.status_txt = tk.StringVar()
        self.status_txt.set(txt['status_none'])
        status = tk.Label(self.root, textvariable=self.status_txt)
        status.grid(row=3, column=1, sticky=tk.W)

    def _cv2pillow(self, img):
        cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        return ImageTk.PhotoImage(image=img)

    def show_frame(self):
        self.cap.read()
        self.cap.getRectAndColor()
        imgtk = self._cv2pillow(self.cap.imgs())
        self.lmain.imgtk = imgtk
        self.lmain.configure(image=imgtk)
        self.lmain.after(10, self.show_frame)

    def chechk_color(self, color):
        trueVal = (140, 70, 70)
        print(trueVal, color)
        diff_pow = [(i - j)**2 for i, j in zip(trueVal, color)]
        return np.max([1, np.sum(diff_pow)**0.5])

    def changeLabel(self):
        if self.eval_txt1.get() == self.txt['none']:
            colordiff = self.chechk_color(self.cap.ave_color)
            #colordiff = self.chechk_color((140,70,70))
            pt = 100/colordiff
            print(pt)
            self.eval_txt1.set(self.cap.value())
            self.eval_txt2.set('THIS IS VERY NICE!!')
            self.total_txt.set(str(pt))
            self.button_txt.set(self.txt['clear'])
            self.cap.write('./data')
        else:
            self.eval_txt1.set(self.txt['none'])
            self.eval_txt2.set(self.txt['none'])
            self.total_txt.set(self.txt['none'])
            self.button_txt.set(self.txt['button'])
