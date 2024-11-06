

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
  def __init__(self, location: set[tuple[int, int]]):
    """
    Initialize the RevealCell move.
    This is used to reveal a set of cells.
    Args:
      location set[tuple[int, int]]: the set of (x, y) coordinates to reveal.
    """
    self.location = location

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