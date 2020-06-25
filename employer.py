import random
import copy
import numpy as np
from constant import *
import general
import indexer
import distribution
import q_learning as ql

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")


##########雇用者エージェント作成クラス##########
class LMMiniEmployerFactory:
    def create(self):
        employer = Employer()
        employer.examql  = MinExamEGQLearning(employer)
        employer.renewql = MinRenewEGQLearning(employer)
        employer.changeql = ChangeEmploymentQLearning(employer)
        return employer


#########労働市場##########
class LMLearningCore:
    action_structure = [2]
    action_map = [True, False]
    
    def __init__(self, ql_core):
        self.name = "CORE"
        self.ql_core = ql_core

    def state(self, employer):
        raise Exception

    def reward(self, employer):
        raise Exception

    def action(self, state, employee):
        act = self.ql_core.action(state)
        return LMLearningCore.action_map[act]

    #Q学習更新
    def update(self, pstate, nstate, action, reward):
        action_index = LMLearningCore.action_map.index(action) if action in LMLearningCore.action_map else 0
        self.ql_core.update(pstate, nstate, action_index, reward)

    def icheck(self, granularity, index):
        if index < 0:
            index = 0
        if index >= granularity:
            index = granularity - 1
        return index


##########雇用転換のQ学習##########
class ChangeEmploymentQLearning(LMLearningCore):

    #初期設定
    def __init__(self, employer):
        self.alpha = 0.9
        self.gamma = 0.5
        self.epsilon = 0.1
        self.granularity = 10
        self.state_structre = [self.granularity,self.granularity,self.granularity]
        action_method = ql.EpsilonGreedyMethod(self.epsilon)
        ql_instance = ql.Q_learning(self.alpha, self.gamma, self.state_structre + LMLearningCore.action_structure, action_method)
        super(ChangeEmploymentQLearning, self).__init__(ql_instance)
        self.name = "MinChangeQL"
        self.employer = employer

    #状態
    def state(self, employer, employee):  #Q学習Steteの要素を設定する

        #np.linspace(最初の値,最後の値,要素数)
        bin = np.linspace(1.0 / self.granularity, 1.0, self.granularity)
        
        #昨年と今年のGDP
        pgdp = employer.assigned_work(-2)
        ngdp = employer.assigned_work(-1)
        std = np.std(employer.assignment_work_history)
        diff = abs((pgdp - ngdp + 1) / (std + 1))

        #数値をある範囲でグループ化する
        index_1 = np.digitize(diff, bins=bin)
        if index_1 < 0:
            index_1 = 0
        if index_1 >= self.granularity:
            index_1 = self.granularity - 1
        
        #Q学習Steteの要素を設定する
        #年齢割合
        age_ratio = (employee.age - WORKER_AGE.LOWER) / (WORKER_AGE.UPPER - WORKER_AGE.LOWER)
        index_2 = np.digitize(age_ratio, bins=bin)
        index_2 = self.icheck(self.granularity, index_2)

        #勤続年数
        los_retio = (employee.length_of_service - WORKER_AGE.LOWER) / (WORKER_AGE.UPPER - WORKER_AGE.LOWER)
        index_3 = np.digitize(los_retio, bins=bin)
        index_3 = self.icheck(self.granularity, index_3)

        #Q学習Steteの要素を設定する
        return [index_1,index_2,index_3] 

    #報酬
    def reward(self, employer):
        #かなり小さい値になると思うので、標準偏差は小さくする必要がある
        rw = distribution.normal((employer.remained_work() + 1) / (employer.assigned_work() + employer.processed_work() + 1), 0, 0.01)
        return rw


