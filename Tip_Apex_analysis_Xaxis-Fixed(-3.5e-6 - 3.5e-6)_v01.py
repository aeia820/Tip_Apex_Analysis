''' Tip_analysis_v05 '''
# -*- Python 3.7.6 -*-
# -*- coding: utf-8 -*-

''' ライブラリのインポート '''
import os, tkinter, tkinter.filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as ptick
import numpy as np
import math
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import sys

def start():
    ''' GUIの設定 '''
    # GUIの作成
    root = tkinter.Tk()
    # GUIのタイトルを設定
    root.title('確認画面')
    # GUIの描画領域を設定
    root.geometry('240x100')
    # テキスト表示
    input_label = tkinter.Label(root, text='CSVファイルを選択してください')
    input_label.place(x=50, y=14)
    # ボタン押下時の動作を定義
    def ok():
        root.destroy()
    # ボタンを作成
    button_ok = tkinter.Button(root, text='OK',command=ok, font=('', '10', 'bold'), width=8, height=2, bg='gainsboro')
    button_ok.place(x=80, y=42)

    # GUIを表示
    root.mainloop()

    return


def main():
    ''' ファイルダイアログの表示 → ファイル選択 '''
    root = tkinter.Tk()
    root.withdraw()
    fTyp = [('','.csv')]    # *.csvファイルのみ表示
    iDir = os.path.abspath(os.path.dirname(__file__))   # パスの取得
    file = tkinter.filedialog.askopenfilename(filetypes = fTyp,initialdir = iDir)   # パスを含むファイル名の取得

    ''' csvファイルの読み込み(ヘッダーなし) '''
    input_csv = pd.read_csv(file, header=None)
    # 1列目と2列目の値を取得
    x = input_csv[input_csv.keys()[0]]
    y = input_csv[input_csv.keys()[1]]

    ''' 2次の最小二乗法でフィッティング '''
    res1 = np.polyfit(x, y, 2)
    y_fit = np.poly1d(res1)(x)
    # フィッティングカーブの係数と切片を取得
    a,b,c = np.polyfit(x, y, 2)
    
    # x^2の係数から曲率半径を算出
    r = 1 / abs(2*a)

    ''' フィッティングカーブの接線を求める '''
    y_grad = np.gradient(y_fit, x)
    f = lambda i: y_grad[i] * x + (y_fit[i] - y_grad[i] * x[i])

    # xが最小のときの接線を算出
    res2 = np.polyfit(x, f(0), 1)
    tan_line1 = np.poly1d(res2)(x)
    # 接線の傾きからラジアン → 角度 → y軸からの角度を算出
    d1,e1 = np.polyfit(x, f(0), 1)
    rad1 = math.atan(d1)
    deg1 = (rad1*180) / math.pi
    theta1 = (90 - abs(deg1))

    # xが最大のときの接線を算出
    res3 = np.polyfit(x, f(len(x)-1), 1)
    tan_line2 = np.poly1d(res3)(x)
    # 接線の傾きからラジアン → 角度 → y軸からの角度を算出
    d2,e2 = np.polyfit(x, f(len(x)-1), 1)
    rad2 = math.atan(d2)
    deg2 = (rad2*180) / math.pi
    theta2 = (90 - abs(deg2))

    # 2つの接線の角度から先端角度を算出
    theta = theta1 + theta2

    ''' 中心軸を設定 '''
    y_line = [-1,1]
    x_line = [0,0]

    ''' 現在時刻を取得 '''
    dt = datetime.datetime.now()
    dtstr = dt.strftime('%Y-%m-%d %H:%M:%S.%f')     # データタイプをstring型に変換(txtファイルに挿入するため)

    ''' テキストファイルにデータを保存 '''
    # 読み込んだcsvファイルの名前を抽出
    name = file.strip('.csv')
    # csvファイルと同名でtxtファイルを作成して開く
    f = open(name + '.txt', 'w')
    # 任意のデータを書き込み(int型はすべてstring型に変換)
    f.write(dtstr + '\n\n')
    f.write('#### Tip-analysis ####\n')
    f.write('Fitting : least squares method\n' + 'y_1 = ax^2 + bx + c\n')
    f.write('a = ' + str(a) + ', b = ' + str(b) + ', c = ' + str(c) + '\n\n')
    f.write('Tangent\n' + 'y_2 = dx + e\n')
    f.write('Minimum\n' + 'd_1 = ' + str(d1) + ', e_1 = ' + str(e1) + '\n')
    f.write('Maximum\n' + 'd_2 = ' + str(d2) + ', e_2 = ' + str(e2) + '\n\n')
    f.write('Curvature radius\n' + 'r = ' + str(r) + '\n')
    f.write('Cone angle\n' + 'θ = ' + str(theta) + '\n\n')
    f.write('r = ' + str(round(r*(10**9),2)) + ' [nm]\n' + 'θ = ' + str(round(theta,2)) + ' [°]')
    # txtファイルを閉じる
    f.close()

    ''' グラフ設定 '''
    fig, ax=plt.subplots(figsize=(5, 8))    # グラフ枠と軸を同時に生成，グラフサイズ設定
    plt.xlabel('X [m]')     # 軸ラベル
    plt.ylabel('Y [m]')
    plt.ylim(-8e-6,5e-6)    # 描画範囲
    plt.xlim(-3.5e-6,3.5e-6)
    ax.xaxis.set_major_formatter(ptick.ScalarFormatter(useMathText=True))   # 軸目盛を指数表記(x10^*)に変更
    ax.yaxis.set_major_formatter(ptick.ScalarFormatter(useMathText=True)) 

    ''' グラフ描画 '''
    plt.plot(x_line , y_line, linestyle='dashdot', color='lightgray')   # 中心軸
    plt.plot(x, y, linestyle='None', marker='o', color='dodgerblue', label='Shape plot')    # 形状プロット
    plt.plot(x, y_fit, linestyle='solid', color='red', label='Fitting curve')   # フィッティングカーブ
    plt.plot(x, tan_line1, linestyle='solid', color='green', label='Tangent')   # 接線
    plt.plot(x, tan_line2, linestyle='solid', color='green')
    plt.legend(loc='lower right')   # 凡例表示

    ''' グラフを保存 '''
    # csvファイルと同名でpngファイルを保存
    fig.savefig(name + '.png')

    ''' GUIの設定 '''
    # GUIの作成
    root = tkinter.Tk()
    # GUIのタイトルを設定
    root.title('実行画面')
    # GUIの描画領域を設定
    root.geometry('500x900')
    # GUIにグラフを挿入
    canvas = FigureCanvasTkAgg(fig, root)
    canvas.get_tk_widget().place(x=0, y=0)
    # 実行結果のテキスト表示
    input_label = tkinter.Label(root, text='曲率半径 = ' + str(round(r*(10**9),2)) + ' [nm]\n' + '先端角度 = ' + str(round(theta,2)) + ' [°]', anchor='e', justify='left')
    input_label.place(x=0, y=800)
    # ファイル保存場所のテキスト表示
    input_label = tkinter.Label(root, text='ファイルが保存されました\n', font=('', '12', 'bold'), anchor='w')
    input_label.place(x=0, y=840)
    input_label = tkinter.Label(root, text=name + '.png\n' + name + '.txt', anchor='e', justify='left')
    input_label.place(x=0, y=860)
    # ボタン押下時の動作を定義
    def restart():
        root.destroy()
        main()
    def exit():
        sys.exit('プログラム終了')
    # ボタンを作成
    button_restart = tkinter.Button(root, text='Restart',command=restart, font=('', '10', 'bold'), width=8, height=2, bg='gainsboro')
    button_restart.place(x=340, y=850)
    button_exit = tkinter.Button(root, text='Exit',command=exit, font=('', '10', 'bold'), width=8, height=2, bg='gainsboro')
    button_exit.place(x=420, y=850)

    # GUIを表示
    root.mainloop()

    return

""" pythonを上手に動かすおまじない（外部からの*.py呼び出しに対応）"""
if __name__ == '__main__':
    # 実行
    start()
    main()