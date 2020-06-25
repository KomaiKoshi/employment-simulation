#ファイルのインポート
import constant
import general
import q_learning
import employee as ee
import employer as er

#エージェント人数
employee_num = 60
employer_num = 3

#試行回数
trial = 200

scale = 100.0/(6500*10**4)
base_gdp = 67 * 20

#logging
log = np.zeros([40,100]).tolist()
nth = 0

#gdp.csvファイルからデータを読み取る
def read_GDP(file = './gdp.csv'):
    data = []
    with open(file, 'r') as f:
        reader = csv.reader(f)
        #header = next(reader)  # ヘッダーを読み飛ばしたい時
        for row in reader:
            data.append(float(row[0]))
    #GDPグラフの表示
    plotgraph_GDP(data)
    #データを返す
    return data

#グローバル変数
def trial_routine(arg):
    global employee_num
    global employer_num
    global trial
    global scale
    global base_gdp
    global nth

    #雇用者・労働者エージェントを作るためのインスタンスを作成
    ee_f = ee.EmployeeFactory()
    er_f = er.LMMiniEmployerFactory()

    #雇用者エージェントを作成
    employers = [er_f.create() for _ in range(employer_num)]
    employees = []

    #労働者エージェントを追加や削除をするために管理するリスト
    next_employees = []
    retire_employees = []

    #gdpを読み取るための関数のインスタンスを生成
    gdp = read_GDP()

    #出力するgdp,雇用者・労働者エージェント数,採用人数,解雇人数,各雇用者エージェントに対する労働者エージェント
    return_val = [[], [], [], [], [], [], []]
    return_val_other = []

    #現在のgdpデータを管理する変数
    current_gdp = 0

    
    #試行回数分を学習させる
    for trial_index in range(trial):

        #現在の試行回数の表示
        print(trial_index)

        #労働者・雇用者エージェントのデータを消す(初期化)
        employees.clear()
        for e in employers:
            e.clear()

        #労働者エージェント生成し、年齢を設定する
        employees = [ee_f.create(np.random.uniform(15,65)) for _ in range(employee_num)]

        #GDPの年数分繰り返す
        for gdp_index in range(len(gdp)):

            #エージェントを管理する変数たちの初期化
            next_employees.clear()
            retire_employees.clear()
            fire_wk = 0
            emp_wk = 0

            #労働者エージェントが定年退職か判断する
            for e in employees:
                if constant.WORKER_AGE.LOWER <= e.age <= constant.WORKER_AGE.UPPER:
                    next_employees.append(e)
                else:
                    retire_employees.append(e)

            #労働者エージェントを定年退職させる
            for ree in retire_employees:
                ree.retire()

            #いなくなったエージェント分新労働者エージェントを雇う
            while len(next_employees) <= employee_num:
                next_employees.append(ee_f.create(23))
            employees = copy.copy(next_employees)

            """
            #5年勤めると正規労働者エージェントになる
            for e in employees:
                if e.length_of_service >= 5 and e.work_type == constant.WORKER_TYPE.TEMPORARY:
                    e.change(constant.WORKER_TYPE.REGULAR)
            """

            #雇用転換するかしないか
            for er_t in employers:
                for ee_t in er_t.employees:
                    if e.length_of_service >= 5 and e.work_type == constant.WORKER_TYPE.TEMPORARY:
                        result = None
                        result = er_t.change_employment(ee_t)
                        if result == True:
                            er_t.regular_employ(ee_t)
                        elif result == False:
                            er_t.temporary_employ(ee_t)

            #今年のGDPを分割して、仕事量として割り振る
            if gdp_index >= 1:
                task = base_gdp * (gdp[gdp_index-1] / gdp[gdp_index])
                base_gdp = current_gdp
                current_gdp = task
            else:
                task = base_gdp
                base_gdp = base_gdp
                current_gdp = base_gdp

            #労働者エージェントに仕事を与える
            for e in employers:
                e.set_work(task / len(employers))

            #入社試験
            for e in employees:
                if e.work_type == constant.WORKER_TYPE.JOBLESS:
                    #1年に1社
                    #雇用者エージェントを選択する
                    selected_ers = e.select_employers(employers)

                    for selected_er in selected_ers:
                        #合格か不合格か
                        result = None
                        result = selected_er.exam(e)

                        #試験は一社なので、合格=入社
                        if result == True:
                            selected_er.employ(e,gdp_index)
                            emp_wk += 1

                        elif result == False:
                            selected_er.reject(e)

            #給与を労働者エージェントに与える
            for e in employees:
                if e.work_type != constant.WORKER_TYPE.JOBLESS:
                    e.salary(e.work())

            #契約更新をする
            for er_t in employers:
                for ee_t in er_t.employees:
                    #契約更新するかしないか
                    result = None
                    result = er_t.renew(ee_t)
                    if result == True:
                        er_t.keep(ee_t)
                    elif result == False:
                        er_t.fire(ee_t)
                        fire_wk += 1

            #年度末処理
            for e in employees:
                e.elapse()
            for e in employers:
                e.elapse()
            
            #仕事量,残った仕事量,非正規労働者,正規労働者,雇用した人数,契約更新しなかった人数
            if trial_index == trial - 1:
                g = task
                p = sum([e.remained_work() for e in employers])
                wt = sum([e.count_temporary() for e in employers])
                wr = sum([e.count_regular() for e in employers])\
                #各雇用者エージェントが契約している労働者エージェント数
                num = []
                for e in employers:
                    Number_of_workers = e.count_employee()
                    num.append(Number_of_workers)
                return_val[0].append(g)
                return_val[1].append(p)
                return_val[2].append(wt)
                return_val[3].append(wr)
                return_val[4].append(emp_wk)
                return_val[5].append(fire_wk)
                return_val[6].append(num)

    return return_val


