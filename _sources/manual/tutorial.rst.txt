
ssmixtwinsを使ったデータベースの生成マニュアル
========================================

このドキュメントでは、ssmixtwinsを使用してSS-MIX2ストレージを生成する方法について説明します。

1. 元となるデータの準備
--------------------

   このPythonパッケージは、データベースの元となる最小限の患者データを必要とします。  
   ssmixtwinsはこれをもとに、患者名や住所、オーダー番号、アレルギー情報、保険情報などさまざまなダミーデータを追加し、本物らしいSS-MIX2ストレージを構築します。  
   必要なCSVファイルの詳細については :doc:`CSVデータ詳細 <source_data>` をご覧ください。

2. ssmixtwinsをインストール
-------------------------

   .. note::
      - このパッケージは、Python 3.10以上の環境で動作します。必要に応じてまずPython3をインストールまたはアップデートしてください。

   ステップ:

      1. ssmixtwinsのリポジトリをクローンします。

         .. code-block:: bash

            cd /path/to/your/working_dir
            git clone https://github.com/yuakagi/ssmixtwins.git

         ここで、/path/to/your/working_dirは、作業ディレクトリのパスに置き換えてください。

      2. リポジトリのルートディレクトリに移動し、Pythonの仮想環境を構築します。

         .. code-block:: bash

               cd /path/to/your/working_dir/ssmixtwins
               python3 -m venv .venv
               source .venv/bin/activate
      
      3. ssmixtwinsをインストールします。

         .. code-block:: bash

            pip install .

         必要な依存関係もインストールされます。

3. SS-MIX2ストレージを生成
------------------------

   :meth:`ssmixtwins.create_ssmix` を使用して、SS-MIX2ストレージを生成します。

   .. code-block:: python

      from ssmixtwins import create_ssmix

      create_ssmix(
         # 元となるCSVファイルが格納されているディレクトリ
         source_dir="/path/to/your/source_data",
         # 出力先ディレクトリ
         output_dir="/path/to/your/output_data",
         # ワーカーの数。大量のデータを処理する場合は、マシンのCPUコア数に応じて調整してください。ワーカーの数が少ないと、非常に時間がかかる場合があります。
         max_workers=10,
         # CSVファイルのバリデーションをスキップしたい場合、Trueに設定します。
         already_validated=False,
      )

   この関数はまず、全てのCSVファイルを一度検証します。全て問題がなければ、SS-MIX2ストレージの生成プロトコルを開始します。  
   もしCSVに問題があった場合（欠損値、フォーマットエラーなど）、途中で終了し、エラーの詳細を含んだJSONファイルをoutput_dirに出力します。  
   検証が成功しない場合、このファイルを参考にして、CSVファイルの修正や除外を行ってください。
   なお、一度検証が済んでおり、CSVファイルの検証をする必要がない場合、 `already_validated=True` を設定することで、検証をスキップできます。

   必要データの生成が完了したらPython仮想環境は不要です。必要に応じて.venvディレクトリを削除してください。

4. 生成されたSS-MIX2ストレージの確認
--------------------------------

   生成されたSS-MIX2ストレージは、 `output_dir` に格納されます。  
   生成されたファイルは、以下のような構造になっています:

   .. code-block:: text

      output_dir/
         ├── ssmixtwins/
         │   ├── ...
         │   ├── ...

   `output_dir/ssmixtwins` がSS-MIX2ストレージのルートディレクトリです。

