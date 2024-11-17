import itertools
from typing import Literal
from Board import Board
from Cell import Cell
from moves import Move, HintStep

def readableNumber(num: int):
  return [
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight"
  ][num]

def getFlagRemainingNeighbors(cell: Cell, mineCount: int, flagCount: int, neighbors: list[Cell]) -> Move:
  """
  Determines if all remaining neighbors of a cell must be mines.
  Args:
    cell (Cell): The cell to check.
    mineCount (int): The number of mines in the cell.
    flagCount (int): The number of flags in the cell.
    neighbors (list[Cell]): The neighbors of the cell.
  Returns:
    Move: The move to place flags on the unrevealed neighbors, or None if no move is found.
  """
  hiddenNeighbors = [neighbor for neighbor in neighbors if not neighbor.isVisible and not neighbor.isFlagged]
  if mineCount == len(hiddenNeighbors) + flagCount and len(hiddenNeighbors) > 0:
    neighborLocations = {neighbor.location for neighbor in hiddenNeighbors}
    hintSteps: list[HintStep] = [
      HintStep(f"Flag the remaining cell{'s' if len(neighborLocations) > 1 else ''}", {cell.location}, neighborLocations)
    ]
    return Move(cellsToFlag=neighborLocations, hintSteps=hintSteps)
  return None

def getExpandCell(cell: Cell, mineCount: int, flagCount: int, neighbors: list[Cell]) -> Move:
  """
  Determines if all remaining neighbors of a cell are safe to reveal.
  Args:
    cell (Cell): The cell to check.
    mineCount (int): The number of mines in the cell.
    flagCount (int): The number of flags in the cell.
    neighbors (list[Cell]): The neighbors of the cell.
  Returns:
    Move: The move to reveal the safe neighbors, or None if no move is found.
  """
  hiddenNeighbors = [neighbor for neighbor in neighbors if not neighbor.isVisible and not neighbor.isFlagged]
  if mineCount == flagCount and len(hiddenNeighbors) > 0:
    neighborLocations = {neighbor.location for neighbor in hiddenNeighbors}
    hintSteps: list[HintStep] = [
      HintStep(f"Reveal the remaining cell{'s' if len(neighborLocations) > 1 else ''}", {cell.location}, neighborLocations)
    ]
    return Move(cellsToReveal=neighborLocations, hintSteps=hintSteps)
  return None

def getIntersectCells(cell1Location: tuple[int, int], mineCount1: int, flagCount1: int, neighbors1: list[Cell], cell2Location: tuple[int, int], mineCount2: int, flagCount2: int, neighbors2: list[Cell]) -> Move:
  """
  Checks a pair of cells to see if the intersection of their neighbors reveals the location of mines.
  Args:
    cell1Location (tuple[int, int]): The location of the first cell.
    mineCount1 (int): The number of mines in the first cell.
    flagCount1 (int): The number of flags in the first cell.
    neighbors1 (list[Cell]): The visible neighbors of the first cell within a 5x5 grid.
    cell2Location (tuple[int, int]): The location of the second cell.
    mineCount2 (int): The number of mines in the second cell.
    flagCount2 (int): The number of flags in the second cell.
    neighbors2 (list[Cell]): The visible neighbors of the second cell within a 5x5 grid.
  Returns:
    Move: The move to flag the dangerous cells and reveal the safe cells, or None if no move is found.
  """
  if mineCount1 == 0 or mineCount2 == 0:
    return None
  if mineCount1 == flagCount1 or mineCount2 == flagCount2:
    return None
  # begin the set math!
  set1 = {neighbor for neighbor in neighbors1 if not neighbor.isFlagged and not neighbor.isVisible}
  set1MineCount = mineCount1 - flagCount1
  set2 = {neighbor for neighbor in neighbors2 if not neighbor.isFlagged and not neighbor.isVisible}
  set2MineCount = mineCount2 - flagCount2
  biggerCellLocation = cell1Location if len(set1) > len(set2) else cell2Location
  smallerCellLocation = cell2Location if len(set1) > len(set2) else cell1Location
  biggerSet, biggerSetMineCount = (set1, set1MineCount) if len(set1) > len(set2) else (set2, set2MineCount)
  smallerSet, smallerSetMineCount = (set2, set2MineCount) if len(set1) > len(set2) else (set1, set1MineCount)
  intersection = set1.intersection(set2)
  mineDifference = biggerSetMineCount - smallerSetMineCount # m(A) - m(B)
  setDifference = biggerSet - smallerSet # A - B
  if mineDifference == len(setDifference) and len(setDifference) > 0: # m(A) - m(B) = |A - B|
    # m(A) - m(B) = m(A - B) - m(B - A)
    # m(A - B) will equal |A - B|, so all squares in A - B are mines
    # m(B - A) will equal zero, so all squares in B - A are safe
    safeSet = smallerSet - biggerSet
    dangerousSet = biggerSet - smallerSet
    hintSteps: list[HintStep] = [
      HintStep("Check out these two cells.", {cell1Location, cell2Location}, {}),
      HintStep(f"There {'are' if smallerSetMineCount > 1 else 'is'} only {readableNumber(smallerSetMineCount)} remaining mine{'s' if smallerSetMineCount > 1 else ''} in {'these' if len(smallerSet) > 1 else 'this'} cell{'s' if len(smallerSet) > 1 else ''}.", {smallerCellLocation}, {c.location for c in smallerSet}),
      HintStep(f"This means there can only be {readableNumber(smallerSetMineCount)} remaining mine{'s' if smallerSetMineCount > 1 else ''} in the cell{'s' if len(intersection) > 1 else ''} shared by both these numbers.", {smallerCellLocation, biggerCellLocation}, {c.location for c in intersection}),
      HintStep(f"That accounts for {readableNumber(smallerSetMineCount)} of the mines, leaving {readableNumber(mineDifference)} more mine{'s' if mineDifference > 1 else ''} in the cells unique to this number.", {biggerCellLocation}, {c.location for c in setDifference}),
      HintStep(f"There {'are' if mineDifference > 1 else 'is'} only {readableNumber(mineDifference)} cell{'s' if mineDifference > 1 else ''} unique to this number, so {'these cells' if mineDifference > 1 else 'this cell'} should be flagged.", {biggerCellLocation}, {c.location for c in dangerousSet}),
      HintStep(f"Reveal the safe cell{'s' if smallerSetMineCount > 1 else ''} unique to this number.", {smallerCellLocation}, {c.location for c in safeSet})
    ]
    return Move(cellsToReveal={cell.location for cell in safeSet}, cellsToFlag={cell.location for cell in dangerousSet}, hintSteps=hintSteps)
  elif mineDifference == 0 and len(setDifference) > 0 and intersection == smallerSet:
    safeSet = setDifference
    dangerousSet = intersection
    hintSteps: list[HintStep] = [
      HintStep("Check out these two cells.", {cell1Location, cell2Location}, {}),
      HintStep(f"There {'are' if smallerSetMineCount > 1 else 'is'} {readableNumber(smallerSetMineCount)} remaining mine{'s' if smallerSetMineCount > 1 else ''} in {'these' if len(smallerSet) > 1 else 'this'} cell{'s' if len(smallerSet) > 1 else ''}.", {smallerCellLocation}, {c.location for c in intersection}),
      HintStep(f"Therefore, there are no remaining mines in {'these' if len(safeSet) > 1 else 'this'} cell{'s' if len(safeSet) > 1 else ''}.", {biggerCellLocation}, {c.location for c in safeSet}),
      HintStep(f"Reveal the safe cell{'s' if len(safeSet) > 1 else ''} unique to this number.", {biggerCellLocation}, {c.location for c in safeSet})
    ]
    return Move(cellsToReveal={cell.location for cell in safeSet}, hintSteps=hintSteps)
  return None

