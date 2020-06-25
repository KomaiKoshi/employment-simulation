# General function
# list から None を取り除いた list を返す。
def compact(list):
    return [elem for elem in list if elem != None]

# list から == で比較して同一のものを削除する
def uniq(list):
    return [elem for elem in list if elem != None or (elem not in list)]

def p(obj):
    print(obj)
