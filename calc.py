
#when we want to acess only one particular function of other file
#if name is not given then module name is given then it will call the other file functions as well 

def add():
    print("result1 is ")
def sub():
    print("result2 is")

def main():
    add()
    sub()
if __name__ =="__main":
    main()
