class Node:

    def __init__(self,value):
        self.info=value
        self.link=None
class SingleLinkedList:  #to find the link or the address of the node use p.link and p.link.link to get the previous node of the current node you are there 

     def __init__(self):
         self.start=None
      def display():
         pass
     def display_list(self):
         if self.start is None:
             print("it is empty")
             return
         else:
             print("list is ")
             p=self.start
             while p is not None:
                 print(p.info,"",end="")
                 p=p.link
              print()
             
      def count_nodes(self):
         p=self.start
         n=0
         while p is not None:
             n+=1
             p=p.link
         print("Number of nodes in the link ",n)
      def search(self,x):
         position=1
         p=self.start
         while p is not None:
             if p.info == x:
                 print(x,"in position",position)
                 return True
             position+=1
             p=p.link
            else:
             print("link not forund in the list")
             return False
        def insert_before (self,data,x):
            if self.start is None:
                print("list is none")
                 return
            if x == self.start.info:
                 temp= Node(data)
                 temp.link = self.start
                 self.start= temp
                return
                
            p=self.start
            while p.link is not None:
                if p.link.info == x:
                    break 
                p=p.link
            if p.link is None:
                print(x,"not present in the list")
            else:
                temp=Node(data)
                temp.link=p.link
                p.link = temp
        def insert_at_position(self,data,k):
            if k == 1:
                temp=Node(data)
                temp.link=self.start
                self.start=temp
                return
            p = self.start
            i=1
            while i<k-1 and p is not None:
                p=p.link
                i+=1
            if p is  None:
                print("you can insert only upto position",i)
            else:
                temp=Node(data)
                temp.link=p.link
                p.link=temp
        def delete_node(self,x):
            if self.start.info == x:
                self.start = self.start.link
                return
            #deletion in between
            p=self.start
            while p.link is not None:
                if p.link.info == x:
                    break
                p=p.link
            if p.link is None:
                print("element ",x,"not in the list ")
            else:
                p.link=p.link.link
        def delete_first_node(self):
            if self.start is None:
                return 
                self.start=self.start.link
        def deletion_last_node(self):
            if self.start is None:
                return
            if self.start.link is None:


list=SingleLinkedList()
list.create_list()
while True:
    print("1.Disply list")
    print("2.count the number of nodes")
    print("3.search for an element")
    print("4.insert in empty ")
    print("Insert at the end of the list ")
    print("Insert at the after  a specified node ")
    print("Insert at the before a specified ")
    print("Insert at the given position ")
    print("delete the first node")
    print("delete the last node")
    print("delete any node")
    print("reverse the list")
    print("bubble sort")
    print("bubble sort by exchanging the links")
    print("merge sort")
    print("insert cycle")
    print("detetct cycle")
    print("remove the cycle")
    print("quit")

    option= int(input("enter your choice "))

    if option == 1:
        list.display_list()
    elif option == 2:
        list.count_nodes()
    elif option== 3 :
        data = int(input("enter the number to be searched"))
        list.search(data)
        
    
         
         