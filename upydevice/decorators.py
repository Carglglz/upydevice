
from dill.source import getsource
import functools


def uparser_dec(long_command, pastemode=False, end=''):
    lines_cmd = []
    space_count = [0]
    buffer_line = ''
    previous_incomplete = False
    for line in long_command.split('\n')[1:]:
        line_before = space_count[-1]
        if line != '':
            if not previous_incomplete:
                line_now = line.count('    ')
                # print(line_now)
        # print(line_now)
            space_count.append(line_now)
            if line_before > line_now:
                if line_now > 0:
                    lines_cmd.append(
                        ''.join(['\b' for i in range(int("{:.0f}".format((line_before-line_now))))]+[line.strip()]))
                    # print('This line must be backspaced {:.0f} times: {}'.format(((line_before-line_now)), line.strip()))
                # else:
                #     if len(line.strip()) > 0:
                #         lines_cmd.append(''.join(['\b' for i in range(1)]+[line.strip()]))

            elif line[-1] == ',':
                # print('line incomplete')
                previous_incomplete = True
                buffer_line += line.strip()
            else:
                if buffer_line != '':
                    if previous_incomplete:
                        # print('This is the complete line:{}'.format(buffer_line+line.strip()))
                        lines_cmd.append('\r'.join([buffer_line+line.strip()]))
                        buffer_line = ''
                        previous_incomplete = False
                else:
                    lines_cmd.append('\r'.join([line.strip()]))
    if not pastemode:
        return "{}{}{}".format('\r'.join(lines_cmd), '\r'*line_now, end)
    else:
        return "\x05{}\x04".format(long_command)


def upy_code(func):  # TODO: ACCEPT DEVICE ARG
    def wrapper_get_str_func(*args, **kwargs):
        print(getsource(func))
        return uparser_dec(getsource(func))
    return wrapper_get_str_func


# PYTHON PHANTOM DECORATORS

def upy_cmd(device, debug=False, rtn=True):
    def decorator_cmd_str(func):
        @functools.wraps(func)
        def wrapper_cmd(*args, **kwargs):
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" if not callable(
                v) else f"{k}={v.__name__}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            cmd = f"{func.__name__}({signature})"
            device.output = None
            if debug:
                device.cmd(cmd)
            else:
                device.cmd(cmd, silent=True)
            if rtn:
                return device.output
            else:
                return None
        return wrapper_cmd
    return decorator_cmd_str


