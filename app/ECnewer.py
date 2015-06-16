# -*- coding: utf-8 -*-

import ECtools as tool

def newLearn (newTerm = '', z = 0):
    CsadDict = tool.loadDict('./app/dic/cdic/sad.dic')
    CsorryDict = tool.loadDict('./app/dic/cdic/sorry.dic')
    CangryDict = tool.loadDict('./app/dic/cdic/angry.dic')
    ChappyDict = tool.loadDict('./app/dic/cdic/happy.dic')
    SCsadDict = tool.loadDict('./app/dic/sdic/sad.sdic')
    SCsorryDict = tool.loadDict('./app/dic/sdic/sorry.sdic')
    SCangryDict = tool.loadDict('./app/dic/sdic/angry.sdic')
    SChappyDict = tool.loadDict('./app/dic/sdic/happy.sdic')
    CXsadDict = tool.loadDict('./app/dic/xdic/sad.xdic')
    CXsorryDict = tool.loadDict('./app/dic/xdic/sorry.xdic')
    CXangryDict = tool.loadDict('./app/dic/xdic/angry.xdic')
    CXhappyDict = tool.loadDict('./app/dic/xdic/happy.xdic')
    NEWsadDict = tool.loadDict('./app/dic/ndic/sad.ndic')
    NEWsorryDict = tool.loadDict('./app/dic/ndic/sorry.ndic')
    NEWangryDict = tool.loadDict('./app/dic/ndic/angry.ndic')
    NEWhappyDict = tool.loadDict('./app/dic/ndic/happy.ndic')
    IsadDict = tool.loadDict('./app/dic/idic/sad.idic')
    IsorryDict = tool.loadDict('./app/dic/idic/sorry.idic')
    IangryDict = tool.loadDict('./app/dic/idic/angry.idic')
    IhappyDict = tool.loadDict('./app/dic/idic/happy.idic')
    AsadDict = tool.loadDict('./app/dic/adic/sad.adic')
    AsorryDict = tool.loadDict('./app/dic/adic/sorry.adic')
    AangryDict = tool.loadDict('./app/dic/adic/angry.adic')
    AhappyDict = tool.loadDict('./app/dic/adic/happy.adic')

    sadDict = CsadDict + SCsadDict + CXsadDict + NEWsadDict + IsadDict + AsadDict
    sorryDict = CsorryDict + SCsorryDict + CXsorryDict + NEWsorryDict + IsorryDict + AsorryDict
    angryDict = CangryDict + SCangryDict + CXangryDict + NEWangryDict + IangryDict + AangryDict
    happyDict = ChappyDict + SChappyDict + CXhappyDict + NEWhappyDict + IhappyDict + AhappyDict
    
    wNEWsad = open('./app/dic/ndic/sad.ndic', 'a')
    wNEWsorry = open('./app/dic/ndic/sorry.ndic', 'a')
    wNEWangry = open('./app/dic/ndic/angry.ndic', 'a')
    wNEWhappy = open('./app/dic/ndic/happy.ndic', 'a')

    if z != '':
        z = int(z)
        if (z == 1) and (newTerm not in sadDict):
            wNEWsad.writelines(newTerm.encode('utf-8') + '\n')
        elif (z == 2) and (newTerm not in sorryDict):
            wNEWsorry.writelines(newTerm.encode('utf-8') + '\n')
        elif (z == 3) and (newTerm not in angryDict):
            wNEWangry.writelines(newTerm.encode('utf-8') + '\n')
        elif (z == 4) and (newTerm not in happyDict):
            wNEWhappy.writelines(newTerm.encode('utf-8') + '\n')

    wNEWsad.close()
    wNEWsorry.close()
    wNEWangry.close()
    wNEWhappy.close()

    return