#学習させた実行結果を平均する関数
def analysis_avg(ary):
    d_list = [ [] for _ in range(len(ary[0]))]
    for i in range(len(ary[0])):
        for e in ary:
            d_list[i].append(e[i])
    avg_ary = [sum(d) / len(d) for d in d_list]
    return avg_ary

#学習させた実行結果を平均する関数
def analysis_list(ary):
    #空のリストを作成する(GDPデータ分　現在は102個分)
    d_list = [[]*3]*len(ary[0])
    list1 = []*10
    list2 = []
    list3 = []
    #データを10個に分ける
    for i in range(10):
        list1.append(ary[i])
    #10回平均を計算
    for i in range(len(ary[0])):
        for j in range(3):
            for k in range(10):
                list2.append(list1[k][i][j])
            z = sum(list2)
            list3.append(z/10)
            list2.clear()
    #平均した結果をリストに格納
    d_list = convert_1d_to_2d(list3, 3)
    return d_list

#リストを変換する(例：一次元から二次元)
def convert_1d_to_2d(l, cols):
    return [l[i:i + cols] for i in range(0, len(l), cols)]

#メイン関数
def main():

    #実行開始時間計測
    t1 = time.time()
    result  = []
    pool = mp.Pool(processes=12)
    result = pool.map(trial_routine, range(10))
    num_list = []
    g_list = analysis_avg([r[0] for r in result] )
    w_list = analysis_avg([r[1] for r in result] )
    p_list = analysis_avg([r[2] for r in result])
    wr_list = analysis_avg([r[3] for r in result])
    ew_list = analysis_avg([r[4] for r in result])
    fw_list = analysis_avg([r[5] for r in result])
    num_list = analysis_list([r[6] for r in result])

    #csvファイルにパラメータを書き込む
    with open("data1.csv", "w") as f:
            f.write("GDP, WORKING, T_WORKER, R_WOKER, EMP, FIR" + "\n")
            for i in range(len(g_list)):
                f.write(str(g_list[i]) + "," + str(w_list[i]) + "," + str(p_list[i]) + "," + str(wr_list[i]) + "," + str(ew_list[i]) + "," + str(fw_list[i]) + "\n")

    #csvファイルにパラメータを書き込む
    with open("data2.csv", "w") as f:
            f.write("employer1, employer2, employer3" + "\n")
            for i in range(len(num_list)):
                f.write(str(num_list[i]) + "\n")

    plotgraph(p_list, wr_list, ew_list, fw_list, num_list)

    #実行終了時間計測
    t2 = time.time()

    #処理時間表示
    elapsed_time = t2-t1
    print(f"経過時間：{elapsed_time/60}")



#雇用形態グラフの表示
def plotgraph_workers(p_list,wr_list,ew_list,fw_list):
    sns.set()
    #非正規労働者
    plt.plot(p_list, color = "red")
    #正規労働者
    plt.plot(wr_list, color = "blue")
    #雇用人数
    plt.plot(ew_list, color = "green")
    #契約破棄人数
    plt.plot(fw_list, color = "yellow")
    plt.grid(True)
    #plt.show()
    plt.savefig("雇用形態に対する各労働者数.png")
 
#各雇用者エージェントが契約する労働者エージェント人数
def plotgraph_each_workers(num_list):
    sns.set()
    list1 = []
    list2 = []
    list3 = []

    for i in range(len(num_list)):
        list1.append(num_list[i][0])
    for i in range(len(num_list)):
        list2.append(num_list[i][1])
    for i in range(len(num_list)):
        list3.append(num_list[i][2])

    plt.plot(list1, color = "blue")
    plt.plot(list2, color = "red")
    plt.plot(list3, color = "green")
    plt.grid(True)
    #plt.show()
    plt.savefig("各雇用者と契約する労働者数.png")

#GDPのグラフ表示
def plotgraph_GDP(g_list):

    #seabornセット
    sns.set()
    #GDP
    plt.plot(g_list, color = "blue")
    #タイトル　軸ラベル
    plt.title("GDP")
    plt.xlabel("Season")
    plt.grid(True)
    #保存名
    plt.savefig("GDP.png") 

def plotgraph(p_list, wr_list, ew_list, fw_list, num_list):

    sns.set()
    list1 = []
    list2 = []
    list3 = []
    turn = []

    for i in range(len(num_list)):
        list1.append(num_list[i][0])
    for i in range(len(num_list)):
        list2.append(num_list[i][1])
    for i in range(len(num_list)):
        list3.append(num_list[i][2])
    j = 1
    for i in range(len(num_list)):
        turn.append(j)
        j+=1
    
    fig = plt.figure(1)
    plt.plot(turn,p_list,color = "red")
    plt.plot(turn,wr_list,color = "blue")
    plt.plot(turn,ew_list,color = "green")
    plt.plot(turn,fw_list,color = "yellow")
    plt.grid(True)
    plt.savefig("雇用形態に対する各労働者数.png")

    fig = plt.figure(2)
    plt.plot(turn,list1,color = "blue")
    plt.plot(turn,list2,color = "green")
    plt.plot(turn,list3,color = "red")
    plt.grid(True)
    plt.savefig("各雇用者が契約する労働者数.png")

if __name__ == "__main__":
    main()
    pass
