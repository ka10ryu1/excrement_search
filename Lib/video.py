#!/usr/bin/env python3
# -*-coding: utf-8 -*-
#
help = 'Webカメラの画像管理'
#

import cv2
import time
import numpy as np

import Tools.imgfunc as I
import Lib.color_trans as C


class VideoCap(cv2.VideoCapture):
    """
    USBカメラの処理をクラス化したもの
    """

    def __init__(self, usb_ch, width=640, height=480, img_ch=3, lower=False, cap_num=6, interval=0.5, w_th=175):
        self._cap = cv2.VideoCapture(usb_ch)
        self.white_threshold = w_th
        self.exc_shape = []
        if lower:
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 200)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 200)
            self._cap.set(5, 5)
            self.size = (144, 176, img_ch)
        else:
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.size = (height, width, img_ch)

        # 表示・保存用画像の格納先を確保
        self._frame = I.blank.black(self.size)
        self._avrg = I.blank.black(self.size)
        self._rect = I.blank.black(self.size)
        # 保存する画像のチャンネル数
        self.ch = self.size[2]
        # キャプチャ画像のサイズ情報
        self.frame_shape = self._frame.shape
        # インターバル撮影する間隔 [s]
        self.interval = interval
        # 保存用の連番
        self._num = 0
        # 最後に書き込んだ時間
        self._write_time = 0
        # タイマー起動
        self._start = time.time()

    def status(self):
        print('<frame>')
        print('- width:\t', self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        print('- height:\t', self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print('- fps:\t', self._cap.get(5))

    def read(self):
        """
        USBカメラから画像を取得し、インターバルを確認する
        """

        # USBカメラから画像を取得する
        ret, frame = self._cap.read()
        if ret is False:
            return ret

        # フレーム情報の確保
        self._frame = frame
        self.frame_shape = frame.shape

        return ret

    def frame(self, rate=1):
        """
        現在のフレームの取得
        """

        return I.cnv.resize(self._frame, rate)

    def white_th(self, val):
        self.white_threshold += val
        print('wthite threshold:', self.white_threshold)

    def white_th_up(self):
        self.white_th(5)

    def white_th_dw(self):
        self.white_th(-5)

    def getRectAndColor(self):
        img = I.cnv.resize(self._frame, 0.1)
        w2b = C.white2black(img, self.white_threshold)
        val, aveImg = C.getAverageImg(w2b)
        self.ave_color = (val[2], val[1], val[0])
        self._avrg = I.cnv.resize(aveImg, 5)
        exc_shape, rectImg = C.getRect(w2b)
        self._rect = I.cnv.resize(rectImg, 5)
        self._rect = I.cnv.resize(rectImg, 5)
        self.exc_shape = (len(exc_shape), int(np.max(exc_shape)))

    def imgs(self):
        return I.cnv.vhstack([I.cnv.resize(self._frame, 0.5), self._rect, self._avrg])

    def value(self):
        num = str(len(self.exc_shape))
        size = str(np.max(self.exc_shape))
        color = str(self.ave_color)
        return color + '/' + num + '(' + size + ')'

    def intervalCheck(self):
        """
        インターバル撮影の確認
        [out] Trueならインターバルの時間経過
        """

        tm = time.time() - self._start
        if tm > self.interval:
            return True
        else:
            return False

    def view(self, imgs, size, resize):
        """
        任意の画像を任意の行列で結合し任意のサイズで出力
        [in]  imgs: 入力画像リスト
        [in]  size: 結合したい行列情報
        [in]  resize: リサイズの割合
        [out] 結合してリサイズした画像
        """

        self._write_time = time.time()
        return I.cnv.resize(I.cnv.vhstack(imgs, size), resize)

    def write(self, out_path):
        img = np.vstack([I.cnv.resize(self._frame, 0.5), self._rect])
        return I.io.write(out_path, 'cap-', img)

    def release(self):
        """
        終了処理
        """

        self._cap.release()
