#!/usr/bin/env python3
# -*-coding: utf-8 -*-
# pylint: disable=missing-docstring,invalid-name
import time
import argparse
import cv2
import numpy as np

from capture import resize, full_screen, add_text, vline, hline, select_key


def command():
    parser = argparse.ArgumentParser(description=help)
    parser.add_argument('--rate', type=float, default=1,
                        help='表示する画像サイズの倍率 [default: 1]')
    parser.add_argument('--white_thresh', type=int, default=115,
                        help='白切り抜きのしきい値 [default: 115]')
    parser.add_argument('--lower', action='store_true',
                        help='select timeoutが発生する場合に画質を落とす')
    return parser.parse_args()


def get_white(img, lower, upper):
    b, g, r = cv2.split(img.copy())
    b = cv2.inRange(b, lower, upper)
    g = cv2.inRange(g, lower, upper)
    r = cv2.inRange(r, lower, upper)
    bg = cv2.bitwise_and(b, g)
    bgr = cv2.bitwise_and(bg, r)
    bgr = cv2.bitwise_not(bgr)
    return bgr


def get_red(img, th1=40, th2=50, th3=30):
    def _get_hsv(_img, _lower, _upper):
        _img = cv2.cvtColor(_img, cv2.COLOR_BGR2HSV_FULL)
        _img = cv2.inRange(_img, _lower, _upper)
        return _img

    lower = np.array([0, th1, th2])
    upper = np.array([th3, 255, 255])
    img1 = _get_hsv(img, lower, upper)

    lower = np.array([225, th1, th2])
    upper = np.array([255, 255, 255])
    img2 = _get_hsv(img, lower, upper)

    return img1 + img2


def get_contours(src, mask, k_size=3, sum_max=5000, num=5,
                 color=(0, 255, 255), thickness=2):
    kernel = np.ones((k_size, k_size), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    contours = cv2.findContours(
        mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )[0]

    cnt_size = [[i, cv2.contourArea(cnt)]
                for i, cnt in enumerate(contours) if cv2.contourArea(cnt) < sum_max]
    cnt_size.sort(key=lambda x: x[-1], reverse=True)
    s_cnt = [contours[i] for i, _ in cnt_size[:int(num)]]
    return cv2.drawContours(src.copy(), s_cnt, -1, color, thickness)


def get_avg_color(img, mask, color=(255, 255, 255), font=cv2.FONT_HERSHEY_SIMPLEX):
    masked = cv2.bitwise_and(img, img, mask=mask)
    b, g, r = cv2.split(masked)
    b_val = int(np.mean(b))
    g_val = int(np.mean(g))
    r_val = int(np.mean(r))
    text = 'B:{}, G:{}, R:{}'.format(b_val, g_val, r_val)
    h, w, ch = img.shape
    bk = np.zeros((h * 2, w * 2, ch), dtype=np.uint8)
    cv2.putText(bk, text, (5, h * 2 - 10), font, 1, color, 1, cv2.LINE_AA)
    return cv2.add(img, resize(bk, 0.5))


def main(args):
    # カメラセッティング
    cap = cv2.VideoCapture(0, cv2.CAP_V4L)
    rate = args.rate
    if args.lower:
        print('MODE: LOW')
        cap.set(3, 200)
        cap.set(4, 200)
        cap.set(5, 5)

    A, B, C, D = 0, 1, 2, 3
    txt = ('RGB', 'Mono', 'Contour', 'Average')
    st = time.time()
    imgs = [0, 0, 0, 0]
    bk = None
    v_img = None
    h_img = None
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
            v_img = vline(frame, 3)

        imgs[0] = frame
        dilate = cv2.dilate(frame, np.ones((5, 5), dtype=np.uint8))
        white = get_white(dilate, args.white_thresh, 255)
        red = get_red(dilate)
        imgs[1] = cv2.merge([white, bk, red])
        imgs[2] = get_avg_color(get_contours(frame, white), white)
        imgs[3] = get_avg_color(get_contours(frame, red), red)

        print('+{:.3f}: imgs'.format((time.time() - st) * 1000))

        img1 = add_text(resize(imgs[A], 2.8), txt[A], 35)
        img2 = np.vstack([
            imgs[B],
            v_img,
            imgs[C],
            v_img,
            imgs[D]
        ])

        if h_img is None:
            h_img = hline(img1, 5)

        print('+{:.3f}: fix'.format((time.time() - st) * 1000))

        img = np.hstack([h_img, img1, h_img, img2, h_img])
        full_screen('frame', resize(img, rate))

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
    print('[ q ] Change top image')
    print('[ a ] Change middle image')
    print('[ z ] Change bottom image')
    print('[ s ] Reset')
    main(command())
