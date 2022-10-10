### INPUT
### n = single integer

### USEAGE
### a = list(divisorGenerator(n))

def number_divisors(n):
    import math
    # Courtesy of https://stackoverflow.com/questions/171765/what-is-the-best-way-to-get-all-the-divisors-of-a-number
    large_divisors = []
    for i in range(1, int(math.sqrt(n) + 1)):
        if n % i == 0:
            yield i
            if i*i != n:
                large_divisors.append(int(n / i))
    for divisor in reversed(large_divisors):
        yield divisor