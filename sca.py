#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This is code that uses a greedy algorithm to attempt to 
solve the min set cover problem.

The way this code works by repeatedly taking the subset that
includes the largest number of elements in the universe that the subsets in
the result set of subsets have not yet inluded until a result that includes a set
of subsets that includes every element in the universe can be returned.
"""

from random import randint
from random import randrange
import time
import sys

MAX=100

def randset(size, rand):
    s = []
    l = size
    a = randint(0, rand)
    while(l > 0):
        s.append(a)
        while(a in s):
            a = randint(0, rand)
        l = l - 1
    return s

def gen_ss_h(size):
    rsl = []
    for i in randrange(0, size):
        rsl.append([])
    return rsl
    
def gen_ss(universe):
    mu = map(lambda a: (a, randint(5)), universe)
    us = len(universe)
    ss = gen_ss_h(us)
    sss = len(ss)
    while(len(mu) > 0):
        m = randint(0, us)
        i = randint(0, sss)
        ss[i].append(mu[m][0])
        mu[m][1] = mu[m][1] - 1
        if(not mu[m][1]):
            del mu[m]
            us = us - 1
    return filter(lambda a: a!=[], ss)
        
    
def greedy(universe, ss):
    rsl = []
    tmp = None
    while(len(universe) > 0):
        tmp = max_unknown(universe, ss)
        ss.remove(tmp)
        for i in tmp:
            if(i in universe):
                universe.remove(i)
        rsl.append(tmp)
        if(len(ss) == 0):
            return []
    return rsl
    
        
def max_unknown(universe, ss):
    s_max = []
    cs_max = 0
    for s in ss:
        c = one_unknown(universe, s)
        if(c > cs_max):
            cs_max = c
            s_max = s
    return s_max
        
    

def one_unknown(universe, s):
    c = 0
    for i in s:
        if(i in universe):
            c = c + 1
    return c


def ebay_q(set):
    b = 0
    c = 0
    for i in set:
        if i > b:
            c = c + 1
            b = i
    return c

def run_sca(s, file):
    uni = range(0, s)
    ss = []
    c = randint(0, 1000)
    while(c > 0):
        ss.append(randset(randint(0, int(len(uni)/2)), s))
        c = c - 1
    rs = []
    time1 = time.time()
    rs = greedy(uni, ss)
    time2 = time.time()
    mytime = (time2 - time1) * 1000
    line = "{0}, {1}, {2}, {3}".format(mytime, s, len(ss), len(rs))
    file.write(line + '\n')
    print line
    
    
def run_ebay(size, file):
    s = randset(size, 5000)
    r = ebay_q(s)
    rs = "{0}, {1}".format(size, r)
    print rs
    file.write(rs + '\n')
    
#if __name__ == '__main__':
#    f = open("data.csv", 'w')
#    f.write("Time, Universe Size, Number of Subsets, Size of Result SuperSet \n")
#    tests = [10, 25, 50, 100, 500, 1000]
#    for i in tests:
#        for j in range(10):
#            run_sca(i, f)

if __name__ == '__main__':
    f = open("data2.csv", 'w')
#    f.write("Size, Result \n")
    print "Size, Result \n"
    tests = range(1000)
    for i in tests:
        run_ebay(i, f)
    
    