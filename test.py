class A:
    two=3
    def __init__(self, first):
        self.first=first

x = A(2)
print(x.first, x.two)
A.first=20
A.two=30

print(x.first, x.two)