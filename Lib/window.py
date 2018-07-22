#!/usr/bin/env python3
# -*-coding: utf-8 -*-

import tkinter as tk
import cv2
from PIL import Image, ImageTk

from Lib.video import VideoCap

class Window:
    def __init__(self, txt, width=640, height=480):
        self.txt = txt
        self.cap = VideoCap(0, width,height)
        self.root = tk.Tk()
        self.root.bind('<Escape>', lambda e: self.root.quit())
        self.root.bind('<Up>', lambda e: self.cap.white_th_up())
        self.root.bind('<Down>', lambda e: self.cap.white_th_dw())
        self.root.title(txt['top'])
        #root.geometry('640x480')

        tk.Label(text=txt['camera']).grid(row=0, column=0, sticky=tk.W)

        self.lmain = tk.Label(self.root)
        self.lmain.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)

        self.button_txt = tk.StringVar()
        self.button_txt.set(txt['button'])
        button = tk.Button(textvariable=self.button_txt, bg='green',font=("",20), command=self.changeLabel)
        button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)

        tk.Label(self.root, text=txt['c/s'], fg='red').grid(row=3, column=0, sticky=tk.W)
        self.eval_txt1 = tk.StringVar()
        self.eval_txt1.set(txt['none'])
        tk.Label(self.root, textvariable=self.eval_txt1).grid(row=3, column=1, sticky=tk.W)
        tk.Label(self.root, text=txt['total'], fg='red',font=("",20)).grid(row=4, column=0, sticky=tk.W)
        self.total_txt = tk.StringVar()
        self.total_txt.set(txt['none'])
        tk.Label(self.root, textvariable=self.total_txt,font=("",20)).grid(row=4, column=1, sticky=tk.W)
        tk.Label(self.root, text=txt['comment'], fg='red').grid(row=5, column=0, sticky=tk.W)
        self.eval_txt2 = tk.StringVar()
        self.eval_txt2.set(txt['none'])
        tk.Label(self.root, textvariable=self.eval_txt2).grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)
        
    def show_frame(self):
        if self.cap.read():
            frame = self.cap.getRect()
        else:
            pass
        
        frame = cv2.flip(frame, 1)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        self.lmain.imgtk = imgtk
        self.lmain.configure(image=imgtk)
        self.lmain.after(10, self.show_frame)

    def changeLabel(self):
        if self.eval_txt1.get() == self.txt['none']:
            self.eval_txt1.set('GOOD/LARGE')
            self.eval_txt2.set('THIS IS VERY NICE!!')
            self.total_txt.set('100 pt')
            self.button_txt.set(self.txt['clear'])
            self.cap.write('./data')
        else:
            self.eval_txt1.set(self.txt['none'])
            self.eval_txt2.set(self.txt['none'])
            self.total_txt.set(self.txt['none'])
            self.button_txt.set(self.txt['button'])

