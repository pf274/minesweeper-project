import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.classes.Board import Board, boardFromString
from src.classes.Cell import Cell
from src.solver import getFlagRemainingCellMove, getNextMove, getRevealCellMove
from src.moves import FlagRemainingNeighbors, RevealCells, ExpandCell, FlagCells, Move

tests = [
  {
    "problem": boardFromString("""
                               M.M
                               ...
                               """),
    "function": getFlagRemainingCellMove,
    "solution": FlagRemainingNeighbors((1, 0), {(0, 0), (2, 0)})
  }, 
  # {
  #   "problem": Board(width=3, height=3, mines=3, startLocation=(2, 2), grid=[
  #       [Cell(True, False, True, (0, 0)), Cell(False, False, False, (1, 0)), Cell(True, False, True, (2, 0))],
  #       [Cell(False, False, False, (0, 1)), Cell(False, True, False, (1, 1)), Cell(False, True, False, (2, 1))],
  #       [Cell(True, False, True, (0, 2)), Cell(False, True, False, (1, 2)), Cell(False, True, False, (2, 2))]
  #     ]),
  #   "solution": RevealCell((1, 1))
  # },
  {
    "problem": Board(width=3, height=3, mines=1, startLocation=(0, 0), grid=[
        [Cell(False, True, False, (0, 0)), Cell(False, False, False, (1, 0)), Cell(False, True, False, (2, 0))],
        [Cell(False, True, False, (0, 1)), Cell(True, False, False, (1, 1)), Cell(False, True, False, (2, 1))],
        [Cell(False, True, False, (0, 2)), Cell(False, False, False, (1, 2)), Cell(False, True, False, (2, 2))]
    ]),
    "function": getRevealCellMove,
    "solution": RevealCells({(1, 2)})
  },
]

allTestsPassed = True
for test in tests:
  print("Getting next move for board:")
  test['problem'].display()
  try:
    output = test['function'](test["problem"])
    assert output is not None, "Error: No move returned"
    assert output.__class__.__name__ == test['solution'].__class__.__name__, f"Error: Expected move of type {test['solution'].__class__.__name__} but got {output.__class__.__name__}"
    assert output.toJSON() == test['solution'].toJSON(), f"Error: Mismatching move details.\n  Expected: {test['solution'].toJSON()}\n  Actual: {output.toJSON()}"
    print(f"Move returned:\n{output.__class__.__name__}\n{output.toJSON()}")
  except Exception as e:
    print(e)
    allTestsPassed = False
if allTestsPassed:
  print("All tests passed!")