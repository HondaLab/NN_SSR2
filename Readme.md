# 概要
スキッドステアリングロボット(SSR3.1/[SSR2](https://github.com/HondaLab/SSR2))の自律行動の
ための知能を，ニューラルネットワーク(NN)を用いて構成する．
NNの入力として，[PiCamera](https://github.com/HondaLab/camera-on-raspi/tree/main)の
画像を用いる．
NNは左右２つのモーター制御値を出力する．
フレームワークとして[Chainer](https://tutorials.chainer.org/ja/)を用いる．

このrepositoryは大きく2つの部分から構成される．
* 学習プロセス(Learning)
* 自律行動(Autonomous_Movement)

以下にそれぞれを簡単に説明する．

## 1.学習プロセス(Learning)
まず教師データの取得する必要がある．
その後，学習用の計算サーバを使ってNNの重みを学習する．
### a.ロボットのラジコン操縦による，教師データの取得
教師データを取得するためには２つのプログラムを実行する必要がある．

* NN_ssr2_chainer/collection_data2.py （ロボット(ラズパイ)で実行）
* NN_ssr2_chainer/recv_data.py （データを受け取る計算サーバ側で実行）

上記２プログラムを両方同時に実行する．
collection_data2.pyはrecv_data.pyに１次元画像データなどをソケット通信
で送る．
そのためには，ロボットと計算サーバーの双方で，modules/li_socket.py 内で
data_reciving_terminal の値を計算サーバのIPアドレスにする．
sensor_portのデフォルト値は50005になっているが，この値を50006などに変更する
ことで，複数のロボットからのデータを同時に１つの計算サーバーで受け取ることもできる．

recv_data.py はデータファイル番号と，取得データ数を聞いてくるので，
答える．
データファイル番号は，あとでintegration_data.pyで複数のデータファイルを結合
するときに参照される番号である．

１度のrunで取得するデータ数は500 〜 1000 程度が適当である．
あまり多くのデータを１度の実行で取得しようとすると，操作の疲労から
ロボットの衝突などが頻発し，教師データとしての質が低下する恐れがある．


ラジコンで人間が手動でロボットを操縦することで，NNの教師データが作成される．
NNの入力はPiCameraからの画像，出力がモーター制御値である．
手動操縦したモーター制御値を正解値とする回帰問題として自律走行を行う．

#### 手動操縦方法
キーボードを用いてロボットを操縦する．
ホームポジションに手をおいて，人差し指と中指だけで基本な操縦が
可能です．
* q : 終了
* w : 増速
* s : 減速
* j : 左折
* k : 右左折終了
* l : 右折
* d : 停止

各キーを押したときだけ，１次元画像データとモーター制御値が
socket通信を通じて計算サーバ側に送られる．


#### socket通信で作成された教師データ（csvファイル)
socket通信で受信したデータは
画像データとモーター出力それぞれ下記ファイルに保存される．

* part_data_inX.csv
* part_motor_outX.csv

Xがrecv_data.pyを実行したときに入力したデータファイル番号となる．

#### 複数の教師データの統合
integration_data.py を実行して，教師デーダを統合する．
データファイル番号を聞かれるので，その答えたデータファイル番号のデータが
統合される．

下記のchainer用の教師データが生成される．

* chainer_data_in.csv：RGB１次元画像データ(縦方向和)
* chainer_motor_out.csv：モーター制御値

### b.学習：重みとバイアスの更新(Learning)
NN_learning_h1.py あるいは NN_learning_h2.py を実行して，
中間層１層と２層のニューラルネットワークを学習させる，

[NN_batch_training]のcodeはミニバッチ学習．


## 2.NNによるロボットの自律行動(Autonomous_Movement)
学習結果の「Input_data_max.csv」「Output_data_max.csv」「optimum_weight_???」
などのfileをロボット(Raspi)に移して「nn_ssr2_hX.py」により，
ロボットが自律行動を開始する．

send.shを利用すると，自動的にロボットに学習結果が送信される．


## teacher data example:

https://muroranit-my.sharepoint.com/:u:/g/personal/20043068_mmm_muroran-it_ac_jp/EW3JrT4Qc2FLv4XZDQQAzXkBjjGTF9sr99w809OttwJUJw?e=LjS0YQ


## NN教師データの収集手順（○：走行ロボットの端末の操作　●：データを受信するコンピュータの端末の操作）<br>
○１．フォルダー「NN_SSR2」の中の「NN_ssr2_chainer」に移動する．ロボット側，データ受信側ともにここに使用するソースコードがある．<br>
２．ロボット側とデータ受信側，両方のフォルダー「modules」の中の「li_sokcket.py」のソースコード内のdata_reciving_terminal（3行目）の値を受信するパソコンのIPアドレスに書き換える．<br>
○３．１のフォルダーで「collention_data.py」を実行する．別のウィンドウでロボットの視点映像が表示される．端末にクリックして，入力できるようにする．画面は暗くなっているが，これはロボットが走行し始めると表示される．以上でロボットの準備完了．<br>
●４．「recv_data.py」を実行する，端末上に表示される質問に答える．以上でデータ受信側のコンピュータも準備完了．<br>
○５．ロボットをラジコン操作する．※操作方法は下記に示す．ロボットの端末に入力行うと，キーボードのボタンを押す瞬間の一次元画像データとモーターの出力をソケット通信でデータ受信側に送信する．データ受信側の端末に受けたデータの数を表示し，設定した数に至ると自動的に停止する．収集したデータは「part_data_in.csv」「part_data_in_include_distance_data.csv」「part_motor_out.csv」として保存される，ファイル名の後ろに番号(手順４で入力した数字)がついてる．<br>
### ロボットの操作方法（a:前進　power +20，z:後退　back power -20，j:左曲がり，l:右曲がり，k:曲がる値を０にする）<br>

## ２回目以降のデータ収集の際の注意点<br>
「rec_data.py」をもう一度実行するとデータは収集される．ファイル名は手順で入力した数字の次のものになる，<br>※データを結合する際，数字が連続されたものでないと結合できないので注意<br>

## 収集したデータの結合方法<br>
１．データ受信側の端末で「intergation_data.py」を実行する．結合したいファイルのstart number と stop number を入力する，結合されたデータは「chainer_data_in.csv」「chainer_data_in_include_distance_data.csv」「chainer_motor_out.csv」に保存される．これは学習用のデータである．このデータは上書きされていくので各自別のフォルダーに移動する．<br>
※NNによる学習するときに学習用のデータが「NN_learning_h1.py」と同じ場所にないと学習できないので注意
２．ロボット側のcollention_data.pyをstopしたら，ロボット視点の動画もフォルダー「temp」にmp4ファイルとして保存される，こちらも上書きされるので学習用のデータと一緒に保存する．<br>

## NNによる学習<br>
１．データを受信したコンピュータで「NN_learning_h1.py」を実行すると，学習データを読み込んで，学習する，学習結果は同じフォルダーに保存される．<br>
２．「send.sh」の４行目のpi@172.16.7.○○○を使用するロボットの番号に書き換える．その後，「send.sh」を実行し学習結果を送信する．<br>
３．学習結果の送信が終わり，ロボット側で「nn_ssr2_h1.py」を実行すると手順２で送信された結果を読み込んで自立走行する．<br>
