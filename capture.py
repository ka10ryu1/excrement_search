#!/usr/bin/env python3
# -*-coding: utf-8 -*-
# pylint: disable=missing-docstring,invalid-name
import time
import argparse
import cv2
import numpy as np

from pathlib import Path


def command():
    parser = argparse.ArgumentParser(description='USB Camera Test')
    parser.add_argument('--id', type=int, default=0,
                        help='USB Camera ID [default: 0]')
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


def save_all_img(save_dir, imgs):
    save_dir = Path(save_dir)
    if not save_dir.exists():
        save_dir.mkdir(parents=True)

    for i, img in enumerate(imgs):
        path = save_dir / 'img_{:04}.jpg'.format(i)
        cv2.imwrite(str(path), img)


def full_screen(winname, img):
    cv2.namedWindow(winname, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(
        winname, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN
    )
    cv2.imshow(winname, img)


def add_text(img, text, h=10, color=(255, 255, 255), font=cv2.FONT_HERSHEY_SIMPLEX):
    bk = vline(img, h)
    cv2.putText(bk, text, (10, h - 10), font, 1, color, 1, cv2.LINE_AA)
    dst = np.vstack([img, bk])
    return dst


def add_text_direct(img, text, h=10, color=(255, 255, 255), font=cv2.FONT_HERSHEY_SIMPLEX):
    cv2.putText(img, text, (10, h - 10), font, 1, color, 1, cv2.LINE_AA)
    return img


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
        return 1, A, B, C, D
    # sキーで画像を保存する
    elif key == ord('q'):
        return 0, B, A, C, D
    elif key == ord('a'):
        return 0, C, B, A, D
    elif key == ord('z'):
        return 0, D, B, C, A
    elif key == ord('s'):
        return 0, 0, 1, 2, 3
    elif key == ord('x'):
        return 10, A, B, C, D

    return 0, A, B, C, D


def main(args):
    # カメラセッティング
    cap = cv2.VideoCapture(args.id, cv2.CAP_V4L)
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
    cnt = 9999
    save_imgs = list()
    while True:
        # カメラキャプチャ
        try:
            ret, frame = cap.read()
        except Exception as e:
            print('except', e)
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
        if cnt > ~ 0 and cnt <= 120:
            img = add_text_direct(
                img, 'REC {:03}'.format(cnt), 40, color=(0, 0, 255)
            )
            save_imgs.append(img)
            cnt += 1

        full_screen('frame', resize(img, rate))

        print('+{:.3f}: view'.format((time.time() - st) * 1000))

        # キー入力判定
        key, A, B, C, D = select_key(A, B, C, D)
        print('{:.3f}'.format((time.time() - st) * 1000))
        st = time.time()
        if key == 1:
            break
        elif key == 10:
            save_imgs = list()
            cnt = 0

    # 終了処理
    save_all_img('out', save_imgs)
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    print('Key bindings')
    print('[Esc] Exit')
    print('[ q ] Change top image')
    print('[ a ] Change middle image')
    print('[ z ] Change bottom image')
    print('[ s ] Reset')
    print('[ x ] Rec start')
    main(command())
