# 概要
スキッドステアリングロボット([SSR2](https://github.com/HondaLab/SSR2))の自律走行実現する．
PiCameraの画像を主な入力データとする，ニューラルネットワーク(NN)を用いる．
NNの構成フレームワークとしてChainerを用いる．

全体は大きく３つの部分から構成されている．
* データ収集(Data_Collection)
* 学習(Learning)
* 自律行動(Autonomous_Movement)


## ロボットのラジコン操縦による，教師データの収集(Data_Collection)
* Raspi@SSR2:robot/NN_teacher_data_collection_by_socket.py
* DebianPC: copmuter/socket_recv.py

上記２プログラムを両方同時に実行する．

ラジコンで人間が手動でロボットを制御することで，NNの教師データを作成する．
NNの入力はPiCameraからの画像，出力がモーター制御値である．
手動制御したモーター制御値を正解値とする回帰問題として自律走行を考える．


### モジュール
* keyin
* li_socket
* motor5a
* vl53_3a
* li_socket

が必要なモジュール.


### 手動操縦方法
キーボードを用いてロボットを操縦する．

* ”a”をおすと，モーター制御値が大きくなる
* ”ｚ”をおすと，モーター制御値が小さくなる
* ”j”をおすと，左のモーター制御値がplus 14の同時に,右のモーター制御値がマイナス14
* "l"をおすと，右のモーター制御値がplus 14の同時に,左のモーターの出力がマイナス14
* "k"をおすと，ボタン”ｊ”と”l”により変化した値がもとに戻す．

各キーを押す瞬間，１次元画像データとモーター制御値が
socket通信を通じてDebianPC側に送られる．


### socket通信で作成された教師データ（csvファイル)
socket通信で受信したデータは
copmuter/teacher_data_folderに保存さる．

NNの入力と出力それぞれ下記ファイルに保存される．

* chainer_data_in.csv：RGB１次元画像データ(縦方向和)
* chainer_motor_out.csv：モーター制御値

### 複数の教師データを融合する
folder「Data_Integration」の「train_data_make_version2」を実行して，
folder「１」と「２」等等にある?教師デーダを統合する．


## 学習：重みとバイアスの更新(Learning)
上記２の教師データをそのままfolder「Learning」に移動して，
「chainer_neural_network_hidden_1」あるいは
「chainer_neural_network_hidden_2」を実行して，
中間層１層と２層のニューラルネットワークを学習させる，
結果が自動的にfolderを作って保存する．

[NN_batch_training]のcodeはミニバッチ学習です．


## NNによるロボットの自律行動(Autonomous_Movement)
学習結果の「data_in_max.csv」「data_out_max.csv」「optimum_weight_???」3つのfileを
「anticlockwise」/ [clockwise]の「hiddenX」に移動して
「nn_ssr2_hX.py」で学習結果により，ロボットが自律行動を開始する．


## teacher data example:

https://muroranit-my.sharepoint.com/:u:/g/personal/20043068_mmm_muroran-it_ac_jp/EW3JrT4Qc2FLv4XZDQQAzXkBjjGTF9sr99w809OttwJUJw?e=LjS0YQ
