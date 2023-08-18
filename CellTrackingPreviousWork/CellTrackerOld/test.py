def a(func):
    def func2(*args, **kwargs):
        func(*args, **kwargs)

    return func2


@a
def b(name):
    print(f'Hello, {name}!')


b('Eli')