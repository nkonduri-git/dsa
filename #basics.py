#basics
#arguments types named arguments
#ordered arguments
#default arguments if no argument passed default taken if argument is passed deault override


def person(name,age):
    print(name)
    print(age-8)
person(age=28,name="lol")

def person(name,age=90):
    print(name)
    print(age-8)
person(name="lol")

def sum(a,*b):
    c=a
    for i in b:
        c=c+i

    print(c)
sum(2,3,4,5,6)

#kwargs if a function doesnt know what they are even sending 
def person(name,**data):
  for i,j in data.items():
    print(i,j)
    print(name)
    print(data)

person('navin',age=28,city='mumbai',phonenumber=908989)
#global and local variable local preference highest and global inside the function we can use
#if global keyword then global access and changes made reflected over there
a=10
def something():
   #global a
   cx=globals()['a']# when we want to acess global and local variable in same function
   a=90
   b=9

   print(a)

something()
print(a)
print("outside",a)
#passing list to a function
def count(lst):
    even=0
    odd=0

    for i in lst:
        if i%2==0:
            even+=1
        else:
            odd+=1
    return even,odd

lst=[20,34,14,19,16,24,28,47,26]

even,odd=count(lst)

print("Even:() and odd:()".format(even,odd))
#fibanoci 
def fib(n):
    a=0
    b=1

    if n==1:
        print(a)

    else:
        print(a)
        print(b)
        

    print(a)
    print(b)

    for i in range(2,n):
        c=a+b
        a=b
        b=c
        print(c)


fib(5)

#factorial of a number


def fact(n):
    p=1
    
    for i in range(1,n+1):
         p=n*i
    
    return p

l=fact(5)
print(l)
#recursion of factorial

def fact(n):

    if n==0:
        return 1
    return n*fact(n-1)




result=fact(5)
print(result)
#lamda function
f=lambda a: a*a
result=f(5)
print(result)

#filter
def is_even(n):
    return n%2==0
nums=[3,2,6,8,4,6,2,9]
evens=list(filter(is_even,nums))
doubles=list(map(lambda n: n+2,evens))
from functools import reduce
def add_all(a,b):
    return a+b
sum=reduce(add_all,doubles)
print(sum)
print(evens)

#decoratores exsisting functions we can add extra code without even touching it 
def div(a,b):
    print(a/b)

def smart_div(func):

    def inner(a,b):
        if a <b:

          a,b=b,a
        return func(a,b)
    return inner

div1=smart_div(div)

div(2,4)

def raja():
    print("rajamouli")

raja()
#to use modules we will take the logic into 1 file then the processing into the other file 
#and import it 

#class basics
class Computer:
    def __init__(self,cpu,ram):
        self.cpu=cpu
        self.ram=ram
    def config(self):
        print("nani")
        print(self.cpu)
    def samantha(self):
        print("sandeep nahi")
        print(self.cpu)


com1=Computer("i5","8gb")
com1.config()#init required when we have multiple variables or aruguments with same name one argument pass all copy then we send the information into the class then y using self.keyword we will copy the data
com1.samantha()#self required to access the particular elements from the particular class functions

print("neney nani ney")
#self indicated the current object being used
#self left side constructor used 

class Computer:
    def __init__(self):
        self.name = "navin"
        self.age = 34

    def compare(self, other):
        if self.age == other.age:
            return True
        else:
            return False

c1 = Computer()  # Creating an instance of Computer class
c1.age = 90
c2 = Computer()

if c1.compare(c2):
    print("they are same")
else:
    print("they are different")

print(c1.name)
#variables
# we have instance variables
class Car:
    wheels=4
    def __init__(self):
        self.mil=90
        self.com="kia"

c1=Car()
c2=Car()
c1.mil=9

print(c1.com,c1.mil,c1.wheels)
print(c2.com,c2.mil,c2.wheels)
#method resolution order multiple functions with same name in the given parent class present the order taken from left to right
#multiple classes parent classes then we try to access the same function then go from left to right 
#generators
def topten:
   yield 5







values=topten()
print(values)