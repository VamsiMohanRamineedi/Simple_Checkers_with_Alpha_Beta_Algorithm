class Board:

	def __init__(self):
		pass

	def default_board(self):
		# resets the boardstate to initial position
        # -1 = empty, 0=black, 1=white
        self.boardState = [
            [-1,1,-1,1,-1,1],
            [1,-1,1,-1,1,-1],
            [-1,-1,-1,-1,-1,-1],
            [-1,-1,-1,-1,-1,-1],
            [-1,0,-1,0,-1,0],
            [0,-1,0,-1,0,-1]]
       
