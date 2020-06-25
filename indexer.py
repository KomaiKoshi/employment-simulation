class Indexer:
    '''
    Indexer class make unique serial number.
    '''
    def __init__(self):
        self.index = 0

    # NAME: gen
    # ユニークな番号を返す。
    def gen(self):
        '''
        Generate the serial number.
        RETURN: number(int)
        '''
        result = self.index
        self.index += 1
        return result
