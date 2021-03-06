#!/usr/bin/python
# -*- coding: UTF-8 -*-


class JustCounter:
    #__secretCount = 0

    def __init__(self):
        self.secretCount = 0

    def countObjectSecretCount(self):
        self.secretCount += 1

    @staticmethod
    def countClassSecretCount():
        JustCounter.secretCount += 1

    def printObjectSecretCount(self):
        print "属性: ", self.secretCount

    @staticmethod
    def printClassSecretCount():
        print "类的属性: ", JustCounter.secretCount


counter1 = JustCounter()
counter2 = JustCounter()
counter1.countObjectSecretCount()
JustCounter.countClassSecretCount()
counter2.countObjectSecretCount()


print "对象1的", counter1.printObjectSecretCount()  # 输出: 对象1的属性:  1
print JustCounter.printClassSecretCount()  # 输出: 类的属性:  1
print "对象2的", counter2.printObjectSecretCount()  # 输出: 对象2的属性:  2


class Vector:

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __str__(self):
        return "Vector( %d, %d)" % (self.a, self.b)

    def __add__(self, other):
        return Vector(self.a + other.a, self.b + other.b)


v1 = Vector(1, 2)
v2 = Vector(3, 4)
print v1 + v2  # 输出: Vector( 4, 6)


class Parent:  # 定义父类方法
    parentAttr = 100

    def __init__(self):
        print "调用父类的构造函数"

    def parentMethond(self):
        print "调用父类的方法"

    def helloWorld(self):
        print "调用父类方法helloWorld"

    def setAttr(self, attr):
        Parent.parentAttr = attr

    def getAttr(self):
        print "父类属性: ", Parent.parentAttr


class Child(Parent):  # 定义子类

    def __init__(self):
        print "调用子类构造函数方法"

    def childMethod(self):
        print "调用子类方法"

    def helloWorld(self):
        print "调用子类方法helloWorld"


c = Child()  # 输出: 调用子类构造函数方法
c.childMethod()  # 输出：调用子类方法
c.parentMethond()  # 输出：调用父类的方法
c.setAttr(200)
c.getAttr()  # 输出：父类属性: 200
c.helloWorld()  # 输出：调用子类方法helloWorld