##########入社試験のQ学習##########
class MinExamEGQLearning(LMLearningCore):

    #初期設定
    def __init__(self, employer):
        self.alpha = 0.9
        self.gamma = 0.5
        self.epsilon = 0.1
        self.granularity = 10
        self.state_structre = [self.granularity,self.granularity]
        action_method = ql.EpsilonGreedyMethod(self.epsilon)
        #インスタンス作成
        ql_instance = ql.Q_learning(self.alpha, self.gamma, self.state_structre + LMLearningCore.action_structure, action_method)
        super(MinExamEGQLearning, self).__init__(ql_instance)
        self.name = "MinExamQL"
        self.employer = employer

    #状態
    def state(self, employer, employee):  #Q学習Steteの要素を設定する
        '''
        index 1: granularity is 10
        ( current task / previous task ) / standard deviation of task 
        '''

        #np.linspace(最初の値,最後の値,要素数)
        bin = np.linspace(1.0 / self.granularity, 1.0, self.granularity)
        
        #昨年と今年のGDP
        pgdp = employer.assigned_work(-2)
        ngdp = employer.assigned_work(-1)
        
        #標準偏差とは
        #配列に含まれる要素のデータの散らばり具合を示す指標の１つとなるものを求める関数
        #GDPから与えれた仕事量のばらつきを求める
        #平均点±標準偏差のなかに大体の値がある
        std = np.std(employer.assignment_work_history)
        diff = abs((pgdp - ngdp + 1) / (std + 1))

        #数値をある範囲でグループ化する
        index_1 = np.digitize(diff, bins=bin)
        if index_1 < 0:
            index_1 = 0
        if index_1 >= self.granularity:
            index_1 = self.granularity - 1
        
        #Q学習Steteの要素を設定する
        #年齢割合
        age_ratio = (employee.age - WORKER_AGE.LOWER) / (WORKER_AGE.UPPER - WORKER_AGE.LOWER)
        index_2 = np.digitize(age_ratio, bins=bin)
        index_2 = self.icheck(self.granularity, index_2)

        #Q学習Steteの要素を設定する
        return [index_1,index_2] 

    #報酬
    def reward(self, employer):
        #かなり小さい値になると思うので、標準偏差は小さくする必要がある
        rw = distribution.normal((employer.remained_work() + 1) / (employer.assigned_work() + employer.processed_work() + 1), 0, 0.01)
        return rw
        
        



#########契約更新のQ学習クラス##########
class MinRenewEGQLearning(LMLearningCore):
    
    def __init__(self, employer):
        self.alpha = 0.9
        self.gamma = 0.5
        self.epsilon = 0.1
        self.granularity = 10
        self.state_structre = [self.granularity,self.granularity,self.granularity]    #Q学習Steteの要素を設定する
        action_method = ql.EpsilonGreedyMethod(self.epsilon)
        ql_instance = ql.Q_learning(self.alpha, self.gamma, self.state_structre + LMLearningCore.action_structure, action_method)
        super(MinRenewEGQLearning, self).__init__(ql_instance)
        self.name = "MinRenewQL"
        self.employer = employer


    def state(self, employer, employee):    #Q学習Steteの要素を設定する
        '''
        index 1: granularity is 10
        ( current task / previous task ) / standard deviation of task 
        '''
        bin = np.linspace(1.0 / self.granularity, 1.0, self.granularity)
        pgdp = employer.assigned_work(-2)
        ngdp = employer.assigned_work(-1)
        std = np.std(employer.assignment_work_history)
        diff = abs((pgdp - ngdp + 1) / (std + 1))
        index_1 = np.digitize(diff, bins=bin)
        if index_1 < 0:
            index_1 = 0
        if index_1 >= self.granularity:
            index_1 = self.granularity - 1
        
        #Q学習Steteの要素を設定する
        #年齢割合
        age_ratio = (employee.age - WORKER_AGE.LOWER) / (WORKER_AGE.UPPER - WORKER_AGE.LOWER)
        index_2 = np.digitize(age_ratio, bins=bin)
        index_2 = self.icheck(self.granularity, index_2)

        #勤続年数
        los_retio = (employee.length_of_service - WORKER_AGE.LOWER) / (WORKER_AGE.UPPER - WORKER_AGE.LOWER)
        index_3 = np.digitize(los_retio, bins=bin)
        index_3 = self.icheck(self.granularity, index_3)

        #Q学習Steteの要素を設定する
        return [index_1,index_2,index_3]  


    def reward(self, employer):
        #かなり小さい値になると思うので、標準偏差は小さくする必要がある
        rw = distribution.normal((employer.remained_work() + 1) / (employer.assigned_work() + employer.processed_work() + 1), 0, 0.01)
        return rw














