import math

def standard_normal(x):
    return normal(x, 0, 1)

#正規分布を求める
#x 　 データの値
#avg　データの平均
#dist 分散
def normal(x, avg, dist):
    return (math.exp(-(x - avg) ** 2 / (2 * dist**2))) / math.sqrt(2 * math.pi * dist**2)
