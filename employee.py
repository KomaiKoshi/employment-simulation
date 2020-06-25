from constant import *
import indexer
import random
import select_employer as se

##########労働者エージェントクラス##############################################
class Employee:
    id_counter = indexer.Indexer()

##########初期設定##########
    def __init__(self):
        self.id = Employee.id_counter.gen()
        self.age = WORKER_AGE.LOWER
        self.work_type = WORKER_TYPE.JOBLESS
        self.employer = None
        self.length_of_service = 0
        self.rewards = {}
        self.selection_strategy = None

##########年始処理##########
    def begin(self):
        self.elapse()
        pass

##########どの雇用者エージェント選択するかを決める########## 
    def select_employers(self, employers, num = 1):
        return self.selection_strategy.select(self, employers, num)

##########雇われる(全ての労働者エージェントは非正規労働者からスタートする)#########
    def employed(self,employer,gdp_index):
        if self.employer is not None and self.employer != employer:
            self.retire()
        self.employer = employer
        self.work_type = WORKER_TYPE.TEMPORARY
        self.length_of_service = 0
        self.rewards[self.employer] = 0

##########働く(労働力計算)##########
    def work(self):
        #労働力最大ピーク43歳(厚労省)
        #定年者は新卒の1.5倍の労働力
        #1人あたりのGDPは67
        # 就業年数に線形で
        # 年齢による労働効率の二次近似式(年齢によっていくら労働力が変わるか)
        # f(x) = -0.00236*x^2+0.22*x-3.12325  x:労働年齢
        #xが最低労働年齢のとき、f(x)は1
        alpha = 0.5
        beta = 0.5
        gdp_unit = 67
        #年齢効率 
        f = lambda x : -0.00236 * x ** 2 + 0.22 * x - 3.12325     
        #勤続年数効率 20 age =1, 55 age = 2
        g = lambda x : 0.029464 * x + 0.410714                     
        dp = alpha*f(self.age)+beta*g(self.length_of_service)
        return gdp_unit*dp
        #pass

##########給料をもらう##########
    def salary(self, money):
        if self.employer is not None:
            if self.work_type == WORKER_TYPE.REGULAR:
                self.rewards[self.employer] += money*2
            elif self.work_type == WORKER_TYPE.TEMPORARY:
                self.rewards[self.employer] += money

##########雇用形態を変更する##########
    def change(self, work_type):
        self.work_type = work_type

##########正規雇用者へ転換する##########
    def change_regular(self):
        self.work_type =  WORKER_TYPE.REGULAR

##########退職する##########
    def retire(self):
        #雇用者エージェントがいる場合
        if self.employer is not None:
            self.employer.resign(self)
            self.employer = None
            self.work_type = WORKER_TYPE.JOBLESS
            self.length_of_service = 0

##########解雇通知する##########
    def fired(self, employer):
        self.employer = None
        self.work_type = WORKER_TYPE.JOBLESS
        self.length_of_service = 0

##########時間経過(勤続年数・年齢)##########
    def elapse(self, time_interval=1):
        self.length_of_service += time_interval
        self.age += time_interval

##########年齢を確認する##########
    def is_worker_age(self):
        return (WORKER_AGE.LOWER <= self.age <= WORKER_AGE.UPPER)

##########文字列オブジェクト###########
    def to_s(self):
        return "<EMPLOEE \n" + \
            "ID:" + str(self.id) + ", " + \
            "EMPLOYER = " + (str(self.employer.id) if self.employer is not None else "None") + ", " + \
            "EMP_TYPE = " + self.work_type + \
            "\n>"

##########年末処理###########
    def end(self):
        #if the law comes into force operation
        #self.change(WORKER_TPYE.REGULAR) by the length of service over 5
        pass

##########労働者エージェント作成クラス###############################################
class EmployeeFactory:
    def create(self, age = None):
        #労働者エージェント生成するため
        employee = Employee()
        if age is not None:
            employee.age = age
        employee.selection_strategy = se.RouletteSelectEmployerStrategy()
        return employee
