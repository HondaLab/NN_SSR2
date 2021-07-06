# 概要
ニューラルネットワーク(NN)を用いて，
スキッドステアリングロボット([SSR2](https://github.com/HondaLab/SSR2))の自律走行実現する．



## ロボットのラジコン操縦による，教師データの作成
* Raspi@SSR2:teacher_data_robot_part/NN_teacher_data_collection_by_socket.py
* DebianPC: teacher_data_copmuter_part/socket_recv.py

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
* ”a”をおすと，ロボットのmotorのoutputが大きくなる
* ”ｚ”をおすと，ロボットのmotorのoutputが小さくなる
* ”j”をおすと，ロボットの左のモーターの出力がplus 14の同時に,右のモーターの出力がマイナス14
* "l"をおすと，ロボットの右のモーターの出力がplus 14の同時に,左のモーターの出力がマイナス14
* "k"をおすと，ボタン”ｊ”と”l”により変化した値がもとに戻す．

buttunを押す瞬間，１次元画像データとモーターの出力を送る


## socket通信で作成された教師データ（csvファイル)
socket通信でもらったデータがfolder「teacher_data_copmuter_part」の「teacher_data_folder」に保存されている．
dataはRGB画像データの列の和とモーターの出力，「chainer_data_in.csv」「chainer_motor_out.csv」に保存されている．


## ニューラルネットワーク(NN)の学習
２のdataをそのままfolder「training_code」に移動して，「chainer_neural_network_hidden_1」
「chainer_neural_network_hidden_2」を実行して，中間層１層と２層のニューラルネットワークを学習させる，
結果が自動的にfolderを作って保存する．[NN_batch_training]のcodeはミニバッチ学習です．


## NNによるロボットの自律走行
３でもらった学習結果の「data_in_max」「data_out_max」「optimum_weight_???」3つのfileを
「moveing_by_NN_robot_part」の「neural_network」の「anticlockwise」or [clockwise]の
「weight_hidden1_anticlockwise」or「weight_hidden2_anticlockwise」or[weight_hidden1_clockwise]or
[weight_hidden2_clockwise] に移動して
「neural_network_hidden1_anticlockwise」と「neural_network_hidden2_clockwise」で学習結果により，
ロボットが動く．こちらの部分はロボットの中に実行する．「keyin」「motor5a」は必要なpackage.

## 複数の教師データを融合する
folder「data_making」の「train_data_make_version2」を実行して，folder「１」と「２」等等にある教師デーダを
融合する．

## teacher data example:

https://muroranit-my.sharepoint.com/:u:/g/personal/20043068_mmm_muroran-it_ac_jp/EW3JrT4Qc2FLv4XZDQQAzXkBjjGTF9sr99w809OttwJUJw?e=LjS0YQ
