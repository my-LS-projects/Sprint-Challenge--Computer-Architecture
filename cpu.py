"""CPU functionality."""

import sys

### OP CODES ###
LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
RET = 0b00010001
CALL = 0b01010000
JEQ = 0b01010101
CMP = 0b10100111
JMP = 0b01010100
JNE = 0b01010110

SP = 7  # stack pointer set to R7


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # 8 general-purpose registers
        self.reg = [0] * 8
        # 256 bytes of memory
        self.ram = [0] * 256
        # program counter
        self.pc = 0
        self.flag = {}

    def load(self, file):
        """Load a program into memory."""
        try:
            address = 0

            with open(file) as f:
                for line in f:
                    # strip out white space, split at inline comment
                    cleaned_line = line.strip().split("#")
                    # grab number
                    value = cleaned_line[0].strip()

                    # check if blank or not, if blank skip to next line
                    if value != "":
                        # convert from binary to num
                        num = int(value, 2)
                        self.ram[address] = num
                        address += 1

                    else:
                        continue

        except FileNotFoundError:
            # exit and give error
            print("ERROR: File not found")
            sys.exit(1)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc

        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]

        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]

        elif op == "CMP":
            """
            * `L` Less-than: during a `CMP`, set to 1 if registerA is less than registerB,
            zero otherwise.
            * `G` Greater-than: during a `CMP`, set to 1 if registerA is greater than
            registerB, zero otherwise.
            * `E` Equal: during a `CMP`, set to 1 if registerA is equal to registerB, zero
            otherwise.
            """
            if self.reg[reg_a] < self.reg[reg_b]:
                self.flag["L"] = 1
            else:
                self.flag["L"] = 0

            if self.reg[reg_a] > self.reg[reg_b]:
                self.flag["G"] = 1
            else:
                self.flag["G"] = 0

            if self.reg[reg_a] == self.reg[reg_b]:
                self.flag["E"] = 1
            else:
                self.flag["E"] = 0

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(
            f"TRACE: %02X | %02X %02X %02X |"
            % (
                self.pc,
                # self.fl,
                # self.ie,
                self.ram_read(self.pc),
                self.ram_read(self.pc + 1),
                self.ram_read(self.pc + 2),
            ),
            end="",
        )

        for i in range(8):
            print(" %02X" % self.reg[i], end="")

        print()

    def ram_read(self, mar):
        """
        should accept the address to read and 
        return the value stored there.

        MAR = Memory Address Register
        MAR contains the address that is being read or written to.
        """
        return self.ram[mar]

    def ram_write(self, mdr, mar):
        """
        should accept a value to write, and 
        the address to write it to.

        MDR = Memory Data Register
        MAR = Memory Address Register

        MAR contains the address that is being read or written to. The MDR contains
        the data that was read or the data to write.
        """
        self.ram[mar] = mdr

    def run(self):
        """Run the CPU."""
        while True:
            op = self.ram_read(self.pc)
            if op == LDI:
                # Set the value of a register to an integer.
                index = self.ram[self.pc + 1]
                value = self.ram[self.pc + 2]
                self.reg[index] = value
                self.pc += 3

            elif op == PRN:
                # Print numeric value stored in the given register.
                index = self.ram[self.pc + 1]
                print(self.reg[index])
                self.pc += 2

            elif op == MUL:
                reg_a = self.ram_read(self.pc + 1)
                reg_b = self.ram_read(self.pc + 2)
                self.alu("MUL", reg_a, reg_b)
                self.pc += 3

            elif op == POP:
                """
                Copy the value from the address pointed to by `SP`
                to the given register.
                
                Increment `SP`.
                """
                # get the value out of memory
                stack_val = self.ram_read(self.reg[SP])
                # get the register number from the instruction in memory
                reg_num = self.ram_read(self.pc + 1)
                # write the value of register to the value held in the stack
                self.reg[reg_num] = stack_val
                # increment the SP
                self.reg[SP] += 1
                self.pc += 2

            elif op == PUSH:
                """
                Copy the value from the address pointed to by `SP`
                to the given register.
                
                Increment `SP`.
                """
                # decrement
                self.reg[SP] -= 1
                # get the value out of memory
                stack_addr = self.reg[SP]
                # get the register number from the instruction in memory
                reg_num = self.ram_read(self.pc + 1)
                # get the value out of the regsiter
                val = self.reg[reg_num]
                # write the reg value to a position in the stack
                self.ram_write(stack_addr, val)
                self.pc += 2

            elif op == CALL:
                """
                Calls a subroutine (function) at the address stored in the register.
                """
                # decrement SP
                self.reg[SP] -= 1
                # get the current memory addres that SP points to
                stack_addr = self.reg[SP]
                # get the return memory address
                return_addr = self.pc + 2
                # push the return addr onto the stack
                self.ram_write(stack_addr, return_addr)
                # set PC to the value in the register
                reg_num = self.ram_read(self.pc + 1)
                self.pc = self.reg[reg_num]

            elif op == RET:
                """
                Return from subroutine.
                Pop the value from the top of the stack and store it in the `PC`.
                """
                self.pc = self.ram_read(self.reg[SP])
                self.reg[SP] += 1

            elif op == CMP:
                reg_a = self.ram_read(self.pc + 1)
                reg_b = self.ram_read(self.pc + 2)
                self.alu("CMP", reg_a, reg_b)
                self.pc += 3

            elif op == JMP:
                """
                Jump to the address stored in the given register.
                Set the `PC` to the address stored in the given register.
                """
                reg_a = self.ram_read(self.pc + 1)
                self.pc = self.reg[reg_a]

            elif op == JNE:
                '''
                If `E` flag is clear (false, 0), jump to the 
                address stored in the given register.
                '''
                reg_a = self.ram_read(self.pc + 1)
                if self.flag["E"] == 0:
                    self.pc = self.reg[reg_a]
                else:
                    self.pc += 2

            elif op == JEQ:
                '''
                If `equal` flag is set (true), jump to the 
                address stored in the given register.
                '''
                reg_a = self.ram_read(self.pc + 1)
                if self.flag["E"] == 1:
                    self.pc = self.reg[reg_a]
                else:
                    self.pc += 2

            elif op == HLT:
                # hHalt the CPU (and exit the emulator).
                print("Exiting...")
                sys.exit(0)

            else:
                print("ERROR: Unknown command")
                sys.exit(1)
