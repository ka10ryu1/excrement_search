#!/usr/bin/env python3
# -*-coding: utf-8 -*-
#
help = 'Webカメラから画像を取得する'
#

import cv2
import time
import argparse
import numpy as np

import Tools.imgfunc as IMG
import Tools.func as F


def command():
    parser = argparse.ArgumentParser(description=help)
    parser.add_argument('--channel', '-c', type=int, default=0,
                        help='使用するWebカメラのチャンネル [default: 0]')
    parser.add_argument('-o', '--out_path', default='./capture/',
                        help='画像の保存先 (default: ./capture/)')
    parser.add_argument('--img_rate', '-r', type=float, default=1,
                        help='表示する画像サイズの倍率 [default: 1]')
    args = parser.parse_args()
    F.argsPrint(args)
    return args


def white2black(img, thresh=125, max_val=250):
    thresh = 125
    max_val = 250
    mask = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(
        cv2.bitwise_not(mask), thresh, max_val, cv2.THRESH_BINARY
    )

    ret, mask_inv = cv2.threshold(
        cv2.bitwise_not(mask), thresh, max_val, cv2.THRESH_BINARY
    )

    # Take only region of logo from logo image.
    return cv2.bitwise_and(img, img, mask=mask)


def getAverageImg(img):
    def ave(img, thresh=50):
        sum1 = np.sum(img)
        sum2 = np.sum(img > thresh)
        if sum2 == 0:
            return 0

        return np.min((250, int(sum1/sum2)))

    b, g, r = cv2.split(img)
    value = (ave(b), ave(g), ave(r))
    return ave, IMG.blank(img.shape, value)


def main(args):
    # カメラセッティング
    cap = cv2.VideoCapture(args.channel)
    num = 0
    while(True):
        # カメラキャプチャ
        ret, frame = cap.read()
        if not ret:
            time.sleep(1)
            continue

        # オリジナルイメージ
        img1 = IMG.resize(frame, 0.5)
        # 画素を減らす
        img2 = IMG.resize(frame, 0.05, cv2.INTER_CUBIC)
        # 便器（画像の白い部分）を黒く塗りつぶす
        img3 = white2black(img2)
        # 平均画像の値と生成
        val, aveImg = getAverageImg(img3)

        # 表示用画像をリサイズ
        img2 = IMG.resize(img2, 10, cv2.INTER_CUBIC)
        img3 = IMG.resize(img3, 10, cv2.INTER_CUBIC)
        img4 = IMG.resize(aveImg, 10, cv2.INTER_CUBIC)
        # print(img1.shape, img2.shape, img3.shape, img4.shape)
        # 表示用に画像を連結
        img = np.vstack([np.hstack([img1, img2]), np.hstack([img3, img4])])
        cv2.imshow('frame', img)

        # キー入力判定
        key = cv2.waitKey(20) & 0xff
        # Escでループを抜ける
        if key == 27:
            print('exit!')
            break
        # sキーで画像を保存する
        elif key == ord('s'):
            name = F.getFilePath(
                args.out_path, 'cap-' + str(num).zfill(5), '.jpg'
            )
            num += 1
            print('capture!', name)
            cv2.imwrite(name, img)

    # 終了処理
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    print('Key bindings')
    print('[Esc] Exit')
    print('[ s ] Save image')
    main(command())