def upy_cmd_c(device, debug=False, rtn=True, out=False):
    def decorator_cmd_str(func):
        @functools.wraps(func)
        def wrapper_cmd(*args, **kwargs):
            flags = ['>', '<', 'object', 'at', '0x']
            args_repr = [repr(a) for a in args if any(
                f not in repr(a) for f in flags)]
            kwargs_repr = [f"{k}={v!r}" if not callable(
                v) else f"{k}={v.__name__}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            cmd_ = f"{func.__name__}({signature})"
            name = func(*args, **kwargs)
            cmd = "{}.{}".format(name, cmd_)
            device.output = None
            if out:
                cmd = "{}".format(cmd_)
            else:
                pass
            if debug:
                device.cmd(cmd)
            else:
                device.cmd(cmd, silent=True)
            if rtn:
                return device.output
            else:
                return None
        return wrapper_cmd
    return decorator_cmd_str


def upy_cmd_c_raw(device, out=False):
    def decorator_cmd_str(func):
        @functools.wraps(func)
        def wrapper_cmd(*args, **kwargs):
            flags = ['>', '<', 'object', 'at', '0x']
            args_repr = [repr(a) for a in args if any(
                f not in repr(a) for f in flags)]
            kwargs_repr = [f"{k}={v!r}" if not callable(
                v) else f"{k}={v.__name__}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            cmd_ = f"{func.__name__}({signature})"
            name = func(*args, **kwargs)
            cmd = "{}.{}".format(name, cmd_)
            device.output = None
            if out:
                cmd = "{}".format(cmd_)
            else:
                pass
            device.cmd(cmd, capture_output=True)
            try:
                device.output = device.long_output[0].strip()
            except Exception as e:
                print(e)
                pass
            return None
        return wrapper_cmd
    return decorator_cmd_str


def upy_cmd_c_r(debug=False, rtn=True, out=False):
    def decorator_cmd_str(func):
        @functools.wraps(func)
        def wrapper_cmd(*args, **kwargs):
            flags = ['>', '<', 'object', 'at', '0x']
            args_repr = [repr(a) for a in args if any(
                f not in repr(a) for f in flags)]
            kwargs_repr = [f"{k}={v!r}" if not callable(
                v) else f"{k}={v.__name__}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            cmd_ = f"{func.__name__}({signature})"
            dev_dict = func(*args, **kwargs)
            cmd = "{}.{}".format(dev_dict['name'], cmd_)
            dev_dict['dev'].output = None
            if out:
                cmd = "{}".format(cmd_)
            else:
                pass
            if debug:
                dev_dict['dev'].cmd(cmd)
            else:
                dev_dict['dev'].cmd(cmd, silent=True)
            if rtn:
                return dev_dict['dev'].output
            else:
                return None
        return wrapper_cmd
    return decorator_cmd_str


def upy_cmd_c_raw_r(out=False):
    def decorator_cmd_str(func):
        @functools.wraps(func)
        def wrapper_cmd(*args, **kwargs):
            flags = ['>', '<', 'object', 'at', '0x']
            args_repr = [repr(a) for a in args if any(
                f not in repr(a) for f in flags)]
            kwargs_repr = [f"{k}={v!r}" if not callable(
                v) else f"{k}={v.__name__}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            cmd_ = f"{func.__name__}({signature})"
            dev_dict = func(*args, **kwargs)
            cmd = "{}.{}".format(dev_dict['name'], cmd_)
            dev_dict['dev'].output = None
            if out:
                cmd = "{}".format(cmd_)
            else:
                pass
            dev_dict['dev'].cmd(cmd, capture_output=True)
            try:
                dev_dict['dev'].output = dev_dict['dev'].long_output[0].strip()
            except Exception as e:
                print(e)
                pass
            return None
        return wrapper_cmd
    return decorator_cmd_str


def upy_cmd_c_r_in_callback(debug=False, rtn=True, out=False):
    def decorator_cmd_str(func):
        @functools.wraps(func)
        def wrapper_cmd(*args, **kwargs):
            flags = ['>', '<', 'object', 'at', '0x']
            args_repr = [repr(a) for a in args if any(
                f not in repr(a) for f in flags)]
            dev_dict = func(*args, **kwargs)
            name = dev_dict['name']
            kwargs_repr = [f"{k}={v!r}" if not callable(
                v) else f"{k}={name}.{v.__name__}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            cmd_ = f"{func.__name__}({signature})"
            cmd = "{}.{}".format(dev_dict['name'], cmd_)
            dev_dict['dev'].output = None
            if out:
                cmd = "{}".format(cmd_)
            else:
                pass
            if debug:
                dev_dict['dev'].cmd(cmd)
            else:
                dev_dict['dev'].cmd(cmd, silent=True)
            if rtn:
                return dev_dict['dev'].output
            else:
                return None
        return wrapper_cmd
    return decorator_cmd_str


def upy_cmd_c_r_nb(debug=False, rtn=True, out=False):
    def decorator_cmd_str(func):
        @functools.wraps(func)
        def wrapper_cmd(*args, **kwargs):
            flags = ['>', '<', 'object', 'at', '0x']
            args_repr = [repr(a) for a in args if any(
                f not in repr(a) for f in flags)]
            kwargs_repr = [f"{k}={v!r}" if not callable(
                v) else f"{k}={v.__name__}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            cmd_ = f"{func.__name__}({signature})"
            dev_dict = func(*args, **kwargs)
            cmd = "{}.{}".format(dev_dict['name'], cmd_)
            dev_dict['dev'].output = None
            if out:
                cmd = "{}".format(cmd_)
            else:
                pass
            if debug:
                dev_dict['dev'].cmd_nb(cmd, long_string=True)
            else:
                dev_dict['dev'].cmd_nb(cmd, silent=True,)
            if rtn:
                dev_dict['dev'].get_opt()
                return dev_dict['dev'].output
            else:
                return None
        return wrapper_cmd
    return decorator_cmd_str


def upy_cmd_c_r_nb_in_callback(debug=False, rtn=True, out=False):
    def decorator_cmd_str(func):
        @functools.wraps(func)
        def wrapper_cmd(*args, **kwargs):
            flags = ['>', '<', 'object', 'at', '0x']
            args_repr = [repr(a) for a in args if any(
                f not in repr(a) for f in flags)]
            dev_dict = func(*args, **kwargs)
            name = dev_dict['name']
            kwargs_repr = [f"{k}={v!r}" if not callable(
                v) else f"{k}={name}.{v.__name__}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            cmd_ = f"{func.__name__}({signature})"
            cmd = "{}.{}".format(dev_dict['name'], cmd_)
            dev_dict['dev'].output = None
            if out:
                cmd = "{}".format(cmd_)
            else:
                pass
            if debug:
                dev_dict['dev'].cmd_nb(cmd)
            else:
                dev_dict['dev'].cmd_nb(cmd, silent=True)
            if rtn:
                dev_dict['dev'].get_opt()
                return dev_dict['dev'].output
            else:
                return None
        return wrapper_cmd
    return decorator_cmd_str


def upy_wrcmd_c_r(debug=False, rtn=True, out=False):
    def decorator_cmd_str(func):
        @functools.wraps(func)
        def wrapper_cmd(*args, **kwargs):
            flags = ['>', '<', 'object', 'at', '0x']
            args_repr = [repr(a) for a in args if any(
                f not in repr(a) for f in flags)]
            kwargs_repr = [f"{k}={v!r}" if not callable(
                v) else f"{k}={v.__name__}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            cmd_ = f"{func.__name__}({signature})"
            dev_dict = func(*args, **kwargs)
            cmd = "{}.{}".format(dev_dict['name'], cmd_)
            dev_dict['dev'].output = None
            if out:
                cmd = "{}".format(cmd_)
            else:
                pass
            if debug:
                dev_dict['dev'].wr_cmd(cmd)
            else:
                dev_dict['dev'].wr_cmd(cmd, silent=True)
            if rtn:
                return dev_dict['dev'].output
            else:
                return None
        return wrapper_cmd
    return decorator_cmd_str


# def upy_wrcmd_c_raw_r(out=False):
#     def decorator_cmd_str(func):
#         @functools.wraps(func)
#         def wrapper_cmd(*args, **kwargs):
#             flags = ['>', '<', 'object', 'at', '0x']
#             args_repr = [repr(a) for a in args if any(
#                 f not in repr(a) for f in flags)]
#             kwargs_repr = [f"{k}={v!r}" if not callable(
#                 v) else f"{k}={v.__name__}" for k, v in kwargs.items()]
#             signature = ", ".join(args_repr + kwargs_repr)
#             cmd_ = f"{func.__name__}({signature})"
#             dev_dict = func(*args, **kwargs)
#             cmd = "{}.{}".format(dev_dict['name'], cmd_)
#             dev_dict['dev'].output = None
#             if out:
#                 cmd = "{}".format(cmd_)
#             else:
#                 pass
#             dev_dict['dev'].wr_cmd(cmd, capture_output=True)
#             try:
#                 dev_dict['dev'].output = dev_dict['dev'].long_output[0].strip()
#             except Exception as e:
#                 print(e)
#                 pass
#             return None
#         return wrapper_cmd
#     return decorator_cmd_str


def upy_wrcmd_c_r_in_callback(debug=False, rtn=True, out=False):
    def decorator_cmd_str(func):
        @functools.wraps(func)
        def wrapper_cmd(*args, **kwargs):
            flags = ['>', '<', 'object', 'at', '0x']
            args_repr = [repr(a) for a in args if any(
                f not in repr(a) for f in flags)]
            dev_dict = func(*args, **kwargs)
            name = dev_dict['name']
            kwargs_repr = [f"{k}={v!r}" if not callable(
                v) else f"{k}={name}.{v.__name__}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            cmd_ = f"{func.__name__}({signature})"
            cmd = "{}.{}".format(dev_dict['name'], cmd_)
            dev_dict['dev'].output = None
            if out:
                cmd = "{}".format(cmd_)
            else:
                pass
            if debug:
                dev_dict['dev'].wr_cmd(cmd)
            else:
                dev_dict['dev'].wr_cmd(cmd, silent=True)
            if rtn:
                return dev_dict['dev'].output
            else:
                return None
        return wrapper_cmd
    return decorator_cmd_str
