.. _install:

Modipyd のインストール
====================================
このドキュメントでは *Modipyd* のインストール方法について書いています。

必要なソフトウェアやライブラリ
-----------------------------------
Modipyd に必要なのは **Python 2.4** かそれ以降のバージョンだけです。他のライブラリやモジュールをインストールする必要はありません。

Python は `http://www.python.org <http://www.python.org>`_ から入手できます。もし、あなたの OS が Linux や Mac OS X なら、Python は最初からインストールされているでしょう。

最新バージョンをインストール
---------------------------------------------------
1. まずは最新バージョンの Modipyd をダウンロードしてください（\ `zip`_ 形式か `tar.gz`_ 形式の圧縮ファイルで配布しています）
2. ダウンロードしたファイルを解凍します（例：zip 形式の場合、\ ``unzip ishikawa-modipyd-XXX.zip``\ 、tar.gz 形式の場合、\ ``tar xzvf ishikawa-modipyd-XXX.tar.gz``\ ）
3. ファイルを解凍して出来たディレクトリに移動します（例：\ ``cd ishikawa-modipyd-XXX``\ ）
4. シェルプロンプトで ``sudo python setup.py install`` を実行します

上記ステップで以下のものがインストールされます：

* :mod:`modipyd` パッケージが Python の :file:`site-packages` 以下にインストールされます
* :command:`modipyd`, :command:`pyautotest` のふたつのコマンドがインストールされます

これでインストールは完了です。\ :ref:`チュートリアル <quick>`\ に進みましょう。

.. _zip: http://github.com/ishikawa/modipyd/zipball/release-1-0-rc1
.. _tar.gz: http://github.com/ishikawa/modipyd/tarball/release-1-0-rc1
