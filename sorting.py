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