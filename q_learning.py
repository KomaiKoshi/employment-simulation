import numpy as np
import employer
import copy
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

##########Q学習のクラス##########
class Q_learning:

    #初期設定
    def __init__(self, alpha, gamma, table_structure, act_method):
        '''
        PARAM: alpha (float) ; learning rate
        PARAM: gamma (float) ; discount rate
        PARAM: table_structure (tuple, list) ; Q table structure as tuple, e.g. in the case that there are two state A as 10 grade and B as 5 grade. In addition, there are 4 actions. Then, the structure is (10, 5, 4).
        PARAM: act_method (QLaerningAction) ; Action class object. 
        '''
        #パラメータ設定
        self.table_structure = tuple(table_structure)
        self.q_table = np.zeros(table_structure)
        self.alpha = alpha                                     
        self.gamma = gamma                                       
        self.act_list = [i for i in range(table_structure[-1])]  
        self.act_method = act_method                               

    #Q値の更新
    def update(self, prev_env, next_env, act, reward):
        prev_env = tuple(prev_env)
        next_env = tuple(next_env)
        prev_q_val = self.q_table[prev_env][act]
        next_mq_val = max(self.q_table[next_env])
        self.q_table[prev_env][act] = prev_q_val + self.alpha * (reward + self.gamma * next_mq_val - prev_q_val)

    #行動方法(EpsilonGreedyMethod)によって行動する
    def action(self, prev_env):
        return self.act_method.action(self.q_table, prev_env, self.act_list)


class QLearningAction:
    def action(self, q_table, prev_env, act_list):
        raise Exception

###########EpsilonGreedyMethodのクラス(行動選択方法)##########
class EpsilonGreedyMethod(QLearningAction):
    def __init__(self, epsilon):
        self.epsilon = epsilon
    def action(self, q_table, prev_env, act_list):
        prev_env = tuple(prev_env)
        action = None
        if np.random.uniform(0, 1) < self.epsilon:
            action = np.random.choice(act_list)
        else:
            action = np.argmax(q_table[prev_env])
        if action is None:
            raise Exception
        return action


