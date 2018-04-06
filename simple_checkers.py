class Board:

	def __init__(self):
		# sets the boardstate to starting condition
        # -1 = empty, 0=black, 1=white
		self.boardState = [[-1,1,-1,1,-1,1],
            [1,-1,1,-1,1,-1],
            [-1,-1,-1,-1,-1,-1],
            [-1,-1,-1,-1,-1,-1],
            [-1,0,-1,0,-1,0],
            [0,-1,0,-1,0,-1]]

b = Board()
print(b.boardState[5][1])

        


       