##########雇用者エージェントのクラス##########
class Employer:
    id_counter = indexer.Indexer()

    #初期設定
    def __init__(self):
        self.id = Employer.id_counter.gen()
        self.employees = []
        self.assignment_work_history = []
        #self.processed_work = 0.0
        self.time = 0
        self.examql = None
        self.renewql = None
        self.changeql = None

    #雇用転換
    def change_employment(self, employee):
        state = self.changeql.state(self,employee)    
        return self.changeql.action(state, employee)

    #入社試験
    def exam(self, employee):
        state = self.examql.state(self,employee)    
        return self.examql.action(state, employee)

    #契約更新
    def renew(self, employee):
        state = self.renewql.state(self,employee)
        return self.renewql.action(state, employee)
    
    #雇用転換(合格)
    def regular_employ(self, employee):
        if employee in self.employees:
            pstate = self.changeql.state(self,employee)
            action = True
            employee.change_regular()
            nstate = self.changeql.state(self,employee)
            reward = self.changeql.reward(self)
            self.changeql.update(pstate, nstate, action, reward)

    #雇用転換(不合格)
    def temporary_employ(self, employee):
        if employee in self.employees:
            pstate = self.examql.state(self,employee)
            action = False
            nstate = self.changeql.state(self,employee)
            reward = self.changeql.reward(self)
            self.changeql.update(pstate, nstate, action, reward)

    #入社試験(合格)
    def employ(self, employee, gdp_index):
        if employee not in self.employees:
            pstate = self.examql.state(self,employee)
            action = True
            employee.employed(self,gdp_index)
            self.employees.append(employee)
            nstate = self.examql.state(self,employee)
            reward = self.examql.reward(self)
            self.examql.update(pstate, nstate, action, reward)

    #入社試験(不合格)
    def reject(self, employee):
        if employee not in self.employees:
            pstate = self.examql.state(self,employee)
            action = False
            nstate = self.examql.state(self,employee)
            reward = self.examql.reward(self)
            self.examql.update(pstate, nstate, action, reward)

    #契約更新(合格)
    def keep(self, employee):
        if employee in self.employees:
            pstate = self.renewql.state(self, employee)
            action = True
            nstate = self.renewql.state(self, employee)
            reward = self.renewql.reward(self)
            self.renewql.update(pstate, nstate, action, reward)        

    #契約更新(不合格)
    def fire(self, employee):
        if employee in self.employees:
            pstate = self.renewql.state(self, employee)
            action = False
            employee.fired(self)
            self.employees.remove(employee)
            nstate = self.renewql.state(self, employee)
            reward = self.renewql.reward(self)
            self.renewql.update(pstate, nstate, action, reward)
                  
    #労働者エージェントの辞職
    def resign(self, employee):
       if employee in self.employees:
            self.employees.remove(employee)

    #雇用形態をカウント
    def count_worker_type(self, work_type):
        return len([e for e in self.employees if e.work_type == work_type])

    #正規労働者をカウント
    def count_regular(self):
        return self.count_worker_type(WORKER_TYPE.REGULAR)

    #非正規労働者をカウント
    def count_temporary(self):
        return self.count_worker_type(WORKER_TYPE.TEMPORARY)

    #労働者エージェントをカウント
    def count_employee(self):
        return len(self.employees)

    #GDPから仕事を割り振る
    def set_work(self, work):
        self.assignment_work_history.append(work)

    def assigned_work(self, index=-1):
        if index < 0:
            if abs(index) > len(self.assignment_work_history):
                return 0
        else:
            if index + 1 > len(self.assignment_work_history):
                return 0
        return self.assignment_work_history[index]

    #行った仕事量
    def processed_work(self):
        return sum([e.work() for e in self.employees])

    #残った仕事量
    def remained_work(self):
        return self.assigned_work() - self.processed_work()
    
    #時間経過
    def elapse(self, time_interval=1):
        self.time += time_interval

    #リセットする
    def clear(self):
        self.employees.clear()
        self.assignment_work = 0
        self.time = 0

    def to_s(self):
        l = [e.to_s() for e in self.employees]
        emoloyee_str = ', \n'.join(l)

        return '<EMPLOER ' + \
            'ID:' + str(self.id) + \
            ', ' + \
            'EMPLOYEES = \n' + emoloyee_str + \
            'T_TASK = ' + str(self.assignment_work) + \
            'P_TASK = ' + str(self.processed_work) + \
            '\n>'
