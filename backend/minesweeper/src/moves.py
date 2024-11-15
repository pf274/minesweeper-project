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

class Move:
  def __init__(self, *, cellsToReveal: set[tuple[int, int]] = set(), cellsToFlag: set[tuple[int, int]] = set(), cellsToExpand: set[tuple[int, int]] = set(), hintSteps: list[HintStep] = []):
    """
    Initialize the Move.
    This is used to reveal, flag, and expand cells.
    Args:
      cellsToReveal (set[tuple[int, int]]): A set of (x, y) coordinates to reveal.
      cellsToFlag (set[tuple[int, int]]): A set of (x, y) coordinates to flag.
      cellsToExpand (set[tuple[int, int]]): A set of (x, y) coordinates to expand.
      hintSteps (list[HintStep]): A list of hint steps to show the user.
    """
    if len(cellsToReveal) == 0 and len(cellsToFlag) == 0 and len(cellsToExpand) == 0:
      raise ValueError("Move must have at least one of cellsToReveal, cellsToFlag, or cellsToExpand.")
    self.cellsToReveal = cellsToReveal
    self.cellsToFlag = cellsToFlag
    self.cellsToExpand = cellsToExpand
    if any(not isinstance(hintStep, HintStep) for hintStep in hintSteps):
      raise ValueError("All hint steps must be of type HintStep.")
    self.hintSteps = hintSteps
  def toJSON(self):
    """
    Convert the Move object to a JSON-serializable dictionary.
    Returns:
      dict: A dictionary containing the move's attributes.
    """
    return {
      "cellsToReveal": list(self.cellsToReveal),
      "cellsToFlag": list(self.cellsToFlag),
      "cellsToExpand": list(self.cellsToExpand),
      "hintSteps": [step.toJSON() for step in self.hintSteps]
    }