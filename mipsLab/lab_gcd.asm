.data
n1: .asciiz "Ingresa el primer numero: "
n2: .asciiz "Ingresa el segundo numero: "
result: .asciiz "Resultado : "

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

    #se pasan los parametros a la funcion
    move $a0, $t0
    move $a1, $t1

    #Se llama a funcion
    jal gcd_function

    
    #Se hace la llamada a sistema para printear string
	li $v0, 4     #printear un string
    la $a0, result    #cargar el string a printear
    syscall      #llamada

    #Mover el resultado
    move $a0, $v1
    li $v0, 1
    syscall

    #Terminar
    li $v0, 10
    syscall

gcd_function:
    #Espacio en stack
    addi $sp, $sp, -12
    sw $ra, 0($sp) 
    sw $s0, 4($sp)  
    sw $s1, 8($sp) 

    move $s0, $a0
    move $s1, $a1
   
   #si b=0 retornar
   beq $s1, $zero, return_gcd

   #b es primer parametro
   move $a0, $s1

   #make division
   div $s0, $s1
   mfhi $a1 # residuo de la division
   jal gcd_function


exit: 
    lw $ra, 0 ($sp)  # read registers from stack
    lw $s0, 4 ($sp)
    lw $s1, 8 ($sp)
    addi $sp,$sp , 12 # bring back stack pointer
    jr $ra

return_gcd:
    move $v1, $s0
    j exit
