"""Small geometry helpers"""
import math

def vector_norm(v):
    return math.sqrt(sum(x*x for x in v))
