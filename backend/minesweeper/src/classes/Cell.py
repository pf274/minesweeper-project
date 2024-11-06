class Cell:
  def __init__(self, isMine: bool, isVisible: bool, isFlagged: bool, location: tuple[int, int]):
    """
    Initializes a Cell object.
    Args:
      isMine (bool): Indicates if the cell contains a mine.
      isVisible (bool): Indicates if the cell is visible to the player.
      isFlagged (bool): Indicates if the cell is flagged by the player.
      location (tuple[int, int]): The (x, y) location of the cell on the board.
    """
    self.isMine = isMine
    self.isVisible = isVisible
    self.isFlagged = isFlagged
    self.location = location

  def toJSON(self):
    """
    Convert the Cell object to a JSON-serializable dictionary.
    Returns:
      dict: A dictionary containing the cell's attributes:
        - isMine (bool): Whether the cell contains a mine.
        - isVisible (bool): Whether the cell is visible.
        - isFlagged (bool): Whether the cell is flagged.
        - location (tuple): The (row, column) location of the cell.
    """
    return {
      "isMine": self.isMine,
      "isVisible": self.isVisible,
      "isFlagged": self.isFlagged,
      "location": self.location
    }
