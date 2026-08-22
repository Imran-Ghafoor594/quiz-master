num=int(input("Enter the number which you want ot check ->"))
for i in range (num):
    input("press <Enter> to continue..")
    if i <=2:
        print(f"{i} it is prime number")
    if i % 3 ==0:
        print(f'{i} it is prime number')
        
    else:
         print(f'{i} it is not number')
         


