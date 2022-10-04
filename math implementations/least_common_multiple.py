### INPUT
### denominators = list of integer numbers

### OUTPUT
### returns the least common multuiple of denominators

def least_common_multiple(denominators):
    import math
    import functools as ft
    return ft.reduce(lambda a,b: a*b // math.gcd(a,b), denominators)