def getFlagRemainingMines(board: Board) -> Move:
  """
  Attempts to find a set of cells that can be flagged as mines based on the number of remaining mines on the board.
  It starts by evaluating if the number of remaining mines is equal to the number of unrevealed cells, and if so, flags all unrevealed cells.
  If not, it groups cells together, then tries to place the fewest flags possible to satisfy the revealed neighbors of each group.
  If the minimum number of flags possible to fulfill all exposed neighbors is equal to the number of remaining mines, it returns the move.
  Otherwise, it returns None.
  Args:
    board (Board): The Minesweeper board.
  Returns:
    Move: The move to flag the cells, or None if no move is found.
  """
  # print("getRemainingMinesFlagMove")
  unrevealedCells = [cell for row in board.grid for cell in row if not cell.isVisible and not cell.isFlagged]
  flaggedCells = [cell for row in board.grid for cell in row if cell.isFlagged]
  remainingMines = board.mines - len(flaggedCells)
  if remainingMines == len(unrevealedCells):
    hintSteps: list[HintStep] = [
      HintStep(f"Flag {'the' if remainingMines == 1 else 'all'} remaining mine{'s' if remainingMines > 1 else ''}", {}, {cell.location for cell in unrevealedCells})
    ]
    return Move(cellsToFlag={cell.location for cell in unrevealedCells}, hintSteps=hintSteps)
  # form cell groups
  cellGroups: list[list[Cell]] = []
  for i in range(len(unrevealedCells)):
    cell = unrevealedCells[i]
    neighbors = board.neighbors(cell)
    group = None
    for j in range(len(cellGroups)):
      potentialGroup = cellGroups[j]
      if any(neighbor.location in potentialGroup for neighbor in neighbors):
        cellGroups[j].append(cell)
        break
    if group is None:
      cellGroups.append([cell])
  # categorize groups
  exposedGroups: list[tuple[list[Cell],list[Cell]]] = []
  for group in cellGroups:
    revealedNeighbors = set()
    for cell in group:
      if any(neighbor.isVisible for neighbor in board.neighbors(cell)):
        revealedNeighbors.add(cell)
        break
    if len(revealedNeighbors) > 0:
      exposedGroups.append((list(revealedNeighbors), group))
  # combine groups that share a revealed neighbor
  for i in range(len(exposedGroups)):
    neighbors, group = exposedGroups[i]
    for j in range(i + 1, len(exposedGroups)):
      neighbors2, group2 = exposedGroups[j]
      if any(neighbor in neighbors for neighbor in neighbors2):
        exposedGroups[i] = (neighbors.union(neighbors2), group.union(group2))
        del exposedGroups[j]
        break
  # for each group, only keep cells with a revealed neighbor
  groupsToAnalyze: list[tuple[list[Cell],list[Cell]]] = []
  for i in range(len(exposedGroups)):
    neighbors, group = exposedGroups[i]
    cellsToKeep = []
    for cell in group:
      if any(neighbor in neighbors for neighbor in board.neighbors(cell)):
        cellsToKeep.append(cell)
    if len(cellsToKeep) > 15:
      # print("getRemainingMinesFlagMove: Too many cells to analyze")
      return None # too many cells to analyze
    groupsToAnalyze.append((neighbors, cellsToKeep))
  # analyze groups by trying to place the fewest flags possible to satisfy the revealed neighbors
  allFlags: set[tuple[int, int]] = set()
  for neighbors, group in groupsToAnalyze:
    numFlags = 0
    foundSolutionForGroup = False
    while numFlags <= len(group) and not foundSolutionForGroup:
      for flags in itertools.combinations(group, numFlags):
        if all(board.cellMinesNum(neighbor) == board.cellFlagsNum(neighbor) for neighbor in neighbors):
          allFlags.update({flag.location for flag in flags})
          if foundSolutionForGroup:
            return None # multiple solutions found
          foundSolutionForGroup = True
      numFlags += 1
  
  # see if all mines have been flagged!
  if len(allFlags) > 0:
    if len(allFlags) == remainingMines:
      hintSteps: list[HintStep] = [
        HintStep(f"There {'are' if remainingMines > 1 else 'is'} only {remainingMines} remaining mine{'s' if remainingMines > 1 else ''} left", {}, {cell.location for cell in unrevealedCells}),
        HintStep("This is the only possible configuration", {}, {cell.location for cell in allFlags})
      ]
      return Move(cellsToFlag=allFlags, hintSteps=hintSteps)
  return None

