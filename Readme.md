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


