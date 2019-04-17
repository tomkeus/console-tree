#! /usr/bin/env python3

import typing
import argparse
import json
import sys
import os


JUNCTION = "\u251c"
VERTICAL = "\u2502"
CORNER = "\u2514"
HORIZONTAL = "\u2500"

EMPTY_CELL = ""


def tabularize_tree(tree_object: typing.Union[int, float, bool, str, list, dict], simple_mode: bool) -> list:
    """ Transforms tree into a tabular form. All tree items at the same depth level are
    positioned in the same column. Parents are positioned one column to the left and
    one row above with respect to the first child.

    If simple mode is indicated, parents the array elements directly under the parent
    array. Otherwise, they will be parented under their corresponding index, which will
    be parented under parent array.

    Remark: tree items cannot be empty strings

    :param tree_object: a dictionary, list, or atomic value of type int, float, bool, str
    :param simple_mode: a boolean, indicating whether to use simple mode
    :return: tabular representation of the tree (rectangular list of lists)
    """
    # If its an atomic value, just wrap it into 2D array
    if isinstance(tree_object, (int, float, bool, str)):
        # If string, check it's not empty
        if isinstance(tree_object, str):
            if tree_object.strip() == "":
                raise ValueError("Tree items cannot be empty strings")

        return [[str(tree_object)]]
    # If its a list, we have a list of items with the same depth
    elif isinstance(tree_object, list):
        # Table cells to be filled
        cells = []

        if simple_mode:
            # For each item in a list, get its tabular representation and
            # add it to the list of cells
            for oi in tree_object:
                cells += [row for row in tabularize_tree(oi, simple_mode)]
        else:
            for i, oi in enumerate(tree_object):
                cells += [[str(i)]] + [[EMPTY_CELL] + row for row in tabularize_tree(oi, simple_mode)]

        return cells
    # If its a dictionary, we have a list parents and their children
    elif isinstance(tree_object, dict):
        # Table cells to be filed
        cells = []

        # Tabularize children for each parent and add to the list of cells
        for parent, children in tree_object.items():
            # For each parent, add a row containing only parent, and then for each
            # child row, add empty cell followed by the child row. Adding empty cell
            # offsets children one column to the right from the parent
            cells += [[parent]] + [[EMPTY_CELL] + row for row in tabularize_tree(children, simple_mode)]

        # Since rows are staggered we need to pad them from the end
        # in order to obtain rectangular table.

        # Get the longest row
        max_row_len = max(len(row) for row in cells)

        # Pad all the rows to the longest row length
        for i, row in enumerate(cells):
            cells[i] = row + [EMPTY_CELL] * (max_row_len - len(row))

        return cells
    else:
        raise TypeError("Type " + type(tree_object) + " is unsupported in the tree")


def draw(cells: list, element: str, i: int, j: int):
    """ Draws piece of an angular connector. Assumes drawing is top-down and then left-right,
    starting from parent in a column, towards its children in rows below the parent and in
    the column directly to the right of the parent. Cannot be used to draw on cells that
    contain tree items. It can only be used to draw on empty cells

    :param cells: table of cells (rectangular list of lists)
    :param element: element to draw (VERTICAL, CORNER, JUNCTION or HORIZONTAL)
    :param i: row index of the cell where to draw
    :param j: column index of the cell where to draw
    :return:
    """

    # Get length of the cell
    cell_len = len(cells[i][j])

    # Get cell value
    cell_val = "" if cells[i][j].strip() == "" else cells[i][j][0]

    # Since we are drawing top-down and left-right, we always draw
    # down the column from a parent to its child. This means we pull
    # VERTICAL down the colum until we reach child's row, and then
    # we add CORNER and pad with HORIZONTAL until cell is filled.
    # Since a parent can have multiple children, we can draw over
    # already drawn connector. So if we draw VERTICAL over an already
    # drawn CORNER, we have to make sure we change the CORNER
    # into the JUNCTION
    if element == VERTICAL:
        # If we are drawing VERTICAL over an empty cell, or
        # existing VERTICAL, just add vertical to the beginning
        # of the cell
        if cell_val == "" or cell_val == VERTICAL:
            cells[i][j] = VERTICAL + cells[i][j][1:]
        # If we are drawing VERTICAL over CORNER, we have to
        # change the corner into JUNCTION
        elif cell_val == CORNER:
            cells[i][j] = JUNCTION + cells[i][j][1:]
        # If we are drawing VERTICAL over JUNCTION, there is nothing to do
        elif cell_val == JUNCTION:
            pass
        # If we are drawing over horizontal, draw method is not used correctly
        else:
            raise RuntimeError("It should not be possible for VERTICAL to be drawn over HORIZONTAL")
    elif element == HORIZONTAL:
        # If we are drawing HORIZONTAL over an empty cell, we just
        # need to add CORNER and then pad the rest of the cell with
        # HORIZONTAL
        if cell_val == "":
            cells[i][j] = CORNER + HORIZONTAL * (cell_len - 1)
        # If we are drawing HORIZONTAL over non-empty cell, draw
        # method is not used correctly
        else:
            raise RuntimeError("It should not be possible to draw HORIZONTAL over non-empty cell")


