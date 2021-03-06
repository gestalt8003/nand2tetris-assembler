# parser.py
from exceptions import InvalidAddressError
from symboltable import SymbolTable

A_COMMAND = 0
C_COMMAND = 2
L_COMMAND = 4


class Parser:
    """Encapsulates access to the input code. 
       Reads an assembly language com-mand, parses it, and 
    provides convenient access to the command’s 
    components(fields and symbols). 
       In addition, removes all white space and comments."""

    def __init__(self, path):
        """Opens the file at file_path and gets ready to parse it."""
        
        # File
        self.path = path
        self.file = open(self.path)
        # File reading
        self.lines = self.file.readlines()
        self.index = -1 # Line when reading the file
        self.line_index = 0 # Line index, not including empty spaces
        self.line = None
        # Symbol table
        self.symbol_table = SymbolTable()
        
        print("Opened file:", self.path)
        print("Fetching L commands")
        self.fetch_l_commands()

    def __str__(self):
        return self.line

    def __len__(self):
        return len(self.line)

    def has_more_commands(self):
        return self.index + 1 < len(self.lines)

    def advance(self):
        """Reads the next command from the input and makes it the current command.
        Should be called only when has_more_commands is True. Initially there is no current command."""
        
        self.line = self.get_next_line()
        while len(self.line) == 0: # Skip empty lines
            self.line = self.get_next_line()
        
        if self.command_type() != L_COMMAND:
            self.line_index += 1

        return self.line

    def get_next_line(self):
        """Advances the reader. Cleans the line but does not ignore empty lines."""
        self.index += 1
        dirty_line = self.lines[self.index]
        return dirty_line.split("//")[0].strip() # Remove whitespace and comments

    def fetch_l_commands(self):
        i = 0
        for line in self.lines:
            clean_line = line.split("//")[0].strip()
            if len(clean_line) != 0:
                if clean_line[0] == "(" and clean_line[-1] == ")":
                    addy_only = clean_line[1:-1]
                    if not addy_only.isdigit():
                        self.symbol_table.add_entry(addy_only, i)
                else:
                    i += 1   
    
    def command_type(self):
        """Returns the type of the current command.
        A_COMMAND: @Xxx where Xxx is either a symbol or decimal number.
        C_COMMAND: for dest=comp;jump
        L_COMMAND: (Xxx) where Xxx is a symbol"""
        if self.line[0] == "@":
            return A_COMMAND
        elif self.line[0] == "(" and self.line[-1] == ")":
            return L_COMMAND
        else:
            return C_COMMAND

    def symbol(self):
        """Returns the symbol or decimal Xxx of the current command @Xxx or (Xxx).
        Should be called only when command_type is A_COMMAND or L_COMMAND"""
        # Check if symbol
        address_dec = 0
        c_type = self.command_type()
        addy_only = ""
        if c_type == L_COMMAND:
            addy_only = self.line[1:-1]
        else: # A_COMMAND
            addy_only = self.line[1:]
        
        if addy_only.isdigit():
            address_dec = int(addy_only)
        else:
            print(addy_only)
            if self.symbol_table.contains(addy_only):
                address_dec = self.symbol_table.get_address(addy_only)
            else:
                if c_type == L_COMMAND:
                    address_dec = self.symbol_table.add_entry(addy_only, self.line_index)
                else:
                    address_dec = self.symbol_table.add_entry(addy_only)

        if address_dec > 2 ** 15: # max 15-bit integer (32767)
            raise InvalidAddressError("Address " + str(address_dec) + " exceeds the maximum capacity.")
        if address_dec < 0: # Address cannot be negative
            raise InvalidAddressError("Address cannot be negative.")
        return format(address_dec, "015b") # Returns binary conversion of address_dec w/o 0b at the beginning

    def dest(self):
        """Returns the dest mnemonic. Should be called only when command_type is C_COMMAND"""
        
        if "=" in self.line:
            return self.line.split("=")[0]
        return None

    def comp(self):
        """Returns the comp mnemonic. Should be called only when command_type is C_COMMAND"""
        
        comp = self.line
        temp = comp.split("=")
        if len(temp) > 1:
            comp = temp[1]
        temp = comp.split(";")
        if len(temp) > 0:
            comp = temp[0]
        return comp

    def jump(self):
        """Returns the jump mnemonic. Should be called only when command_type is C_COMMAND"""
        
        if ";" in self.line: # dest, jump
            return self.line.split(";")[1]
        return None

    def __del__(self):
        print(self.line_index, "lines translated.")
        self.file.close()
        print("Closing file:", self.path)



# class Line:
#     """Is returned when reading from a Parser object. 
#     Contains functions related to a line."""

#     def __init__(self, line):
#         self.line = line
#         self.length = len(line)

    