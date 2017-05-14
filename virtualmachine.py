class VirtualMachineError(Exception):
    pass

class VirtualMachine(object):

    def __init__(self):
        self.frames = []
        self.frame = None
        self.return_value = None
        self.last_exception = None

    def run_code(self, code, global_names=None, local_names=None):
        frame = self.make_frame(code, global_names=global_names, local_names=local_names)
        self.run_frame(frame)

    def make_frame(self, code, callargs={}, global_names=None, local_names=None):
        if global_names is not None and local_names is not None:
            local_names = global_names
        elif self.frames:
            global_names = self.frame.global_names
        else:
            global_names = local_names = {
                '__builtins__': __builtins__,
                '__name__': '__main__',
                '__doc__': None,
                '__package__': None,
            }
        local_names.update(callargs)
        frame = Frame(code, global_names, local_names, self.frame)
        return frame

    def push_frame(self, frame):
        self.frames.append(frame)
        self.frame = frame

    def pop_frame(self):
        self.frames.pop()
        if self.frames:
            self.frame = self.frames[-1]
        else:
            self.frame = None

    def run_frame(self):
        pass

    def top(self):
        return self.frame.stack[-1]

    def pop(self):
        return self.frame.stack.pop()

    def push(self, *vals):
        self.frame.stack.extend(vals)

    def popn(self, n):
        if n:
            ret = self.frame.stack[-n:]
            self.frame.stack[-n:] = []
            return ret
        else:
            return []

    def parse_byte_and_args(self):
        f = self.frame
        opoffset = f.last_instruction
        bytecode = f.code_obj.co_code[opoffset]
        f.last_instruction += 1
        byte_name = dis.opname[bytecode]

        if bytecode >= dis.HAVE_ARGUMENT:
            arg = f.code_obj.co_code[f.last_instruction:f.last_instruction+2]
            f.last_instruction += 2
            arg_val = arg[0] + (arg[1] * 256)
            if bytecode in dis.hasconst:
                arg = f.code_obj.co_consts[arg_val]
            elif bytecode in dis.hasname:
                arg = f.code_obj.co_names[arg_val]
            elif bytecode in dis.haslocal:
                arg = f.code_obj.co_varnames[arg_val]
            elif bytecode in dis.hasjrel:
                arg = f.last_instruction + arg_val
            else:
                arg = arg_val

            argument = [arg]
        else:
            argument = []

        return byte_name, argument
