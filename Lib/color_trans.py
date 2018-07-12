#!/usr/bin/env python3
# -*-coding: utf-8 -*-
#
help = '取得した画像に関する変換など'
#

import cv2
import numpy as np

import Tools.imgfunc as I


def white2black(img, thresh=125, max_val=250):
    # マスク用のグレースケール画像を用意する
    mask = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 白っぽい部分を白く、それ以外を黒くする
    ret, mask = cv2.threshold(
        cv2.bitwise_not(mask), thresh, max_val, cv2.THRESH_BINARY
    )
    # 白黒反転し、もう一度白っぽい部分を白く、それ以外を黒くする
    # これによって塗りつぶしたいエリア(便器)のマスクが作成できる
    ret, mask_inv = cv2.threshold(
        cv2.bitwise_not(mask), thresh, max_val, cv2.THRESH_BINARY
    )
    # マスク画像を使って便器(白)部分を黒く塗りつぶす
    return cv2.bitwise_and(img, img, mask=mask)


def getAverageImg(img):
    # 画像の平均値とそれを可視化した画像を返す
    # ほぼ黒(20以下)の画素に対して計算する
    def ave(img, thresh=20):
        sum1 = np.sum(img[img > thresh])
        sum2 = len(img[img > thresh])
        if sum2 == 0:
            return 0

        return int(np.min((250, sum1//sum2)))

    # BGRで画像を分割する
    b, g, r = cv2.split(img)
    # 各色の平均値を計算する
    value = (ave(b), ave(g), ave(r))
    return value, I.blank.blank(img.shape, value)


def rgbMultplySum(img, th):
    # BGRで画像を分割する
    b, g, r = cv2.split(img)
    # しきい値を超えた部分を1,それ以外を0とすることで、
    # 要素の掛け算をするとすべてのしきい値を満たす画素だけ抽出できる
    mul = np.multiply(np.multiply(b < th[0], g < th[1]), r > th[2])
    # すべての要素を満たす画素の数を返す
    return np.sum(mul)


def getRedArea(img, split_size=4, ch=3, th_b=30, th_g=30, th_r=100, color=(255, 255, 0)):
    # 血便を検出するために画像を分割する
    imgs, split = I.cnv.splitSQ(img, split_size, w_rate=1)
    # 分割した画像に対して
    # 任意のしきい値条件を満たす場合は満たす場合は真っ黒画像に、
    # そうでない場合はそのままにする
    red = [I.blank.black(e.shape[0], e.shape[1], e.shape[2])
           if rgbMultplySum(e, (th_b, th_g, th_r)) == 0 else e
           for i, e in enumerate(imgs)]
    # 最後に分割した画像を連結する
    return I.cnv.vhstack(red, split, img.shape)


def getRect(img, th_1=50, th_2=255, color=(0, 255, 255), line_w=1):
    w, h, _ = img.shape
    area_max = w*h*0.750
    area_min = w*h*0.001
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 2値化
    retval, bw = cv2.threshold(
        gray, th_1, th_2, cv2.THRESH_BINARY | cv2.THRESH_OTSU
    )
    # 輪郭を抽出
    #   contours : [領域][Point No][0][x=0, y=1]
    #   cv2.CHAIN_APPROX_NONE: 中間点も保持する
    #   cv2.CHAIN_APPROX_SIMPLE: 中間点は保持しない
    cnt_img, contours, hierarchy = cv2.findContours(
        bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    num = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > area_max or area_min > area:
            continue

        if len(cnt) > 0:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(img, (x, y), (x+w, y+h), color, line_w)
            num += 1

    return num, img
