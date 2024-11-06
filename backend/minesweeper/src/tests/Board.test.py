import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.classes.Board import Board
from src.classes.Cell import Cell

threeRemainingUnflagged = Board(width=3, height=3, mines=3, startLocation=(2, 2), grid=[
  [Cell(True, False, False, (0, 0)), Cell(False, True, False, (1, 0)), Cell(True, False, False, (2, 0))],
  [Cell(False, True, False, (0, 1)), Cell(False, True, False, (1, 1)), Cell(False, True, False, (2, 1))],
  [Cell(True, False, False, (0, 2)), Cell(False, True, False, (1, 2)), Cell(False, True, False, (2, 2))]
])
# B 2 B
# 2 3 1
# B 1 0
threeRemainingFlagged = Board(width=3, height=3, mines=3, startLocation=(2, 2), grid=[
  [Cell(True, False, True, (0, 0)), Cell(False, False, False, (1, 0)), Cell(True, False, True, (2, 0))],
  [Cell(False, False, False, (0, 1)), Cell(False, True, False, (1, 1)), Cell(False, True, False, (2, 1))],
  [Cell(True, False, True, (0, 2)), Cell(False, True, False, (1, 2)), Cell(False, True, False, (2, 2))]
])
# F B F
# B 3 1
# F 1 0
# assert threeRemainingUnflagged.getNextStep() == ('flag', {(0, 0), (2, 0), (0, 2)}), "Error: Expected to flag cells at (0, 0), (2, 0), and (0, 2)"
# assert threeRemainingFlagged.getNextStep() == ('reveal', {(1, 1)}), "Error: Expected to reveal cell at (1, 1)"
# print("All tests pass!")

# threeRemainingFlagged.display()
# threeRemainingUnflagged.display()