def getRevealRemainingCells(board: Board) -> Move:
  """
  If there are no more mines to flag, this function will reveal the remaining cells.
  Args:
    board (Board): The Minesweeper board.
  Returns:
    RevealCell: The move to reveal the cells, or None if no move is found.
  """
  # print("getRemainingCellRevealsMove")
  remainingMines = board.getRemainingMineCount()
  cellsToReveal = set() # should be a set of all unrevealed cell locations (tuples x, y)
  
  if remainingMines == 0:
    for row in board.grid:
      for current_cell in row:
        if not current_cell.isVisible and not current_cell.isFlagged:
          cellsToReveal.add(current_cell.location)
      
    hintSteps : list[HintStep] = [
      HintStep("There are no remaining mines to flag. Reveal the remaining squares!", {}, cellsToReveal)
    ]
      
    return Move(cellsToReveal= cellsToReveal, hintSteps= hintSteps)

def getNextMove(board: Board, type: Literal['getFlagRemainingNeighbors', 'getExpandCell', 'getIntersectCells', 'getRevealRemainingCells', 'getFlagRemainingMines', None] = None) -> Move:
  """
  Determines the next move to make on the Minesweeper board.
  Args:
    board (Board): The Minesweeper board.
  Returns:
    Move: The move to make, or None if no move is found.
  """
  visibleCells: list[dict] = list()
  for row in board.grid:
    for cell in row:
      if cell.isVisible:
        neighbors = board.neighbors(cell)
        mineCount = board.cellMinesNum(cell)
        flagCount = board.cellFlagsNum(cell)
        visibleCells.append({
          "location": cell.location,
          "mineCount": mineCount,
          "flagCount": flagCount,
          "neighbors": neighbors
        })
        if type == 'getFlagRemainingNeighbors' or type is None:
          move = getFlagRemainingNeighbors(cell, mineCount, flagCount, neighbors)
          if move:
            return move
        if type == 'getExpandCell' or type is None:
          move = getExpandCell(cell, mineCount, flagCount, neighbors)
          if move:
            return move
  if type == 'getIntersectCells' or type is None:
    pairCombos = itertools.combinations(visibleCells, 2)
    for pair in pairCombos:
      cell1Info = pair[0]
      cell2Info = pair[1]
      xDiff = cell1Info['location'][0] - cell2Info['location'][0]
      yDiff = cell1Info['location'][1] - cell2Info['location'][1]
      if xDiff < -2 or xDiff > 2 or yDiff < -2 or yDiff > 2:
        continue
      move = getIntersectCells(cell1Info['location'], cell1Info['mineCount'], cell1Info['flagCount'], cell1Info['neighbors'], cell2Info['location'], cell2Info['mineCount'], cell2Info['flagCount'], cell2Info['neighbors'])
      if move:
        return move
  if type == 'getRevealRemainingCells' or type is None:
    move = getRevealRemainingCells(board)
    if move:
      return move
  if type == 'getFlagRemainingMines' or type is None:
    move = getFlagRemainingMines(board)
    if move:
      return move
  return None