from colorama import Fore, Style


def repr_float(num: float):
    return f"{num:,.2f}"


def repr_int(num: int):
    return f"{num:,}"


def rg(text):
    is_negative = text[0] == '-' if type(text) == str else text < 0
    if is_negative:
        return Fore.RED + text + Style.RESET_ALL
    return Fore.GREEN + text + Style.RESET_ALL
