class CPU:
    def __init__(self, memory_size=1024):
        self.memory = ['0' * 16] * memory_size  # Memory array with 16-bit binary strings
        self.registers = {
            "ACC": '0' * 16,  # Accumulator
            "PC": '0' * 16,   # Program Counter
            "MAR": '0' * 16,  # Memory Address Register
            "MDR": '0' * 16,  # Memory Data Register
            "IR": '0' * 16    # Instruction Register
        }

        # Instruction set with corresponding methods
        self.instruction_set = {
            '00000000' : self.HLT,  # HLT - Stops the program
            '00000001' : self.ADD,  # ADD - Adds the value at the memory address to the ACC
            '00000010' : self.LDA,  # LDA - Loads the value at the memory address to the ACC
            '00000011' : self.BRA,  # BRA - Always Branches to a given memory address.
            '00000100' : self.BRZ,  # BRZ - branch to a given memory location if acc == 0
            '00000101' : self.BRP,  # BRP - branches to a given memory location if acc > 0
            '00000110' : self.STA,  # STA - Stores the contents of the ACC into a location in memory
            '00000111' : self.SUB,  # SUB - Subtracts the value given from the operand address from the ACC
            '11111111' : self.OUT   # OUT - Outputs the value in the ACC as a denery number
        }

        self.running = True  # Flag for the Fetch-Decode-Execute cycle

    def load_program(self, program):
        # Loads machine code instructions and data into memory as 16-bit binary strings
        for i, instruction in enumerate(program):
            self.memory[i] = instruction.zfill(16)

    # Fetch-Decode-Execute Cycle
    def fetch(self):
        self.registers["MAR"] = self.registers["PC"]  # Set MAR to the current PC
        self.registers["MDR"] = self.memory[int(self.registers["MAR"], 2)]  # Fetch instruction from memory
        self.registers["IR"] = self.registers["MDR"]  # Load the fetched instruction into IR
        # Increment PC by 1 (in binary)
        self.registers["PC"] = bin(int(self.registers["PC"], 2) + 1)[2:].zfill(16)[-16:]

    def decode(self):
        # Decode the instruction stored in IR
        instruction = self.registers["IR"]
        opcode = instruction[:8]   # First 8 bits are the opcode
        operand = instruction[8:]  # Last 8 bits are the operand
        return opcode, operand

    def execute(self, opcode, operand):
        # Execute the instruction corresponding to the opcode
        if opcode in self.instruction_set:
            self.instruction_set[opcode](operand)
        else:
            print("Unknown opcode:", opcode)
            self.running = False

    # Instructions
    # For instructions where no operand is needed,
    # this must still be passed through to ensure the executer dosent throw an error when it is missing

    def ADD(self, operand):
        self.registers["MAR"] = operand  # Set MAR to the address specified by the operand
        self.registers["MDR"] = self.memory[int(self.registers["MAR"], 2)]  # Fetch value from memory
        acc_value = int(self.registers["ACC"], 2)  # Convert ACC to an integer
        mdr_value = int(self.registers["MDR"], 2)  # Convert MDR to an integer

        # Add the values and handle 16-bit overflow
        result = (acc_value + mdr_value) & 0xFFFF  # Keep only the lower 16 bits

        # Update the ACC with the new value as a binary string
        self.registers["ACC"] = self.to_bin(result)

        print(f"ADD executed: ACC = {self.registers['ACC']}")

    def SUB(self, operand):
        self.registers["MAR"] = operand
        self.registers["MDR"] = self.memory[int(self.registers["MAR"], 2)]
        acc_value = int(self.registers["ACC"], 2)
        mdr_value = int(self.registers["MDR"], 2)

        result = acc_value - mdr_value
        print(f"SUB result: {result}, type: {type(result)}")

        self.registers["ACC"] = self.to_bin(result)
        print(f"SUB executed: ACC = {self.registers["ACC"]}")

    def LDA(self, operand):
        self.registers["MAR"] = operand  # Set MAR to the address specified by the operand
        self.registers["MDR"] = self.memory[int(self.registers["MAR"], 2)]  # Fetch value from memory
        self.registers["ACC"] = self.registers["MDR"]  # Load MDR into ACC
        print(f"LDA executed: ACC = {self.twos_complement(self.registers['ACC'])} (signed)")

    def STA(self, operand):
        self.memory[int(operand, 2)] = self.registers["ACC"]
        print(f"STA executed: Memory[{operand}] = {self.twos_complement(self.registers['ACC'])}")

    def BRA(self, operand):
        self.registers["PC"] = operand # This should just work.
        print("BRA executed: PC =", str(self.registers["PC"]))
        
    def BRP(self, operand):
        if self.twos_complement(self.registers["ACC"]) >= 0:  # Check if ACC is positive or zero
            self.registers["PC"] = operand
            print(f"BRP executed: PC = {self.registers['PC']}")

    def BRZ(self, operand):
        if self.twos_complement(self.registers["ACC"]) == 0:  # Check if ACC is zero
            self.registers["PC"] = operand
            print(f"BRZ executed: PC = {self.registers['PC']}")

    def HLT(self, operand):
        # Halt the CPU
        print("HLT executed")
        self.running = False

    def OUT(self, operand):
        print(f"OUT executed: {self.twos_complement(self.registers['ACC'])}")


# Conversion Functions 
# as much as I dont want to be using python logic there is no way around 2's compliment 
# where we can stay in binary

    def twos_complement(self, binary_str, bit_width=16):

        if not isinstance(binary_str, str):
            binary_str = str(binary_str)  # Convert to string if not already
        value = int(binary_str, 2)  # Interpret as unsigned binary
        if value >= (1 << (bit_width - 1)):  # If MSB is 1 (negative number)
            value -= (1 << bit_width)  # Subtract 2^bit_width to get the negative value
        
        return value


    def to_bin(self, value, bits=16):
        if not isinstance(value, int):  # Ensure value is an integer
            raise TypeError(f"Expected int, got {type(value).__name__}")
        if value < 0:  # Handle negative numbers
            value = (1 << bits) + value  # Apply two's complement
        return bin(value & ((1 << bits) - 1))[2:].zfill(bits)  # Ensure proper bit-width


    def run(self):
        # Main loop for the Fetch-Decode-Execute cycle
        while self.running:
            self.fetch()  # Fetch the next instruction
            opcode, operand = self.decode()  # Decode the instruction
            self.execute(opcode, operand)
