.data
const_0: .asciiz "Hello, World2.\n"
.text
.globl main
main:
        la $a0, const_0
        jal out_string
        jr $ra
li $v0, 10
syscall
out_string: li $v0, 4
        syscall
        jr $ra