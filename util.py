def remove_comma(entry):
    return "".join(str(entry).split(","))


def add_comma(entry):
    price = remove_comma(entry)
    if str(price).isdigit():
        return f"{int(price):,}"


