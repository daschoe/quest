"""Different randomization methods"""
from math import floor


def balanced_latin_squares(n):
    """
        Creates orders of scene sequences
        from: https://medium.com/@graycoding/balanced-latin-squares-in-python-2c3aa6ec95b9
        but changed a bit
        Checked against: http://statpages.info/latinsq.html

        Parameters
        ----------
        n : int
            size of the square / number of stimuli

        Returns
        -------
        list[list[int]]
            compiled square
    """
    latin = [[((floor(j / 2 + 1) if j % 2 else floor(n - j / 2)) + i) % n + 1 for j in range(n)] for i in range(n)]
    if n % 2:  # Repeat reversed for odd n
        latin += [seq[::-1] for seq in latin]
    return latin


def order_from_file(file):
    """Load custom randomization orders from file.

    Parameters
    ----------
    file : str
        file holding comma separated integers (no comma on line break)

    Returns
    -------
    list[list[int]]
        list of orders
    """
    with open(file) as f:
        orders = f.read().splitlines()
    for row, order in enumerate(orders):
        orders[row] = order.split(",")
        for entry in range(0, len(orders[row])):
            orders[row][entry] = int(orders[row][entry])
    return orders
