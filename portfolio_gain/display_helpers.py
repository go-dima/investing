from colorama import Fore, Style


def repr_float(num: float):
    try:
        return f"{num:,.2f}"
    except TypeError:
        return "nan"


def repr_int(num: int):
    try:
        return f"{num:,}"
    except TypeError:
        return "nan"


def rg(text):
    is_negative = text[0] == '-' if type(text) == str else text < 0
    if is_negative:
        return Fore.RED + text + Style.RESET_ALL
    return Fore.GREEN + text + Style.RESET_ALL
