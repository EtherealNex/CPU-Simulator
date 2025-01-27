class assembler:
    def __init__(self, file_path = None, debug = True):
        self.file_path = file_path
        self.debug = debug
        self.instruction_set = {
            'HLT' : ('00000000', False),  # HLT - Stops the program - False, no operand
            'ADD': ('00000001', True),  # ADD - Adds the value at the memory address to the ACC - True Requires operand
            'LDA': ('00000010', True),  # LDA - Loads the value at the memory address to the ACC - True Requires Operand Added
            'BRA' : ('00000011', True), # BRA - Always branch to a section in memory - True, requires an operand
            'BRZ': ('00000100', True),   # BRZ - branch to a given memory location if acc == 0 - True, requires an operand
            'BRP': ('00000101', True),   # BRP - branches to a given memory location if acc > 0 - True, requires an operand
            'STA' : ('00000110', True),  # STA - Stores the contents of the ACC into a location in memory - True, requires an operand
            'SUB' : ('00000111', True), # SUB - Subtracts the value in ACC from the value given from the operand mem address - True, requires an operand
            'OUT' : ('11111111', False),  # OUT - Outputs the value in the ACC as a denery number - False, no operand
            'DAT' : None # Special Case: handled as data
        }

        self.machine_code = []

    def load_assembaly(self):
        with open (self.file_path, 'r') as file:
            lines = file.readlines()
            return [line.strip() for line in lines if line.strip() and not line.startswith('//')]
    
    def preprocessing(self):
        asm_code = self.load_assembaly()
        processed_lines = []
        for line in asm_code:
            line = line.split("//")[0].strip()
            if line:
                processed_lines.append(line)
        return processed_lines

    def first_pass(self):
        asm_code = self.preprocessing()
        data_address = 0
        var_table = {}
        label_table = {}

        for index, token in enumerate(asm_code):
            tokens = token.split()

            if len(tokens) >= 2 and tokens[1] in self.instruction_set and tokens[1] != "DAT":
                label_name = tokens[0]
                if label_name in label_table:
                    raise ValueError(f"ERROR: Label used - {label_name}")
                label_table[label_name] = data_address
                asm_code[index] = ' '.join(tokens[1:])
                tokens = tokens[1:]

            elif len(tokens) >= 2 and tokens[1] == "DAT":
                var_name = tokens[0]
                if var_name in var_table:
                    raise ValueError(f"ERROR: Variable exists - {var_name}")
                var_table[var_name] = data_address

                if len(tokens) == 2:
                    asm_code[index] = (asm_code[index] + ' 0')
            
            elif len(tokens) == 2 and tokens[0] == "DAT":
                raise ValueError("Undefined Variable at address:", str(data_address))

            data_address += 1

            if self.debug:
                print("Tokens:", tokens)

        if self.debug:
            print("Variable Table:", var_table)
            print("Label Table:", label_table)
            print("Assembly Code:", asm_code)

        return label_table, var_table, asm_code

    def second_pass(self):
        label_table, var_table, asm_code = self.first_pass()
        self.machine_code = []

        for token in asm_code:
            tokens = token.split()

            if len(tokens) == 3 and tokens[1] == "DAT":
                var_value = int(tokens[2])
                var_bin = f'{var_value:016b}'
                self.machine_code.append(var_bin)
            else:
                instruction = tokens[0]
                operand = tokens[1] if len(tokens) > 1 else None

                if instruction not in self.instruction_set:
                    raise ValueError(f"ERROR: Unknown instruction {instruction}")

                opcode, needs_operand = self.instruction_set[instruction]

                if needs_operand:
                    if operand in label_table:
                        operand_address = label_table[operand]
                    elif operand in var_table:
                        operand_address = var_table[operand]
                    else:
                        try:
                            operand = int(operand)
                            operand_address = operand
                        except Exception as e:
                            print(e)
                            raise ValueError("ERROR - String Variable Detected and undefinded -", str(operand))


                    operand_bin = f'{operand_address:08b}'
                else:
                    operand_bin = '00000000'

                self.machine_code.append(opcode + operand_bin)

        if self.debug:
            print("Machine Code:", self.machine_code)

    def assemble(self):
        self.second_pass()
        return self.machine_code