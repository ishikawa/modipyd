.. Modipyd documentation master file

Modipyd: Autotest for Python, and more
=======================================

**Modipyd** は石川尊教（いしかわ・たかのり）が開発した、\ `Python`_ モジュールの依存性解析、および、モジュールの変更を監視するためのフレームワークです。\ `MIT ライセンス`_\ のもとで配布しています。

**このプロジェクトの目標：**

* `ZenTest の autotest <http://www.zenspider.com/ZSS/Products/ZenTest/>`_ のような、ユニットテストの実行を自動化するためのツール **pyautotest** を Python プログラム向けに提供する
* モジュールが変更されたときに実行するアクションを柔軟にカスタマイズできるように、プラグインの仕組みを提供する
* バイトコード解析、モジュールの依存性解析、およびモジュールの変更を監視するための API を提供する

**ユーザー向けのリソース**

* *最新のリリースをダウンロード*\ ：\ `バージョン 1.0 のリリース候補 <http://metareal.lighthouseapp.com/projects/17658-modipyd/milestones/current>`_\ を近いうちに公開予定です
* `バグ報告や要望はこちら <http://metareal.lighthouseapp.com/projects/17658-modipyd/tickets/new>`_\ ：バグ報告や要望はリンク先のフォームからおねがいします。\ Lighthouse_ という海外のサービスを利用しているため、インターフェースは英語になっていますが、報告する内容は日本語でもかまいません（そのうち、より詳しい手順の解説を書く予定です）。

**このプロジェクトに興味がある開発者の方へ：**

* `ソースコードをみる <http://github.com/ishikawa/modipyd/>`_\ ： Modipyd のソースコードは GitHub_ で管理しています。\ `こちら <http://github.com/ishikawa/modipyd/>`_\ から最新のソースコードを閲覧、取得できます。
* `チケットやマイルストーンをみる <http://metareal.lighthouseapp.com/projects/17658/>`_\ ：バグ報告や要望はリンク先のフォームからおねがいします。

関連リンク
-----------------------------------
* `ZenTest: Automated test scaffolding for Ruby <http://www.zenspider.com/ZSS/Products/ZenTest/>`_ Modipyd を開発するきっかけともなったオリジナルの autotest です。
* `pyautotest <http://github.com/dbr/pyautotest/>`_ Unittest notifier: Notification of unittest passes and failures, via Growl. Like autotest for Python
* `Is there something like 'autotest' for Python unittests? - Stack Overflow <http://stackoverflow.com/questions/108892/is-there-something-like-autotest-for-python-unittests>`_


.. toctree::
   :maxdepth: 2

索引と検索
-----------------------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _Python: http://www.python.org/
.. _MIT ライセンス: http://www.opensource.org/licenses/mit-license.php
.. _GitHub: http://github.com/
.. _Lighthouse: http://lighthouseapp.com/
