"""
Methods initializing some interesting game of life states
"""

import numpy as np
import random

def random_state(arr, density=0.5):
    """Return random array of 1s and 0s with specified density"""
    rows,cols = arr.shape
    arr = np.zeros( (rows,cols) )
    for i in range(rows):
        for j in range(cols):
            rand = random.random()
            if rand<density:
                arr[i][j]=1
    return arr

def glider( arr ):
    """Discovered 1969"""
    arr = np.zeros(arr.shape)
    m = int( min(arr.shape)/4 )
    arr[m][m:m+3]=1
    arr[m-1][m+2]=1
    arr[m-2][m+1]=1
    return arr

def lightweight_spaceship( arr ):
    """Discovered 1970"""
    a = np.zeros(arr.shape)
    m = int( min(arr.shape)*0.45 )
    a[m][m:m+4]=1
    a[m+1][m]=a[m+1][m+4]=1
    a[m+2][m]=1
    a[m+3][m+1]=a[m+3][m+4]=1
    return a

def copperhead( arr ):
    """c/10 orthogonal discovered 2016"""
    a = np.zeros(arr.shape)
    m = int( min(arr.shape)*0.5 )
    a[m][m:m+2]=1
    a[m-1][m:m+2]=1
    a[m-3][m-1:m+3]=1
    a[m-4][m-2:m] = a[m-4][m+2:m+4] =1
    a[m-5][m-3] = a[m-5][m+4] = 1
    a[m-7][m-3] = a[m-7][m+4] = 1
    a[m-8][m-3] = a[m-8][m+4] = 1
    a[m-8][m-1] = a[m-8][m+2] = 1
    a[m-9][m] = a[m-9][m+1] = 1
    a[m-10][m] = a[m-10][m+1] = 1
    a[m-11][m-2:m] = a[m-11][m+2:m+4] = 1
    return a
