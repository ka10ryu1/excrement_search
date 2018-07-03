# 概要

成果物から情報を取得する

# 動作環境

## $ cat /etc/issue

- **Ubuntu** 16.04.4 LTS

## $ Tools/version_check.py

- **Python** 3.6
- **pip** 10.0.1
- **numpy** 1.13.0
- **opencv-python** 3.4.1.15
- **matplotlib** 2.2.2
- **Pillow** 5.1.0

## ハードウェア

- USBカメラ(UVC規格で640x480の動画撮影可能なもの)

# ファイル構成

## 生成方法

```console
$ ls `find ./ -maxdepth 3 -type f -print` | xargs grep 'help = ' --include=*.py >& log.txt
$ tree >& log.txt
```

## ファイル

```console
.
├── LICENSE
├── Lib
│   └── color_trans.py < 取得した画像に関する変換など
├── README.md
├── Tools
├── capture.py < Webカメラから画像を取得する
└── clean_all.sh
```

# チュートリアル

## USBカメラを使って成果物を取得する

以下を入力するとカメラキャプチャが開始される。「s」で画像を保存、「w」「x」で便器のしきい値を変更、「Esc」でプログラムを終了する。オプション引数を確認する場合は`-h`を追加して実行する。

```console
$ ./capture.py
```
