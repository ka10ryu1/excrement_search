#!/usr/bin/env python3
# -*-coding: utf-8 -*-
#
help = 'Webカメラから画像を取得する'
#

import cv2
import time
import argparse
import numpy as np

import Tools.imgfunc as I
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


def getRedArea(img, split_size=4, ch=3, th_b=40, th_g=40, th_r=90, color=(255, 255, 0)):
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


def main(args):
    # カメラセッティング
    cap = cv2.VideoCapture(args.channel)
    num = 0
    cap.set(3, 200)
    cap.set(4, 200)
    cap.set(5, 5)

    scale = [0.1, 10]
    while(True):
        # カメラキャプチャ
        ret, frame = cap.read()
        if not ret:
            time.sleep(1)
            continue

        # 画素を減らす
        img2 = I.cnv.resize(frame, scale[0], cv2.INTER_CUBIC)
        # 便器（画像の白い部分）を黒く塗りつぶす
        img3 = white2black(img2)
        # 平均画像の値と生成
        val, aveImg = getAverageImg(img3)
        # 血便エリアの検出
        redImg = getRedArea(img2)

        # 表示用画像をリサイズ
        img1 = I.cnv.resize(frame, scale[0]*scale[1], cv2.INTER_CUBIC)
        # img2 = I.cnv.resize(img2, scale[1], cv2.INTER_CUBIC)
        img3 = I.cnv.resize(img3, scale[1], cv2.INTER_CUBIC)
        img4 = I.cnv.resize(aveImg, scale[1], cv2.INTER_CUBIC)
        img5 = I.cnv.resize(redImg, scale[1], cv2.INTER_CUBIC)
        shape = img3.shape
        img1 = img1[:shape[0], :shape[1], :shape[2]]
        # print(img1.shape, img2.shape, img3.shape, img4.shape, img5.shape)
        # 表示用に画像を連結
        img = np.vstack([np.hstack([img1, img3]), np.hstack([img5, img4])])
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
