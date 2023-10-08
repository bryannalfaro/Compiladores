.data
n1: .asciiz "Ingresa el primer numero: "
n2: .asciiz "Ingresa el segundo numero: "

.text
.globl main

main:
	#Se hace la llamada a sistema para printear string
	li $v0, 4     #printear un string
    la $a0, n1    #cargar el string a printear
    syscall      #llamada

    #se realiza la peticion al usuario
    li $v0, 5
    syscall
    move $t0, $v0

    #Se hace la llamada a sistema para printear string
	li $v0, 4     #printear un string
    la $a0, n2    #cargar el string a printear
    syscall      #llamada

    #se realiza la peticion al usuario
    li $v0, 5
    syscall
    move $t1, $v0

    jal gcd_function


    #Terminar
    li $v0, 10
    syscall

gcd_function:
	#Se hace la llamada a sistema para printear int
	li $v0, 1     #printear integer
    move $a0, $t0    #cargar el int
    syscall      #llamada

    jr $ra
