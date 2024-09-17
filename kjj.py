def translate(number, base=2):
    alpabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    result = []
    while number > 0:
        result.append(alpabet[(number % base)])
        number //= base
    return ''.join(reversed(result))


def from_to(number, num_base, base=10):
    pre_result = 0
    i = 0
    while number > 0:
        pre_result += number % 10 * 7 ** i
        number //= 10
        i += 1
    return translate(pre_result, base)


# for i in range(1000, 10000):
#     s = str(i)
#     a, b, c, d = [int(j) for j in s]
#     li = [str(a * b), str(c * d)]
#     li.sort(key=lambda x: int(x), reverse=True)
#     print(li)
#     if int(''.join(li)) == 274:
#         print(i)
#         break

print(5 * 512 ** 3 + 2 ** 64 ** 6 - 7 * 8 ** 4 - 111)
