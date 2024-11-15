import itertools
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.classes.Board import Board
from src.classes.Cell import Cell
from src.moves import Move, HintStep

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

def getFlagRemainingNeighbors(board: Board) -> Move:
  """
  Attempts to find an cell where all unrevealed neighbors must be mines.
  Args:
    board (Board): The Minesweeper board.
  Returns:
    Move: The move to place flags on the unrevealed neighbors, or None if no move is found.
  """
  
  for row in board.grid:
    for current_cell in row:
      
      numOfMines = board.cellMinesNum(current_cell)
      neighbors = board.neighbors(current_cell)
      numOfFlaggedNeighbor = board.cellFlagsNum(current_cell)
      hiddenNeighbors = []
      
      for neighbor in neighbors:
        if not neighbor.isVisible and not neighbor.isFlagged:
          hiddenNeighbors.append(neighbor)
          
      if numOfMines == len(hiddenNeighbors) + numOfFlaggedNeighbor and len(hiddenNeighbors) > 0:
        neighborLocations = {neighbor.location for neighbor in hiddenNeighbors}
        
        hintSteps : list[HintStep] = [
          HintStep("Flag the remaining cell", {current_cell.location}, neighborLocations)
        ]
        
        return Move(cellsToFlag= neighborLocations, hintSteps= hintSteps)
      
  return None

def getExpandCellMove(board: Board) -> Move:
  """
  Attempts to find an cell where all remaining neighbors are safe.
  Args:
    board (Board): The Minesweeper board.
  Returns:
    Move: The move to reveal safe neighbors, or None if no move is found.
  """
  
  for row in board.grid:
    for current_cell in row:
      
      if not current_cell.isVisible:
        continue
      
      neighbors = board.neighbors(current_cell)
      numOfMines = board.cellMinesNum(current_cell)
      numOfFlags = board.cellFlagsNum(current_cell)
      
      if numOfFlags == numOfMines:
      
        notFlaggedNeighbors = []
        
        for neighbor in neighbors:
          if not neighbor.isFlagged and not neighbor.isVisible:
            notFlaggedNeighbors.append(neighbor)
            
        neighborLocations = {neighbor.location for neighbor in notFlaggedNeighbors}   
            
        hintSteps : list[HintStep] = [
            HintStep("Reveal the remaining cell", {current_cell.location}, neighborLocations)
          ]
        
        return Move(cellsToReveal= {neighbor.location for neighbor in notFlaggedNeighbors}, hintSteps= hintSteps)
      
  return None

