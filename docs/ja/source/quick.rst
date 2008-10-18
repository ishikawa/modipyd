.. _quick:

Modipyd の自動テストツールを使ってみよう
=================================================

このチュートリアルを実際に試すには、なにはともあれ *Modipyd* をインストールしなくてはいけません。インストールの手順については\ :ref:`install`\ が参考になるはずです。

簡単な例：\ :class:`Widget` クラス
----------------------------------------------------
これから、ふたつの簡単な Python スクリプトを例に、Modipyd の自動テストツールの使い方を説明していきます。::

  [~/modipyd/examples/widget]
  % ls
  test_widget.py	widget.py

``widget.py`` は :class:`Widget` クラスを含む Python スクリプトです。一方、\ ``test_widget.py`` はテストケースになります。

``widget.py``:

.. literalinclude:: ../../../examples/widget/000/widget.py

``test_widget.py``:

.. literalinclude:: ../../../examples/widget/000/test_widget.py

pyautotest の実行
----------------------------------------------------

:command:`pyautotest` を実行すると、これらの Python ファイルの更新を監視するようになります（\ :option:`-v/--verbose` オプションを指定すると、プログラムの処理経過が分かるようになるので便利です）::

  % pyautotest -v
  [INFO] Loading plugin: <class 'modipyd.application.plugins.Autotest'> 
  [INFO] Loading BytecodeProcesser 'modipyd.bytecode.ImportProcessor' 
  [INFO] Loading BytecodeProcesser 'modipyd.bytecode.ClassDefinitionProcessor' 
  [INFO] Monitoring:
  test_widget: test_widget.py
    Dependencies: ['widget']
    Reverse: []
  widget: widget.py
    Dependencies: []
    Reverse: ['test_widget'] 

最後の出力が示しているように、\ :command:`pyautotest` は :file:`widget.py` と :file:`test_widget.py` の監視を開始しています。

リファクタリング：初期化での代入をひとつにする
-----------------------------------------------------------------------

ここで :file:`widget.py` を見てみましょう。\ :func:`Widget.__init__` では 3 つある引数をそれぞれ、インスタンス変数に代入していますね。Python ではタプルを使うことで、複数の代入文をひとつにまとめることができます。それでは、\ :file:`widget.py` をそのように編集します。

:file:`widget.py`:

.. literalinclude:: ../../../examples/widget/001/widget.py

:file:`widget.py` を編集すると、\ :command:`pyautotest` は自動的に、変更されたファイル（個の場合 :file:`widget.py`\ ）を読み込み、関連するテストケースをすべて実行します（この場合 :file:`test_widget.py`\ ）。

.. note::

  関連するテストケースを特定するとき、\ :command:`pyautotest` はファイル名のパターンを使用しません。
  そのため、テストケースのファイル名は :file:`widget_test.py`\ 、\ :file:`WidgetTest.py`\ 、
  :file:`test/widget.py` など、自由につけることができます。

::

  [INFO] Reload module descriptor 'widget' at widget.py 
  [INFO] Modified: widget: widget.py
    Dependencies: []
    Reverse: ['test_widget'] 
  [INFO] -> Affected: widget 
  [INFO] -> Affected: test_widget 
  [INFO] Running UnitTests: test_widget 
  .
  ----------------------------------------------------------------------
  Ran 1 test in 0.000s

  OK

:func:`resize` メソッドの追加
----------------------------------------------------

:class:`Widget` クラスには足りない機能がたくさんあります。この節では :func:`resize` メソッドを追加しましょう。:func:`resize` メソッドはふたつの引数 ``width`` と ``height`` をとり、自身の大きさを変更します。テスト駆動開発の精神にのっとり、\ :func:`Widget.resize` を実装するまえにテストケースを書いていきます。

:file:`test_widget.py`:

.. literalinclude:: ../../../examples/widget/002/test_widget.py

新しいテストケースとして :class:`WidgetResizeTestCase` を追加しました。まだ :func:`Widget.resize` がないので、このテストは失敗するはずです。

.. note::

  :command:`pyautotest` は新しく追加された :class:`unittest.TestCase` のサブクラスを
  自動的に検出します。

::

  ======================================================================
  ERROR: test_resize (test_widget.WidgetResizeTestCase)
  ----------------------------------------------------------------------
  Traceback (most recent call last):
    File "test_widget.py", line 21, in test_resize
      widget.resize(45, 50)
  AttributeError: 'Widget' object has no attribute 'resize'

  ----------------------------------------------------------------------
  Ran 3 tests in 0.001s

予想通り、テストは失敗しました。それでは、\ :func:`Widget.resize` を実装しましょう。

:file:`widget.py`:

.. literalinclude:: ../../../examples/widget/002/widget.py

この変更を保存すると、\ :command:`pyautotest` が自動でテストケースを実行し、そのテストは成功します。

::

  [INFO] Running UnitTests: test_widget 
  ...
  ----------------------------------------------------------------------
  Ran 3 tests in 0.000s

  OK

