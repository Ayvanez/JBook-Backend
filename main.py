def huy(func):
    def f():
        print("before func")
        func()
        print('after func')

    return f


@huy
def print_1():
    print(1)


if __name__ == '__main__':
    print_1()
    print_1()
