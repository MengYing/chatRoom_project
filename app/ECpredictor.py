# -*- coding: utf-8 -*-

# =====================
# called by ECmain.py =
# ==== parameter meanings ====
# C initial value of the weights of Core Dictionary
# SC    of Side Core
# CX    of Core Extension
# N    of Side Core Extension
# D initial value of the weights from Dictionary
# P    from Previous sentence
# I    from Chinese particles and Interjections
# A    from ascii art
#
# PD from Previous-Decay
# S sensitivity for paramter adjusting
# R resolution to determine the label when there are at least closed emotion values

import ECtools as tool
    
def taiMethod(x = '', para = [0.3, 0.2, 0.2, 0.3, 0.15, 0.15, 0.35, 0.35], PD = 0.5, R = 0.1, P1 = [0, 0, 0, 0], P2 = [0, 0, 0, 0]):
    # ==== Loading Dictionary ====
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

# ==== Dictionary prediction PHASE ====
    C = para[0]
    SC = para[1]
    CX = para[2]
    N = para[3]
    D = para[4]
    P = para[5]
    I = para[6]
    A = para[7]

    CPre = tool.preDict(x, CsadDict, CsorryDict, CangryDict, ChappyDict, D * C)
    SCPre = tool.preDict(x, SCsadDict, SCsorryDict, SCangryDict, SChappyDict, D * SC)
    CXPre = tool.preDict(x, CXsadDict, CXsorryDict, CXangryDict, CXhappyDict, D * CX)
    NPre = tool.preDict(x, NEWsadDict, NEWsorryDict, NEWangryDict, NEWhappyDict, D * N)
    IPre = tool.preDict(x, IsadDict, IsorryDict, IangryDict, IhappyDict, I)
    APre = tool.preDict(x, AsadDict, AsorryDict, AangryDict, AhappyDict, A)

    CL = tool.labelMe(CPre, R)
    SCL = tool.labelMe(SCPre, R)
    CXL = tool.labelMe(CXPre, R)
    NL = tool.labelMe(CXPre, R)
    IL = tool.labelMe(IPre, R)
    AL = tool.labelMe(APre, R)

# ==== Previous sentense prediction PHASE ====
    PPre = [0.0, 0.0, 0.0, 0.0]
    for i in range(len(PPre)):
        PPre[i] += P * (P1[i] + PD * P2[i])

# ==== Output final prediction PHASE ====
    emo = [0.0, 0.0, 0.0, 0.0]
    for i in range(4):
        emo[i] += (CPre[i] + SCPre[i] + CXPre[i] + NPre[i] + IPre[i] + APre[i])

# ==== normalize emo[] ====
    emoSum = 0.000001    #    avoiding dividing zero
    for i in range(len(emo)):
        emoSum += emo[i]
    for i in range(len(emo)):
        emo[i] /= emoSum

    return emo + [CL, SCL, CXL, NL, IL, AL]