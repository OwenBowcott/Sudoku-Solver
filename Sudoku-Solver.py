

import csv
import itertools

class Board():

    ##########################################
    ####   Constructor
    ##########################################
    def __init__(self, filename):

        # initialize all of the variables
        self.n2 = 0
        self.n = 0
        self.spaces = 0
        self.board = None
        self.valsInRows = None
        self.valsInCols = None
        self.valsInBoxes = None
        self.unsolvedSpaces = None

        # load the file and initialize the in-memory board with the data
        self.loadSudoku(filename)


    # loads the sudoku board from the given file
    def loadSudoku(self, filename):

        with open(filename) as csvFile:
            self.n = -1
            reader = csv.reader(csvFile)
            for row in reader:

                # Assign the n value and construct the appropriately sized dependent data
                if self.n == -1:
                    self.n = int(len(row) ** (1/2))
                    if not self.n ** 2 == len(row):
                        raise Exception('Each row must have n^2 values! (See row 0)')
                    else:
                        self.n2 = len(row)
                        self.spaces = self.n ** 4
                        self.board = {}
                        self.valsInRows = [set() for _ in range(self.n2)]
                        self.valsInCols = [set() for _ in range(self.n2)]
                        self.valsInBoxes = [set() for _ in range(self.n2)]
                        self.unsolvedSpaces = set(itertools.product(range(self.n2), range(self.n2)))

                # check if each row has the correct number of values
                else:
                    if len(row) != self.n2:
                        raise Exception('Each row must have the same number of values. (See row ' + str(reader.line_num - 1) + ')')

                # add each value to the correct place in the board; record that the row, col, and box contain the value
                for index, item in enumerate(row):
                    if not item == '':
                        self.board[(reader.line_num-1, index)] = int(item)
                        self.valsInRows[reader.line_num-1].add(int(item))
                        self.valsInCols[index].add(int(item))
                        self.valsInBoxes[self.spaceToBox(reader.line_num-1, index)].add(int(item))
                        self.unsolvedSpaces.remove((reader.line_num-1, index))


    ##########################################
    ####   Utility Functions
    ##########################################

    # converts a given row and column to its inner box number
    def spaceToBox(self, row, col):
        return self.n * (row // self.n) + col // self.n

    # prints out a command line representation of the board
    def print(self):
        for r in range(self.n2):
            # add row divider
            if r % self.n == 0 and not r == 0:
                if self.n2 > 9:
                    print("  " + "----" * self.n2)
                else:
                    print("  " + "---" * self.n2)

            row = ""

            for c in range(self.n2):

                if (r,c) in self.board:
                    val = self.board[(r,c)]
                else:
                    val = None

                # add column divider
                if c % self.n == 0 and not c == 0:
                    row += " | "
                else:
                    row += "  "

                # add value placeholder
                if self.n2 > 9:
                    if val is None:
                        row += "__"
                    else:
                        row += "%2i" % val
                else:
                    if val is None:
                        row += "_"
                    else:
                        row += str(val)
            print(row)


    ##########################################
    ####   Move Functions - YOUR IMPLEMENTATIONS GO HERE
    ##########################################

    # makes a move, records it in its row, col, and box, and removes the space from unsolvedSpaces
    def makeMove(self, space, val):
        self.board[space] = val
        self.valsInRows[space[0]].add(val)
        self.valsInCols[space[1]].add(val)
        self.valsInBoxes[self.spaceToBox(space[0], space[1])].add(val)
        self.unsolvedSpaces.remove(space)

    # removes the move, its record in its row, col, and box, and adds the space back to unsolvedSpaces
    def undoMove(self, space, val):
        del self.board[space]
        self.valsInRows[space[0]].remove(val)
        self.valsInCols[space[1]].remove(val)
        self.valsInBoxes[self.spaceToBox(space[0], space[1])].remove(val)
        self.unsolvedSpaces.add(space)

    # returns True if the space is empty and on the board,
    # and assigning value to it if not blocked by any constraints
    def isValidMove(self, space, value):
        if space not in self.unsolvedSpaces:
            return False
        else:
            row, col = space
            box = self.spaceToBox(row, col)
            if (
                value in self.valsInBoxes[box] or
                value in self.valsInCols[col] or
                value in self.valsInRows[row]
            ):
                return False
            else:
                return True

    # optional helper function for use by getMostConstrainedUnsolvedSpace
    def evaluateSpace(self, space):
        lst = [1,2,3,4,5,6,7,8,9]
        row = space[0]
        col = space[1]
        box = self.spaceToBox(row, col)
        for item in self.valsInBoxes[box]:
            if item in lst:
                lst.remove(item)
        for item in self.valsInRows[row]:
            if item in lst:
                lst.remove(item)
        for item in self.valsInCols[col]:
            if item in lst:
                lst.remove(item)
        return len(lst)

    # gets the unsolved space with the most current constraints
    # returns None if unsolvedSpaces is empty
    def getMostConstrainedUnsolvedSpace(self):
        if not self.unsolvedSpaces:
            return None
        else:
            space = list(self.unsolvedSpaces)[0]
            for tempSpace in self.unsolvedSpaces:
                tempVal = self.evaluateSpace(tempSpace)
                val = self.evaluateSpace(space)
                if tempVal < val:
                    space = tempSpace
        return space

class Solver:
    ##########################################
    ####   Constructor
    ##########################################
    def __init__(self):
        pass

    ##########################################
    ####   Solver
    ##########################################

    # recursively selects the most constrained unsolved space and attempts
    # to assign a value to it

    # upon completion, it will leave the board in the solved state (or original
    # state if a solution does not exist)

    # returns True if a solution exists and False if one does not
    def solveBoard(self, board): 
        if not board.unsolvedSpaces:
            return True
        constrainedSpace = board.getMostConstrainedUnsolvedSpace()
        for i in range(1, board.n2 + 1):
            if board.isValidMove(constrainedSpace, i):
                board.makeMove(constrainedSpace, i)
                possibleSol = self.solveBoard(board)
                if possibleSol:
                    return possibleSol
                else:
                    board.undoMove(constrainedSpace, i)
        return False

if __name__ == "__main__":
    # change this to the input file that you'd like to test
    board = Board('Desktop/Artificial Intellengence/A2/example.csv')
    s = Solver()
    s.solveBoard(board)
    board.print()
