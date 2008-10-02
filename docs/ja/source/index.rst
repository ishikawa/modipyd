.. Modipyd documentation master file

Modipyd: Autotest for Python, and more
=======================================

**Modipyd** は石川尊教（いしかわ・たかのり）が開発した、Python モジュールの依存性解析と変更を監視するためのフレームワークです。\ `MIT ライセンス`_\ のもとで配布しています。

**このプロジェクトの目標：**

* `ZenTest の autotest <http://www.zenspider.com/ZSS/Products/ZenTest/>`_ のような、ユニットテストの実行を自動化するためのツール **pyautotest** を `Python <http://www.python.org/>`_ プログラム向けに提供する
* モジュールが変更されたときに実行するアクションを柔軟にカスタマイズするために、プラグインの仕組みを提供する
* バイトコード解析、モジュールの依存性解析と変更を監視するための API を提供する

**ユーザー向けのリソース**

* *最新のリリースをダウンロード*\ ：\ `バージョン 1.0 のリリース候補 <http://metareal.lighthouseapp.com/projects/17658-modipyd/milestones/current>`_\ を近いうちに公開予定です
* `バグ報告や要望はこちら <http://metareal.lighthouseapp.com/projects/17658-modipyd/tickets/new>`_\ ：バグ報告や要望はリンク先のフォームから登録してください。\ Lighthouse_ という海外のサービスを利用しているため、インターフェースは英語になっていますが、報告する内容は日本語でもかまいません（そのうち、より詳しい手順の解説を書く予定です）。

**For developers interested in this project:**

* `Getting the code <http://github.com/ishikawa/modipyd/>`_: See the full code via a Web interface. Modipyd code is stored in `the Git repository <http://github.com/ishikawa/modipyd/>`_, where you can find the latest development source code (thanks to GitHub_).
* `Browse Tickets and Milestones <http://metareal.lighthouseapp.com/projects/17658/>`_: Report bugs and make feature requests (thanks to Lighthouse_).


AUTOTEST Related Links
-----------------------------------
* `ZenTest: Automated test scaffolding for Ruby <http://www.zenspider.com/ZSS/Products/ZenTest/>`_ The original autotest tool for Ruby
* `pyautotest <http://github.com/dbr/pyautotest/>`_ Unittest notifier: Notification of unittest passes and failures, via Growl. Like autotest for Python
* `Is there something like 'autotest' for Python unittests? - Stack Overflow <http://stackoverflow.com/questions/108892/is-there-something-like-autotest-for-python-unittests>`_


.. toctree::
   :maxdepth: 2

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _MIT ライセンス: http://www.opensource.org/licenses/mit-license.php
.. _GitHub: http://github.com/
.. _Lighthouse: http://lighthouseapp.com/
