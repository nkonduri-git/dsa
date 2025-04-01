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
#data in sorted is o(n)
#data in reverse sorted order o(n2)
#data in random order it is o(n2)
#search_linear search
def Search(a,n,searchValue):
    for i in range(n):
        if a[i]==searchValue:
            return i
        return -1
#####
n=int(input("Enter the number of elements"))
a=[None]*n
print('Enter the elemets')
for i in range(n):
    a[i]=int(input("Enter elements :"))
SearchValue = int(input("Enter the elements:"))
index=Search(a,n,searchvalue)
if index == -1:
    print("value",searchvalue,"not there in the list")
else:
    print("value",searchvalue,"present at index",index)
#best case we will get it as o(1)
#worst case we will get it as 0(n)
#avg case o(n)
#binary_search only in sorted array
#always search from middle elemet if the other element is bigger then go left if middle bigger than search  is small then go left 
def binary_search(a,n,searchValue):
    first=0
    last=n-1


    while first <= last:
        mid = (first+last)//2
        if searchValue<a[mid]:
            last = mid-1
        elif searchValue > a[mid];
              first =mid+1
        else:
            return mid
    return -1
###########
n=int(input("enter the number of eleemnts"))
a=[None]*n

print("enter the number of elements")
for i in range(n):
    a[i]=int(input("enter element"))
searchValue = int(input("enter the search value"))
index = binary_search(a,n,,searchValue)

if index == -1:
    print("value",searchValue,"not present in the array")
else:
    print("value",searchValue,"present at index",index)
###recursive

def binarysearch(a,n,searchvalue):

return _search(a,0,n-1,searchvalue)
def _search(a,first,last,searchValue):
    if(first > last ):
        return -1
    mid=(first+last)//2
    if searchValue > a[mid]:
        return _search(a,mid+1,last,searchValue)
    elif searchValue<a[mid]:
        return _search(a,first,mid-1,searchValue)
    else:
        return mid 
n=int(input("Enter the number of elements"))
a=[None]*n
print("enter the number of elements")
for i in range(n):
    a[i]=int(input("Enter element"))
searchValue = int(input("Enter the search value"))
index = binary_search(a,n,searchValue)
if index == -1:
    print("value",searchValue,"not present ")
else: 
    print("value",searchValue,"present at index",index)
# binary_search o(n/2)
#search until now number of elemets depends so to reduce time created a table
#where record associated with the index so created a address table where records stored in the adddress
