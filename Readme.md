スキッドステアリングロボット(SSR2)をニューラルネットワーク(NN)を用いて自律走行実験する．

teacher data :

https://muroranit-my.sharepoint.com/:u:/g/personal/20043068_mmm_muroran-it_ac_jp/EW3JrT4Qc2FLv4XZDQQAzXkBjjGTF9sr99w809OttwJUJw?e=LjS0YQ


## NNデータ収集手順（○：走行ロボットの端末の操作　●：データを受信するコンピュータの端末の操作）<br>
○１．フォルダー「NN_SSR2」の中の「NN_ssr2_chainer」に移動する．ロボット側，データ受信側ともにここに使用するソースコードがある．<br>
○２．１のフォルダーで「collention_data.py」を実行する．別のウィンドウでロボットの視点映像が表示される．端末にクリックして，入力できるようにする．<br>
○３．最初はロボットの視点映像が真っ黒であるが，端末に何回か入力すれば，映像が表示される．以上でロボット側の準備完了．<br>
●４．「rec_data.py」を実行する，データ受信側のコンピュータも準備完了．<br>
○５．ロボットをラジコン操作する．ロボットの端末に入力行うと，キーボードのボタンを押す瞬間の一次元画像データとモーターの出力をソケット通信でデータ受信側に送信する．データ受信側の端末に受けたデータの数を表示し，設定した数に至ると自動的に停止する．ここで，両方のフォルダー「modules」の中の「li_sokcket.py」のソースコード内のdata_reciving_terminal（3行目）の値を受信するパソコンのIPアドレスに書き換える．収集したデータは「part_data_in」「part_data_in_include_distance_data」「part_motor_out」として保存される，ファイル名の後ろに番号(手順４で入力した数字)がついてる．<br>
### ロボットの操作方法（a:前進　power +20，z:後退　back power -20，j:左曲がり，l:右曲がり，k:曲がる値を０にする）<br>

## ２回目以降のデータ収集の際の注意点<br>
「rec_data.py」をもう一度実行するとデータは収集される．ファイル名は手順で入力した数字の次のものになる，<br>※データを結合する際連続されたものでないと結合できないので注意<br>

## 収集したデータの結合方法<br>
１．データ受信側の端末で「intergation_data.py」を実行する．結合したいファイルのstart number と stop number を入力する，結合されたデータは「chainer_data_in.py」「chainer_data_in_include_distance_data」「chainer_motor_out」に保存される．これは学習用のデータである．このデータは上書きされていくので各自別のフォルダーに移動する．<br>
２．ロボット側のcollention_data.pyをstopしたら，ロボット視点の動画もフォルダー「temp」にmp4ファイルとして保存される，こちらも上書きされるので学習用のデータと一緒に保存する．<br>

## NNによる学習<br>
１．データを受信したコンピュータで「NN_learning_h1.py」を実行すると，学習データを読み込んで，学習する，学習結果は同じフォルダーに保存される．<br>
２．「send_103.sh」を実行して，ssr103に学習結果を送信する．<br>
３．学習結果の送信が終わり，ロボット側で「nn_ssr2_h1.py」を実行すると手順２で送信された結果を読み込んで自立走行する．<br>
