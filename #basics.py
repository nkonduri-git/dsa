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
   x=globals()['a']# when we want to acess global and local variable in same function
   a=90
   b=9

   print(a)

something()
print(a)
print("outside",a)