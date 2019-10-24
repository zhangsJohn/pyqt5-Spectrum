import numpy as np


INTER_KINDS = ['linear', 'nearest', 'zero', 'slinear',
               'quadratic', 'cubic', 'previous', 'next']
GAUSS_FUN = ['gauss1', 'gauss2', 'gauss3', 'gauss4', 'gauss5']
EXP_FUN = ['exp1', 'exp2']
POW_FUN = ['power1', 'power2']
POLY_FUN = ['poly1', 'poly2', 'poly3', 'poly4', 'poly5', 'poly6', 'poly7']
METHOD_LIST = {0: GAUSS_FUN, 1: POLY_FUN, 2: EXP_FUN, 3: POW_FUN,
               4: INTER_KINDS}


def gauss1(x, a, b, c):
    '''a * e^[-(x - b)^2 / (2 * c^2)]'''
    return a * np.exp(-(x - b)**2 / (2 * c**2))


def gauss2(x, *param):
    '''a0*e^[-(x - b0)^2 / (2 * c0^2)] +\
        a1*e^[-(x - b1)^2 / (2 * c1^2)]'''
    return param[0]*np.exp(-(x - param[1])**2 / (2 * param[2]**2)) +\
        param[3]*np.exp(-(x - param[4])**2 / (2 * param[5]**2))


def gauss3(x, *param):
    '''a0*e^[-(x - b0)^2 / (2 * c0*^2)] +\
        a1*e^[-(x - b1)^2 / (2 * c1^2)] +\
            a2*e^[-(x - b2)^2 / (2 * c2^2)]'''
    return param[0]*np.exp(-(x - param[1])**2 / (2 * param[2]**2)) +\
        param[3]*np.exp(-(x - param[4])**2 / (2 * param[5]**2)) +\
        param[6]*np.exp(-(x - param[7])**2 / (2 * param[8]**2))


def gauss4(x, *param):
    '''a0*e^[-(x - b0)^2 / (2 * c0^2)] +\
        a1*e^[-(x - b1)^2 / (2 * c1^2)] +\
            a2*e^[-(x - b2)^2 / (2 * c2^2)] +\
                a3*e^[-(x - b3)^2 / (2 * c3^2)]'''
    return param[0]*np.exp(-(x - param[1])**2 / (2 * param[2]**2)) +\
        param[3]*np.exp(-(x - param[4])**2 / (2 * param[5]**2)) +\
        param[6]*np.exp(-(x - param[7])**2 / (2 * param[8]**2)) +\
        param[9]*np.exp(-(x - param[10])**2 / (2 * param[11]**2))


def gauss5(x, *param):
    '''a0*e^[-(x - b0)^2 / (2 * c0^2)] +\
        a1*e^[-(x - b1)^2 / (2 * c1^2)] +\
        a2*e^[-(x - b2)^2 / (2 * c2^2)] +\
        a3*e^[-(x - b3)^2 / (2 * c3^2)] +\
        a4*e^[-(x - b4)^2 / (2 * c4^2)]'''
    return param[0]*np.exp(-(x - param[1])**2 / (2 * param[2]**2)) +\
        param[3]*np.exp(-(x - param[4])**2 / (2 * param[5]**2)) +\
        param[6]*np.exp(-(x - param[7])**2 / (2 * param[8]**2)) +\
        param[9]*np.exp(-(x - param[10])**2 / (2 * param[11]**2)) +\
        param[12]*np.exp(-(x - param[13])**2 / (2 * param[14]**2))


def exp1(x, a, b):
    '''a*e^(b*x)'''
    return a*np.exp(b*x)


def exp2(x, a, b, c, d):
    '''a0*e^(b0*x) +a1*e^(b1*x)'''
    return a*np.exp(b*x) + c*np.exp(d*x)


def power1(x, a, b):
    '''a*x^b'''
    return a*x**b


def power2(x, a, b, c):
    '''a*x^b + c'''
    return a*x**b+c


def poly1(x, a, b):
    '''a*x + b'''
    return a*x + b


def poly2(x, *param):
    '''a0*x + a1*x + b'''
    return param[2]*x**2 + param[1]*x + param[0]


def poly3(x, *param):
    '''a0*x + a1*x + a2*x + b'''
    return param[3]*x**3 + param[2]*x**2 + param[1]*x + param[0]


def poly4(x, *param):
    '''a0*x + a1*x + a2*x + a3*x + b'''
    return param[4]*x**4 + param[3]*x**3 + param[2]*x**2 + param[1]*x + param[0]


def poly5(x, *param):
    '''a0*x + a1*x + a2*x + a3*x + a4*x + b'''
    return param[5]*x**5 + param[4]*x**4 + param[3]*x**3 \
        + param[2]*x**2 + param[1]*x + param[0]


def poly6(x, *param):
    '''a0*x + a1*x + a2*x + a3*x + a4*x + a5*x + b'''
    return param[6]*x**6 + param[5]*x**5 + param[4]*x**4\
        + param[3]*x**3 + param[2]*x**2 + param[1]*x + param[0]


def poly7(x, *param):
    '''a0*x + a1*x + a2*x + a3*x + a4*x + a5*x + a6*x + b'''
    return param[7]*x**7 + param[6]*x**6 + param[5]*x**5 + param[4]*x**4\
        + param[3]*x**3 + param[2]*x**2 + param[1]*x + param[0]
