# 概要
スキッドステアリングロボット([SSR2](https://github.com/HondaLab/SSR2))の自律行動の
ための知能を，ニューラルネットワーク(NN)を用いて構成する．
NNの入力として，[PiCamera](https://github.com/HondaLab/camera-on-raspi/tree/main)の
画像を用いる．NNは左右２つのモーター制御値を出力する．
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

* collection.py （ロボット(ラズパイ)で実行）
* recieve.py （データを受け取る計算サーバ側で実行）

上記２プログラムを両方同時に実行する．
その後，ラジコンで人間が手動でロボットを操縦することで，NNの教師データが作成される．
NNの入力はPiCameraからの画像，出力がモーター制御値である．
手動操縦したモーター制御値を正解値とする回帰問題として自律走行を行う．

#### 手動操縦方法
キーボードを用いてロボットを操縦する．
* ”a”をおすと，モーター制御値が大きくなる
* ”ｚ”をおすと，モーター制御値が小さくなる
* ”j”をおすと，左のモーター制御値がplus 14の同時に,右のモーター制御値がマイナス14
* "l"をおすと，右のモーター制御値がplus 14の同時に,左のモーターの出力がマイナス14
* "k"をおすと，ボタン”ｊ”と”l”により変化した値がもとに戻す．

各キーを押す瞬間，１次元画像データとモーター制御値が
socket通信を通じて計算サーバ側に送られる．


#### socket通信で作成された教師データ（csvファイル)
socket通信で受信したデータは
NNの入力と出力それぞれ下記ファイルに保存される．

* chainer_data_in.csv：RGB１次元画像データ(縦方向和)
* chainer_motor_out.csv：モーター制御値

#### 複数の教師データを融合する
データ収集が１回だけの場合には必要ない．

データの収集を複数回に分けて行った場合は，それらを統合できる．
folder「Data_Integration」の「train_data_make_version2」を実行して，
folder「１」と「２」等等にある?教師デーダを統合する．


### b.学習：重みとバイアスの更新(Learning)
learn_h1.py あるいは learn_h2.py を実行して，
中間層１層と２層のニューラルネットワークを学習させる，

[NN_batch_training]のcodeはミニバッチ学習．


## 2.NNによるロボットの自律行動(Autonomous_Movement)
学習結果の「data_in_max.csv」「data_out_max.csv」「optimum_weight_???」3つのfileを
ロボット(Raspi)に移して「nn_ssr2_hX.py」により，ロボットが自律行動を開始する．


## teacher data example:

https://muroranit-my.sharepoint.com/:u:/g/personal/20043068_mmm_muroran-it_ac_jp/EW3JrT4Qc2FLv4XZDQQAzXkBjjGTF9sr99w809OttwJUJw?e=LjS0YQ