def connect(cells, parent_i, parent_j, child_i):
    """ Draws connection between a parent and its child. All children are required
    to be in the rows below the parent and in the column immediately to the right
    of the parent.

    :param cells: table of cells (rectangular list of lists)
    :param parent_i: row index of a parent
    :param parent_j: column index of a parent
    :param child_i:
    :return:
    """
    # Make sure child is in a row below the parent's row
    if child_i <= parent_i:
        raise ValueError("Cannot draw from parent at cell ({0}, {1}) to a child in the row {2} "
                         "which is above it's parent's row".format(parent_i, parent_j, child_i))

    # Draw vertical segments down the parent's column until the child's row
    for i in range(parent_i + 1, child_i):
        draw(cells, VERTICAL, i, parent_j)

    # Draw horizontal segment on the cell immediately to the left of the child
    draw(cells, HORIZONTAL, child_i, parent_j)


def fit_column_width(cells: list) -> list:
    """ Format table cells so that all cells in the same column have same width.

    :param cells: table of cells (rectangular list of lists)
    :return:
    """

    # Initialize column widths to 0
    col_widths = [0] * len(cells[0])

    # Determine maximal cell length for each column
    for i, row in enumerate(cells):
        col_widths = [max(col_widths[j], len(row[j])) for j in range(len(cells[0]))]

    # Format string for each column
    col_formats = ["{{0:<{0}}}".format(ci) for ci in col_widths]

    # Format the cells according to the corresponding column format
    for i, row in enumerate(cells):
        cells[i] = [cfi.format(ci) for cfi, ci in zip(col_formats, row)]

    return cells


def find_parents(cells, j):
    """ Find parents items in a given column

    :param cells: table of cells (rectangular list of lists)
    :param j: column index
    :return: list of parent row indices in a column
    """

    # Find non-empty cells in a column and return their indices
    return [i for i in range(len(cells)) if cells[i][j].strip() != ""]


def find_children(cells, i, j):
    """ Find children belonging to a given parent

    :param cells: table of cells (rectangular list of lists)
    :param i: parent's row index
    :param j: parent's column index
    :return: list of children's row indices
    """

    # Storage for child row indicees
    children = []

    # Starting from a row below the parent's row, go down
    # the parent's column
    for i in range(i + 1, len(cells)):
        # If next parent is reached abort search
        if cells[i][j].strip() != "":
            break

        # If cell in the column to the right is not empty
        # we have found a child item and we add its row
        # index to the list
        if cells[i][j + 1].strip() != "":
            children.append(i)

    return children


def repr_tree(tree_object: dict, simple_mode: bool) -> str:
    """ Generate string representation of a tree. Tree object must have a root.

    :param tree_object: a dictionary, list, or atomic value of type int, float, bool, str
    :param simple_mode: a boolean, indicating whether to use simple mode
    :return: string representation of a tree
    """

    # Ensure we have a root
    if len(tree_object) != 1:
        raise ValueError("Tree must have a root")

    # Get tabular representation of the tree
    cells = tabularize_tree(tree_object, simple_mode)

    # Deal with trivial case
    if len(cells) == 1:
        return cells[0][0]

    # Format cell widths so that all cells in a column have same widths
    # and all cell content fits
    cells = fit_column_width(cells)

    # For each column in the table
    for j in range(len(cells[0]) - 1):
        # Find parent items in the column
        parents = find_parents(cells, j)

        # For each parent
        for parent_i in parents:
            # Find its children and for each child draw
            # the connection
            for child_i in find_children(cells, parent_i, j):
                connect(cells, parent_i, j, child_i)

    return "\n".join(["".join(row) for row in cells])


def main():
    parser = argparse.ArgumentParser(description="Draws tree corresponding to the specified JSON file")

    parser.add_argument("file", type=str, help="JSON file to draw. UTF-8 encoding is supported. The "
                                               "content of the JSON file must have a root. If that is "
                                               "not the case, use --add-root option")
    parser.add_argument("-s", "--simple-mode", action="store_true", default=False,
                        help="Whether to use simple mode. In simple mode, array elements are just "
                             "parented directly under parent array, without indices being shown")
    parser.add_argument("-r", "--add-root", type=str, default=None,
                        help="Name of the root which will be parent to the content of the JSON file. "
                             "To be used when the content of the JSON file has no root")

    try:
        args = parser.parse_args()
    except Exception as err:
        sys.stderr.write("Error: Unable to parse command line arguments. "
                         "Error was:\n{0}\n".format(err))

        exit(-1)

    if not os.path.isfile(args.file):
        sys.stderr.write("Error: Specified file {0} does not exist\n".format(args.file))

        sys.exit(-1)

    try:
        json_txt = open(args.file, encoding="utf-8").read()
    except IOError as err:
        sys.stderr.write("Error: Unhandled exception caught when "
                         "opening the input file. Exception was:\n{0}\n".format(err))

        sys.exit(-1)

    try:
        tree_obj = json.loads(json_txt)
    except Exception as err:
        sys.stderr.write("Error: Unhandled exception caught when "
                         "parsing JSON. Exception was:\n{0}\n".format(err))

        sys.exit(-1)

    if args.add_root is not None:
        tree_obj = {args.add_root: tree_obj}

    try:
        tree_repr = repr_tree(tree_obj, args.simple_mode)

        sys.stdout.write(tree_repr + "\n")
    except Exception as err:
        sys.stderr.write("Error: Unhandled exception caught when "
                         "drawing the tree. Exception was:\n{0}\n".format(err))

        sys.exit(-1)


if __name__ == "__main__":
    main()

