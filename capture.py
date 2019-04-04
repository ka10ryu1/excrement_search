#!/usr/bin/env python3
# -*-coding: utf-8 -*-
# pylint: disable=missing-docstring
import time
import argparse
import cv2
import numpy as np


def command():
    parser = argparse.ArgumentParser(description=help)
    parser.add_argument('--rate', type=float, default=1,
                        help='表示する画像サイズの倍率 [default: 1]')
    parser.add_argument('--lower', action='store_true',
                        help='select timeoutが発生する場合に画質を落とす')
    return parser.parse_args()


def resize(img, rate, flg=cv2.INTER_NEAREST):
    if rate < 0:
        return img

    size = (int(img.shape[1] * rate), int(img.shape[0] * rate))
    return cv2.resize(img, size, flg)


def fullscreen(winname, img):
    cv2.namedWindow(winname, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(
        winname, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN
    )
    cv2.imshow(winname, img)


def add_text(img, text, h, color=(255, 255, 255), font=cv2.FONT_HERSHEY_SIMPLEX):
    bk = vline(img, h)
    cv2.putText(bk, text, (5, h - 5), font, 1, color, 1, cv2.LINE_AA)
    dst = np.vstack([img, bk])
    return dst


def vline(img, h):
    w = img.shape[1]
    ch = 1
    if img.shape[-1] == 3:
        ch = 3

    return np.zeros((h, w, ch), dtype=np.uint8)


def hline(img, w):
    h = img.shape[0]
    ch = 1
    if img.shape[-1] == 3:
        ch = 3

    return np.zeros((h, w, ch), dtype=np.uint8)


def select_key(A, B, C, D, w_time=5):
    key = cv2.waitKey(w_time) & 0xFF
    # Escでループを抜ける
    if key == 27:
        print('exit!')
        return False, A, B, C, D
    # sキーで画像を保存する
    elif key == ord('q'):
        return True, B, A, C, D
    elif key == ord('a'):
        return True, C, B, A, D
    elif key == ord('z'):
        return True, D, B, C, A
    elif key == ord('s'):
        return True, 0, 1, 2, 3

    return True, A, B, C, D


def main(args):
    # カメラセッティング
    cap = cv2.VideoCapture(0)
    rate = args.rate
    if args.lower:
        print('MODE: LOW')
        cap.set(3, 200)
        cap.set(4, 200)
        cap.set(5, 5)
        rate = 0.8

    A, B, C, D = 0, 1, 2, 3
    txt = ('RGB color', 'Blue', 'Green', 'Red')
    st = time.time()
    imgs = [0, 0, 0, 0]
    bk = None
    v_img = None
    h_img = None
    while True:
        # カメラキャプチャ
        try:
            ret, frame = cap.read()
        except:
            print('except')
            time.sleep(1)
            continue

        if not ret:
            print('not ret')
            time.sleep(1)
            continue

        print('+{:.3f}: cap'.format((time.time() - st) * 1000))
        b, g, r = cv2.split(frame)
        if bk is None:
            bk = np.zeros_like(b, dtype=np.uint8)
            v_img = vline(frame, 1)

        imgs[0] = frame
        imgs[1] = cv2.merge([b, bk, bk])
        imgs[2] = cv2.merge([bk, g, bk])
        imgs[3] = cv2.merge([bk, bk, r])

        print('+{:.3f}: imgs'.format((time.time() - st) * 1000))

        img1 = add_text(resize(imgs[A], 2.8), txt[A], 31)
        img2 = np.vstack([
            imgs[B],
            v_img,
            imgs[C],
            v_img,
            imgs[D]
        ])

        if h_img is None:
            h_img = hline(img1, 1)

        print('+{:.3f}: fix'.format((time.time() - st) * 1000))

        # print(img1.shape, img2.shape, mini1.shape)
        img = np.hstack([img1, h_img, img2])
        fullscreen('frame', resize(img, rate))

        print('+{:.3f}: view'.format((time.time() - st) * 1000))

        # キー入力判定
        key, A, B, C, D = select_key(A, B, C, D)
        print('{:.3f}'.format((time.time() - st) * 1000))
        st = time.time()
        if not key:
            break

    # 終了処理
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    print('Key bindings')
    print('[Esc] Exit')
    print('[ w ] White threshold UP')
    print('[ a ] Get value')
    print('[ s ] Save image')
    print('[ x ] White threshold DOWN')
    main(command())
