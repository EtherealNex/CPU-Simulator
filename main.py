from processing.cpu import CPU
from translators.assembler import assembler

# Program in machine code (16-bit binary strings)
MyFirstProgram = [
    '0000001000000100',  # LDA 4: Load the number in memory address 4 into ACC
    '0000000100000101',  # ADD 5: Add the number stored in memory address 5 to ACC
    '1111111100000000',  # OUT: Outputs the contets of the ACC as a denery number
    '0000000000000000',  # HLT: Stop the program
    '0000000000000001',  # Memory address 4: Value 1
    '0000000000000001'   # Memory address 5: Value 1
]

cpu = CPU()
asm = assembler("programs/powerOf2.txt", False)
cpu.load_program(asm.assemble())  # Load the program into memory
cpu.run()

# Output the final state of registers
print(f"Final Registers: ACC = {cpu.registers['ACC']}, PC = {cpu.registers['PC']}")