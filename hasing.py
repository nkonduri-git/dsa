#hasing process where a number converted into the digit in the range using this process
#the number of address points are reduced so that space wastage reduced if array is smaller than the spaces 
#has value is a integer
#hash values same then linked list arrange those 2 
#need to add the element then get the hash address insert it in the beggining of the linked list 
# #that is done if there  are multiple values with same hash address .
#for searching get the hash address and search in the corresponding linked list
#similarly for deletion we will search it then delete it 
#list_lnegth is lamda then lambda comparisions if it is unsuccesfull search
#if successfull comparision then lamda/2 
#the table size choosen such that number of records/table size =10

class studentRecord:
    def __init__(self,i,name):
        self.studentId = i
        self.studentName = name
    def get_student_id(self):
        return self.studentId
    def set_student_id(self,i):
        self.studentId = i
    def __str__(self):
        return str(self.studentId) + " " + self.studentName
############3
class Node:
    def __init__(sself,value):
        self.info = value
        self.link = None
###########
class SingleLinkedList:
    def __init__(self):
        self.start = None
    def display_list(self):
        if self.start is None;
            print("__")
            return
        p=self.start
        while p is not None:
            print(p.info , "" , end="")
    def search(self,x):
        p=self.start
        while p is not None:
            if p.info.get_student_id() == x:
                return p.info
            p=p.link
        else:
            return None
    def insert_in_beginning(self,data):
        temp=Node(data)
        temp.link = self.start
        self.start = temp
    def delete_node(self,x):
        if self.start is None:
            print("list is empty")
            return
        #deletion of first  node
        if self.start.info.get_student_id() == x:
            self.start = self.start.link
            return
        p=self.start
        while p.link is not None:
            if p.link.info.get_student_id() == x:
                break
            p=p.link

        if p.link is None:
            print("Element ",x,"not in list")
        else:
            p.link=p.link.link
#####################
class HashTable:
    def __init__(self,tablesize):
        self.m=tablesize
        self.array = [None]*self.m
        self.n = 0
    def hash(self,key):
        return (key%self.m)
    def display_table(self):
        for i in range(self.m):
            print("[",i,"] -->",end='')
            if self.array[i]!=None:
                self.array[i].display_list()
            else:
                print("__")
                  
    def search(self,key):
        h=self.hash(key)
        if self.array[h] != None:
            return self.array[h].search(key)
        return None
    def insert(self,newRecord):
        key=newRecord.get_student_id()
        h=self.hash(key)

        if self.array[h] == None:
            self.array[h] = singleLinkedList()
            self.array[h].insert in beginning(newRecord)
            self.n+=1

    def search(self,key):
        h=self.hash(key)
        if self.array[h] != None:
            return self.array[h].search(key)
        return None
    def delete(self,key):
        h=self.hash(key)
        if self.array[h] !=None:
            self.array[h].delete_node(key)
            self.n-=1
        else:
            print("value",key,"not present")

size = int(input("Enter size of table"))
table=HashTable(size)

while True:
    print("1.insert a record")
    print("2. search a record")
    print("3. delete a record")
    print("4.display a table")
    print("exit")

    choice = int(input("enter the choice"))
    if choice == 1:
        id=int(input("enter student id"))
        name=input("enter student name")
        aRecord =studentRecord(id,name)
        table.insert(aRecord)
    elif choice == 2:
        id=int(input("Enter a key to be searched"))
        aRecord = table.search(id)
        if aRecord is None:
            print("key is not found")
        else:
            print(aRecord)
    elif choice == 3:
        id=int(input("Enter a key to be deleted"))
        table.delete(id)
    elif choice == 4:
        table.display_table()
    elif choice == 5:
        break
    else:
        print("print wrong option")
    print()  
