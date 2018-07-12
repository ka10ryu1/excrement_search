#!/usr/bin/env python3
# -*-coding: utf-8 -*-
#
help = 'Webカメラから画像を取得する'
#

import cv2
import time
import argparse

import Tools.imgfunc as I
import Tools.func as F
import Lib.color_trans as C


def command():
    parser = argparse.ArgumentParser(description=help)
    parser.add_argument('-c', '--channel', type=int, default=0,
                        help='使用するWebカメラのチャンネル [default: 0]')
    parser.add_argument('-w', '--white_threshold', type=int, default=175,
                        help='便器しきい値 [default: 175]')
    parser.add_argument('-o', '--out_path', default='./capture/',
                        help='画像の保存先 (default: ./capture/)')
    parser.add_argument('-r', '--img_rate', type=float, default=1,
                        help='表示する画像サイズの倍率 [default: 1]')
    parser.add_argument('--lower', action='store_true',
                        help='select timeoutが発生する場合に画質を落とす')
    args = parser.parse_args()
    F.argsPrint(args)
    return args


def main(args):
    # カメラセッティング
    cap = cv2.VideoCapture(args.channel)
    scale = (0.10, 5)
    w_th = args.white_threshold
    if args.lower:
        cap.set(3, 200)
        cap.set(4, 200)
        cap.set(5, 5)
        scale = (0.5, 5)

    print('white threshold: {}'.format(w_th))
    while(True):
        # カメラキャプチャ
        ret, frame = cap.read()
        if not ret:
            time.sleep(1)
            continue

        # 画素を減らす
        img2 = I.cnv.resize(frame, scale[0], cv2.INTER_CUBIC)
        # 便器（画像の白い部分）を黒く塗りつぶす
        img3 = C.white2black(img2, w_th)
        # 平均画像の値と生成
        val, aveImg = C.getAverageImg(img3)
        # 血便エリアの検出
        #redImg = C.getRedArea(img2)
        # 成果物の位置と数を検出
        exc_num, rectImg = C.getRect(img3.copy())

        # 表示用画像をリサイズ
        img1 = I.cnv.resize(frame, scale[0]*scale[1], cv2.INTER_CUBIC)
        # img2 = I.cnv.resize(img2, scale[1], cv2.INTER_CUBIC)
        img3 = I.cnv.resize(img3, scale[1], cv2.INTER_CUBIC)
        img4 = I.cnv.resize(aveImg, scale[1], cv2.INTER_CUBIC)
        # img5 = I.cnv.resize(redImg, scale[1], cv2.INTER_CUBIC)
        img5 = I.cnv.resize(rectImg, scale[1], cv2.INTER_CUBIC)
        shape = img3.shape
        img1 = img1[:shape[0], :shape[1], :shape[2]]
        # print(img1.shape, img2.shape, img3.shape, img4.shape, img5.shape)
        # 表示用に画像を連結
        img = I.cnv.vhstack([img1, img5, img3, img4], (2, 2))
        cv2.imshow('frame', img)

        # キー入力判定
        key = cv2.waitKey(20) & 0xff
        # Escでループを抜ける
        if key == 27:
            print('exit!')
            break
        # sキーで画像を保存する
        elif key == ord('s'):
            print('capture!', I.io.write(args.out_path, 'cap-', img))
        elif key == ord('w'):
            w_th += 5
            print('white threshold: {}'.format(w_th))
        elif key == ord('x'):
            w_th -= 5
            print('white threshold: {}'.format(w_th))

    # 終了処理
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    print('Key bindings')
    print('[Esc] Exit')
    print('[ s ] Save image')
    main(command())
