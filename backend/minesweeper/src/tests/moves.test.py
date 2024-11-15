import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.classes.Board import boardFromString
from src.solver import getFlagRemainingNeighbors, getExpandCellMove, getRemainingMinesFlagMove, getIntersectCells, getRemainingCellRevealsMove
from src.moves import Move, HintStep

tests = [
  {
    "problem": boardFromString("""
                               M.M
                               ...
                               """),
    "function": getFlagRemainingNeighbors,
    "solution": Move(cellsToFlag={(0, 0), (0, 2)},hintSteps=[
      HintStep('There are only two squares remaining around this square, and they must be mines.', {(1, 0)}, {(0, 0), (0, 2)})
    ])
  },
  {
    "problem": boardFromString("""
                               F?
                               .F
                               .?
                               """),
    "function": getExpandCellMove,
    "solution": Move(cellsToExpand={(0, 0)}, hintSteps=[
      HintStep('There are no unflagged mines around this square. Reveal the remaining squares!', {(0, 1)}, {(1, 0), (1, 2)})
    ])
  },
  {
    "problem": boardFromString("""
                               F..FF
                               ??MM.
                               ????.
                               """),
    "function": getIntersectCells,
    "solution": Move(cellsToReveal={(0, 1)}, cellsToFlag={(3, 1)}, hintSteps=[
      HintStep('Check out these two cells.', {(1, 0), (2, 0)}, {}),
      HintStep('There is only one remaining mine in these cells.', {(1, 0)}, {(0, 1), (1, 1), (2, 1)}),
      HintStep('This means there can only be one remaining mine in the cells shared by both these numbers.', {(1, 0), (2, 0)}, {(1, 1), (2, 1)}),
      HintStep('That accounts for one of the mines, leaving one more mine in the cells unique to this number.', {(2, 0)}, {(3, 1)}),
      HintStep('There is only one cell unique to this number, so this cell should be flagged.', {(2, 0)}, {(3, 1)}),
      HintStep('Reveal the safe cell unique to this number.', {(1, 0)}, {(0, 1)})
    ]),
  },
  {
    "problem": boardFromString("""
                               ???M
                               ????
                               FF.M
                               ...?
                               ..FF
                               """),
    "function": getIntersectCells,
    "solution": Move(cellsToReveal={(3, 1), (1, 1), (2, 1)}, hintSteps=[
      HintStep('Check out these two cells.', {(2, 3), (2, 2)}, {}),
      HintStep('There is one remaining mine in these cells.', {(2, 3)}, {(3, 2), (3, 3)}),
      HintStep('Therefore, there are no remaining mines in these cells.', {(2, 2)}, {(3, 1), (1, 1), (2, 1)}),
      HintStep('Reveal the safe cells unique to this number.', {(2, 2)}, {(3, 1), (1, 1), (2, 1)})
    ])
  },
  {
    "problem": boardFromString("""
                               MF.
                               FF.
                               ...
                               """),
    "function": getRemainingMinesFlagMove,
    "solution": Move(cellsToFlag={(0, 0)}, hintSteps=[
      HintStep('Flag the remaining mine', {}, {(0, 0)})
    ])
  },
  {
    "problem": boardFromString("""
                               ?F.
                               FF.
                               ...
                               """),
    "function": getRemainingCellRevealsMove,
    "solution": Move(cellsToReveal={(0, 0)}, hintSteps=[
      HintStep('There are no remaining mines to flag. Reveal the remaining squares!', {}, {(0, 0)})
    ])
  }
]

allTestsPassed = True
for index, test in enumerate(tests):
  print(f"-------- test {index + 1} --------")
  print("Getting next move for board:")
  test['problem'].display()
  try:
    output: Move = test['function'](test["problem"])
    assert output is not None, "Error: No move returned"
    assert output.__class__.__name__ == test['solution'].__class__.__name__, f"Error: Expected move of type {test['solution'].__class__.__name__} but got {output.__class__.__name__}"
    expectedOutput: Move = test['solution']
    if output.toJSON() != expectedOutput.toJSON():
      if output.cellsToReveal != expectedOutput.cellsToReveal:
        raise ValueError(f"Error: Mismatching cells to reveal.\n  Expected: {expectedOutput.cellsToReveal}\n  Actual: {output.cellsToReveal}")
      if output.cellsToFlag != expectedOutput.cellsToFlag:
        raise ValueError(f"Error: Mismatching cells to flag.\n  Expected: {expectedOutput.cellsToFlag}\n  Actual: {output.cellsToFlag}")
      if output.cellsToExpand != expectedOutput.cellsToExpand:
        raise ValueError(f"Error: Mismatching cells to expand.\n  Expected: {expectedOutput.cellsToExpand}\n  Actual: {output.cellsToExpand}")
      if output.hintSteps != expectedOutput.hintSteps:
        if len(expectedOutput.hintSteps) == 0:
          raise ValueError(f"Error: Expected these hints:\n  Expected: {[hintStep.toJSON() for hintStep in output.hintSteps]}\n  Actual: No hints")
        elif len(output.hintSteps) != len(expectedOutput.hintSteps):
          raise ValueError(f"Error: Mismatching hint steps.\n  Expected: {len(expectedOutput.hintSteps)} steps\n  Actual: {len(output.hintSteps)} steps")
        for i, hintStep in enumerate(output.hintSteps):
          if hintStep.toJSON() != expectedOutput.hintSteps[i].toJSON():
            raise ValueError(f"Error: Mismatching hint step.\n  Expected: {expectedOutput.hintSteps[i].toJSON()}\n  Actual: {hintStep.toJSON()}")
    print(f"Success! Correct move returned!")
  except Exception as e:
    print(f"Error: {e}")
    allTestsPassed = False
if allTestsPassed:
  print("All tests passed!")
else:
  print("ERROR: Some tests failed.")