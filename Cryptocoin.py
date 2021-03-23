


class cryptocoin:
    def __init__(self, name, codeCoinbase, codeAlphaVantage, min, proffit, totalBuyed, isbuyed, isBlocked):
        self.name = name
        #Abbreviation that appears in exchange
        self.codeCoinbase = codeCoinbase
        # Abbreviation that appears in the consulted data history
        self.codeAlphaVantage = codeAlphaVantage
        #Minimum to invest
        self.min = min
        #Proffit until now
        self.proffit = proffit
        #Total amount buyed of this coin
        self.totalBuyed = totalBuyed
        #Is still a order in this crypto(Buyed and not selled yet)
        self.isbuyed = isbuyed
        #It is blocked by me
        self.isBlocked = isBlocked
        self.profileCoinbaseID = None


    def getName(self):
        return self.name


