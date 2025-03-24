#we will do sorting
#stable sort will retain the relative position of the duplicate values and unstable will not retian the relative position of the duplicate values 
#SELECTION SORT select the smallest and sort 
def selection_sort(a):
    for i in range(len(a)-1):
        minIndex=i
        for j in range(i+1,len(a)):
            if(a[j]<a[minIndex]):
                minIndex = j
        if i!=minIndex:
            a[i],a[minIndex]=a[minIndex],a[i]

list1=[6,3,1,5,9,0]
selection_sort(list1)
print(list1)

list2=[3,45,5,6,6,7,9]
selection_sort(list2)
print(list2)
#selection sort is unstable and the time complexity o(n2)
#bubble sort
def bubble_sort(a):
    for x in range(len(a)-1,0,-1):
        for j in range(x):
            if a[j]>a[j+1]:
                if(a[j]>a[j+1]):
                    a[j],a[j+1]=a[j+1],a[j]
            
list1=[6,3,1,5,9,8]
bubble_sort(list1)
print(list1)

list2=[9,8,2,3,4,5]
bubble_sort(list2)
print(list2)
## the above code can be betterd by 
def bubble_sort(a):
    for x in range(len(a)-1,0,-1):
        swap=0
        for j in range(x):
            if a[j]>a[j+1]:
                a[j],a[j+1]=a[j+1],a[j]
                 swaps+=1
        if swap == 0:
            break
#already sorted no swaps required so time complexity o(n )as it reuquired to check once overall
#rev sorted o(n2)
#insertion_sort
def insertion_sort(a):
    for i in range(1,len(a)):
        temp=a[i]
        j=i-1
        while j>=0 and a[j]>temp:
            a[j+1]=a[j]
            j=j-1
            a[j+1]=temp

list1=[6,3,1,5,9,8]
insertion_sort(list1)
print(list1)