def pairCoords(x: int, y: int, width: int, height: int):
  """
  Returns the coordinates in a 5x5 grid around the given coordinates, not including the center.
  This is used in getIntersectCells to find pairs of cells that share neighbors.
  """
  potentialCoords = [
    (x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
    (x - 1, y), (x + 1, y),
    (x - 1, y + 1), (x, y + 1), (x + 1, y + 1),
    (x - 2, y - 2), (x - 1, y - 2), (x, y - 2), (x + 1, y - 2), (x + 2, y - 2),
    (x - 2, y - 1), (x + 2, y - 1),
    (x - 2, y), (x + 2, y),
    (x - 2, y + 1), (x + 2, y + 1),
    (x - 2, y + 2), (x - 1, y + 2), (x, y + 2), (x + 1, y + 2), (x + 2, y + 2)
  ]
  return [coords for coords in potentialCoords if 0 <= coords[0] < width and 0 <= coords[1] < height]

def getIntersectCells(board: Board) -> Move:
  """
  Attempts to find a pair of cells where the intersection of their neighbors reveals the location of mines.
  Args:
    board (Board): The Minesweeper board.
  Returns:
    Move: The move to flag the dangerous cells and reveal the safe cells, or None if no move is found.
  """
  for y in range(board.height):
    for x in range(board.width):
      cell = board.grid[y][x]
      numMines1 = board.cellMinesNum(cell)
      numFlags1 = board.cellFlagsNum(cell)
      if (cell.isVisible and numMines1 > 0 and numMines1 != numFlags1) is False:
        continue
      # find revealed, incomplete cells that share neighbors with this cell
      pairContestants = []
      potentialCoords = pairCoords(x, y, board.width, board.height)
      for x2, y2 in potentialCoords:
        cell2 = board.grid[y2][x2]
        numMines2 = board.cellMinesNum(cell2)
        numFlags2 = board.cellFlagsNum(cell2)
        if cell2.isVisible and numMines2 > 0 and numFlags2 != numMines2:
          pairContestants.append((cell2, numMines2, numFlags2))
      for cell2, numMines2, numFlags2 in pairContestants:
        # begin the set math!
        set1 = {neighbor for neighbor in board.neighbors(cell) if not neighbor.isFlagged and not neighbor.isVisible}
        set1MineCount = numMines1 - numFlags1
        set2 = {neighbor for neighbor in board.neighbors(cell2) if not neighbor.isFlagged and not neighbor.isVisible}
        set2MineCount = numMines2 - numFlags2
        biggerCell = cell if len(set1) > len(set2) else cell2
        smallerCell = cell2 if len(set1) > len(set2) else cell
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
            HintStep("Check out these two cells.", {cell.location, cell2.location}, {}),
            HintStep(f"There {'are' if smallerSetMineCount > 1 else 'is'} only {readableNumber(smallerSetMineCount)} remaining mine{'s' if smallerSetMineCount > 1 else ''} in {'these' if len(smallerSet) > 1 else 'this'} cell{'s' if len(smallerSet) > 1 else ''}.", {smallerCell.location}, {c.location for c in smallerSet}),
            HintStep(f"This means there can only be {readableNumber(smallerSetMineCount)} remaining mine{'s' if smallerSetMineCount > 1 else ''} in the cell{'s' if len(intersection) > 1 else ''} shared by both these numbers.", {smallerCell.location, biggerCell.location}, {c.location for c in intersection}),
            HintStep(f"That accounts for {readableNumber(smallerSetMineCount)} of the mines, leaving {readableNumber(mineDifference)} more mine{'s' if mineDifference > 1 else ''} in the cells unique to this number.", {biggerCell.location}, {c.location for c in setDifference}),
            HintStep(f"There {'are' if mineDifference > 1 else 'is'} only {readableNumber(mineDifference)} cell{'s' if mineDifference > 1 else ''} unique to this number, so {'these cells' if mineDifference > 1 else 'this cell'} should be flagged.", {biggerCell.location}, {c.location for c in dangerousSet}),
            HintStep(f"Reveal the safe cell{'s' if smallerSetMineCount > 1 else ''} unique to this number.", {smallerCell.location}, {c.location for c in safeSet})
          ]
          return Move(cellsToReveal={cell.location for cell in safeSet}, cellsToFlag={cell.location for cell in dangerousSet}, hintSteps=hintSteps)
        elif mineDifference == 0 and len(setDifference) > 0 and intersection == smallerSet:
          safeSet = setDifference
          dangerousSet = intersection
          hintSteps: list[HintStep] = [
            HintStep("Check out these two cells.", {cell.location, cell2.location}, {}),
            HintStep(f"There {'are' if smallerSetMineCount > 1 else 'is'} {readableNumber(smallerSetMineCount)} remaining mine{'s' if smallerSetMineCount > 1 else ''} in {'these' if len(smallerSet) > 1 else 'this'} cell{'s' if len(smallerSet) > 1 else ''}.", {smallerCell.location}, {c.location for c in intersection}),
            HintStep(f"Therefore, there are no remaining mines in {'these' if len(safeSet) > 1 else 'this'} cell{'s' if len(safeSet) > 1 else ''}.", {biggerCell.location}, {c.location for c in safeSet}),
            HintStep(f"Reveal the safe cell{'s' if len(safeSet) > 1 else ''} unique to this number.", {biggerCell.location}, {c.location for c in safeSet})
          ]
          return Move(cellsToReveal={cell.location for cell in safeSet}, hintSteps=hintSteps)
  return None

def getRemainingMinesFlagMove(board: Board) -> Move:
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
      print("getRemainingMinesFlagMove: Too many cells to analyze")
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
        HintStep(f"There are only {remainingMines} remaining mine{'s' if remainingMines > 1 else ''} left", {}, {cell.location for cell in unrevealedCells}),
        HintStep("This is the only possible configuration", {}, {cell.location for cell in allFlags})
      ]
      return Move(cellsToFlag=allFlags, hintSteps=hintSteps)
  return None

def getRemainingCellRevealsMove(board: Board) -> Move:
  """
  If there are no more mines to flag, this function will reveal the remaining cells.
  Args:
    board (Board): The Minesweeper board.
  Returns:
    RevealCell: The move to reveal the cells, or None if no move is found.
  """
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

def getNextMove(board: Board) -> Move:
  """
  Determines the next move to make on the Minesweeper board.
  Args:
    board (Board): The Minesweeper board.
  Returns:
    Move: The move to make, or None if no move is found.
  """
  order = [
    getExpandCellMove,
    getFlagRemainingNeighbors,
    getIntersectCells,
    getRemainingMinesFlagMove,
    getRemainingCellRevealsMove
  ]
  for moveFunction in order:
    move = moveFunction(board)
    if move:
      return move
  return None