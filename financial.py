import pandas as pd
import statsmodels.api as sm
from time import sleep
import itertools

def truncate(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])

def pad(iterable, padding=0, length=8):
    '''
    >>> iterable = [1,2,3]
    >>> list(pad(iterable))
    [0, 0, 0, 0, 0, 1, 2, 3]
    '''
    while len(iterable) < length:
        iterable.insert(0, padding)
    return iterable

def numberToBase(n, b):
    '''
    >>> n = 100
    >>> b = 14
    >>> numberToBase(n, b)
    [7, 2]
    '''
    digits = []
    while n:
        digits.append(int(n % b))
        n /= b
    return digits[::-1]

def toShiftRegister(shift_counter, rows, cols):
    shift_counter = numberToBase(shift_counter, rows)
    shift_counter = pad(shift_counter, 0, cols)
    return shift_counter


df_adv = pd.read_csv('stocks.csv', index_col=0, delimiter=";")
indep_variables = ['ANTM', 'CI', 'FLVEX']
dep_variables   = ['AET']
X = df_adv[indep_variables]
y = df_adv[dep_variables]

df_adv.head()

'''
Create dynamic window
'''
dyn_window_size = X.last_valid_index()/2
number_of_combinations = dyn_window_size**3
#X = sm.add_constant(X)
r2_max = 0
shift_counter_next = 0

for shift_counter in range(number_of_combinations):
    # get original data and shift it according to our shift register
    X_dyn = X.copy()
    shift_register = toShiftRegister(shift_counter, dyn_window_size, len(indep_variables))
    for col, series in X_dyn.iteritems():
        X_dyn[col] = series.shift(shift_register[X_dyn.columns.get_loc(col)])
    
    # perform Ordinary Least Squares fit on dynamic window
    X_dyn  = X.tail(dyn_window_size)
    y_dyn  = y.tail(dyn_window_size)
    est = sm.OLS(y_dyn, X_dyn).fit()
    r2  = est.rsquared
    #print r2
    if r2 > r2_max:
        r2_max = r2
        est_max = est

    '''
    Diagnostics
    '''
    ################################
    if shift_counter == shift_counter_next: # update completion percentage every nth iterations to speed run time
        shift_counter_next = shift_counter + 1250
        print "Percent complete (%): ", truncate((shift_counter/float(number_of_combinations))*100, 4)
    # print "(Last 10 records), X_dyn.tail(10)
        print "Shift register: ", shift_register, "| Count: ", shift_counter
    # print est.summary()
    # raw_input("Press Enter to continue...")
    ################################
    
print est_max.summary()
