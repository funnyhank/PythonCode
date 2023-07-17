def collatz(number):
    if number % 2 == 0:
        print(number // 2)
        return number // 2

    else:
        print(number * 3 + 1)
        return number * 3 + 1


s = int(input("please input a number:"))
try:
    while s != 1:
        collatz(s)
        s = s - 1
except BaseException:
    print("haha")
