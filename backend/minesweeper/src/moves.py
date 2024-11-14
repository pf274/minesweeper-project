

class Move:
  def __init__(self):
      pass
  def toJSON(self):
    """
    Convert the Move object to a JSON-serializable dictionary.
    Returns:
      dict: A dictionary containing the move's attributes.
    """
    return self.__dict__

class FlagRemainingNeighbors(Move):
  def __init__(self, location: tuple[int, int], flagLocations: set[tuple[int, int]]):
    """
    Initialize the FlagRemainingNeighbors move.
    This is used to flag the unrevealed neighbors of a cell.
    Args:
      location (tuple[int, int]): The (x, y) coordinates of the cells whose neighbors are to be flagged.
      flags (set[tuple[int, int]]): A set of (x, y) coordinates of the neighbors to flag.
    """
    self.location = location
    self.flags = flagLocations

class RevealCells(Move):
  def __init__(self, location: tuple[int, int], neighborsToReveal: set[tuple[int, int]]):
    """
    Initialize the RevealCell move.
    This is used to reveal a set of cells.
    Args:
      location (tuple[int, int]): The (x, y) coordinates of the cell used in this deduction.
      neighborsToReveal set[tuple[int, int]]: the set of (x, y) coordinates to reveal.
    """
    self.location = location
    self.neighborsToReveal = neighborsToReveal

class ExpandCell(Move):
  def __init__(self, expandLocation: tuple[int, int]):
    """
    Initialize the ExpandCell move.
    This is used to expand a cell.
    Args:
      expandLocation (tuple[int, int]): The (x, y) coordinates to expand.
    """
    self.expand = expandLocation

class FlagCells(Move):
  def __init__(self, flags: set[tuple[int, int]]):
    """
    Initialize the FlagCells move.
    This is used to flag a set of cells.
    Args:
      flags (set[tuple[int, int]]): A set of (x, y) coordinates to flag.
    """
    self.flags = flags

class IntersectCells(Move):
  def __init__(self, *, locationA: tuple[int, int], locationB: tuple[int, int], sharedCells: set[tuple[int, int]], minesInSharedCells: int, safeCells: set[tuple[int, int]], unsafeCells: set[tuple[int, int]]):
    """
    Initialize the IntersectCells move.
    This is used to flag cells that are shared between two cells.
    Args:
      locationA (tuple[int, int]): The (x, y) coordinates of the first cell.
      locationB (tuple[int, int]): The (x, y) coordinates of the second cell.
      sharedCells (set[tuple[int, int]]): The (x, y) coordinates of the cells shared between the two cells.
      minesInSharedCells (int): The number of mines in the shared cells.
      unsharedCellsA (set[tuple[int, int]]): The (x, y) coordinates of the cells unique to the first cell.
      unsharedCellsB (set[tuple[int, int]]): The (x, y) coordinates of the cells unique to the second cell.
    """
    self.locationA = locationA
    self.locationB = locationB
    self.sharedCells = sharedCells
    self.minesInSharedCells = minesInSharedCells
    self.safeCells = safeCells
    self.unsafeCells = unsafeCells

class HintStep:
  def __init__(self, text: str, revealedCellsToHighlight: set[tuple[int, int]], hiddenCellsToHighlight: set[tuple[int, int]]):
    """
    Initialize the HintStep.
    This is used to show the user a hint.
    Args:
      text (str): The text of the hint.
      revealedCellsToHighlight (set[tuple[int, int]]): A set of (x, y) coordinates to highlight.
      hiddenCellsToHighlight (set[tuple[int, int]]): A set of (x, y) coordinates to highlight.
    """
    self.text = text
    self.revealedCellsToHighlight = revealedCellsToHighlight
    self.hiddenCellsToHighlight = hiddenCellsToHighlight
  def toJSON(self):
    """
    Convert the HintStep object to a JSON-serializable dictionary.
    Returns:
      dict: A dictionary containing the hint step's attributes.
    """
    return self.__dict__

class GeneralMove:
  def __init__(self, *, cellsToReveal: set[tuple[int, int]] = set(), cellsToFlag: set[tuple[int, int]] = set(), cellsToExpand: set[tuple[int, int]] = set(), hintSteps: list[HintStep] = []):
    """
    Initialize the GeneralMove.
    This is used to reveal, flag, and expand cells.
    Args:
      cellsToReveal (set[tuple[int, int]]): A set of (x, y) coordinates to reveal.
      cellsToFlag (set[tuple[int, int]]): A set of (x, y) coordinates to flag.
      cellsToExpand (set[tuple[int, int]]): A set of (x, y) coordinates to expand.
      hintSteps (list[HintStep]): A list of hint steps to show the user.
    """
    if len(cellsToReveal) == 0 and len(cellsToFlag) == 0 and len(cellsToExpand) == 0:
      raise ValueError("GeneralMove must have at least one of cellsToReveal, cellsToFlag, or cellsToExpand.")
    # if len(hintSteps) == 0:
    #   raise ValueError("GeneralMove must have at least one hint step.")
    self.cellsToReveal = cellsToReveal
    self.cellsToFlag = cellsToFlag
    self.cellsToExpand = cellsToExpand
    if any(not isinstance(hintStep, HintStep) for hintStep in hintSteps):
      raise ValueError("All hint steps must be of type HintStep.")
    self.hintSteps = hintSteps
  def toJSON(self):
    """
    Convert the GeneralMove object to a JSON-serializable dictionary.
    Returns:
      dict: A dictionary containing the move's attributes.
    """
    return {
      "cellsToReveal": list(self.cellsToReveal),
      "cellsToFlag": list(self.cellsToFlag),
      "cellsToExpand": list(self.cellsToExpand),
      "hintSteps": [step.toJSON() for step in self.hintSteps]
    }