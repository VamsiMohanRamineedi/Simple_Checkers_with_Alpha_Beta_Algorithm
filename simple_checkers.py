import random
from copy import deepcopy

BOARD_SIZE = 6
NUM_OF_PIECES = 6
DEPTH_LIMIT = 10

PLAYERS = ["Black", "White"]

class Checkers:
	def __init__(self, player=0):
		self.board = Board() # creates a board with given board_size and number of black and white pieces
		self.remaining = [NUM_OF_PIECES, NUM_OF_PIECES] # shows the remaining pieces on the board in the order [black,white]
		self.turn = player # maintains the state of player's turn
	def play(self):
		while not (self.gameOver(self.board)):
			self.board.drawBoardState()
			print("Current Player: "+PLAYERS[self.turn])
			# Human's turn
			if (self.turn == 0):
				# get player's move
				legal = self.board.calcLegalMoves(self.turn)
				if (len(legal) > 0):
					move = self.getMove(legal)
					self.makeMove(move)
				else:
					print("No legal moves available, forfeitting your turn...")
			# Computer's turn
			else:
				legal = self.board.calcLegalMoves(self.turn)
				if (len(legal)>0):
					# no need for AI if there's only one choice!
					if (len(legal)==1):
						choice = legal[0]
					else:
						state = AB_State(self.board, self.turn, self.turn)
						choice = self.alpha_beta(state)
					self.makeMove(choice)
					print("Computer chooses ("+str(choice.start)+", "+str(choice.end)+")")
				else:
					print("No legal moves available, forfeitting Computer's turn...")
			# changing player's turn
			self.turn = 1-self.turn
		self.board.drawBoardState()
		print("------------------- Game OVER ---------------------- \n")
		print("Your pieces remained on the board = "+str(self.remaining[0]))
		print("Computer pieces remained on the board = "+str(self.remaining[1]))
		print('\n')
		if (self.remaining[1] > self.remaining[0]):
			print("Computer wins!")
		elif (self.remaining[0] > self.remaining[1]):
			print("You win!")
		else:
			print("It's a draw!")

	def makeMove(self, move):
		self.board.boardMove(move, self.turn)
		if move.jump:
			# decrement removed pieces after jump
			self.remaining[1-self.turn] -= len(move.jumpOver)
			print("Removed "+str(len(move.jumpOver))+" "+PLAYERS[1-self.turn]+" pieces")

	def getMove(self, legal):
		move = -1
		# repeats until player picks move on the list
		while move not in range(len(legal)):
			# List valid moves:
			print("Valid Moves: ")
			print('\n')
			for i in range(len(legal)):
				print(str(i+1)+": ",end='')
				print(str(legal[i].start)+" "+str(legal[i].end))
			print('\n')
			print('The displayed moves are in the form (row, col)')
			usr_input = input("Pick a move: ")
			# stops error caused when user inputs nothing
			move = -1 if (usr_input == '')  else (int(usr_input)-1)
			if move not in range(len(legal)):
				print("Illegal move")
		print("Legal move")
		return (legal[move])

	# returns a boolean value determining if game finished
	def gameOver(self, board):
		# all pieces from one side captured
		if (len(board.currPos[0]) == 0 or len(board.currPos[1]) == 0):
			return True
		# no legal moves available, stalemate
		elif (len(board.calcLegalMoves(0)) == 0 and len(board.calcLegalMoves(1)) == 0):
			return True
		else:
			# continue onwards
			return False

	def utility(self, board):
		''' Returns the utility value for a terminal node'''

		# white wins, return utility value of +1000
		if len(board.currPos[1]) > len(board.currPos[0]):
			return 1000
		# black wins, return utility value of -1000
		elif len(board.currPos[0]) > len(board.currPos[1]):
			return -1000
		# game is a draw
		else:
			return 0

	# state = board, player
	def alpha_beta(self, state):
		result = self.max_value(state, -1000, 1000, 0)
		print("Total nodes generated: "+str(result.nodes))
		print("Max depth: "+str(result.max_depth))
		print("Max Val Cutoffs: "+str(result.max_cutoff))
		print("Min Val Cutoffs: "+str(result.min_cutoff))
		return result.move

	# returns max value and action associated with value
	def max_value(self, state, alpha, beta, node):
		
		# v <- -inf
		# self, move_value, move, max_depth, total_nodes, max_cutoff, min_cutoff
		v = AB_Value(-1000, None, node, 1, 0, 0)

		# if TERMINAL-TEST(state) then return utility(state)
		actions = state.board.calcLegalMoves(state.player)
		num_act = len(actions)

		if (len(actions)==0): 
			v.move_value = self.utility(state.board)
			return v 

		# depth cutoff
		if (node == DEPTH_LIMIT):
			v.move_value = self.evaluation_function(state.board, state.origPlayer)
			#print("Depth Cutoff. Eval value: "+str(v.move_value))
			return v      
		
		for a in actions:
			newState = AB_State(deepcopy(state.board), 1-state.player, state.origPlayer)
			# RESULT(s,a)
			newState.board.boardMove(a, state.player)
			new_v = self.min_value(newState, alpha, beta, node+1)
			# compute new values for nodes and cutoffs in recursion
			if (new_v.max_depth > v.max_depth):
				v.max_depth = new_v.max_depth         
			v.nodes += new_v.nodes
			v.max_cutoff += new_v.max_cutoff
			v.min_cutoff += new_v.min_cutoff
			# v <- Max(v, MIN_VALUE(RESULT(s,a), alpha, beta))
			if (new_v.move_value > v.move_value):
				v.move_value = new_v.move_value
				v.move = a
			if (v.move_value >= beta):
				v.max_cutoff += 1
				return v
			if (v.move_value > alpha):
				alpha = v.move_value
		return v

	# returns min value
	def min_value(self, state, alpha, beta, node):
		# v.move_value <- inf
		# self, move_value, move, max_depth, total_nodes, max_cutoff, min_cutoff
		v = AB_Value(1000, None, node, 1, 0, 0)

		# if TERMINAL-TEST(state) then return utility(state)
		actions = state.board.calcLegalMoves(state.player)
		num_act = len(actions)
		if (len(actions)==0): 
			v.move_value = self.utility(state.board)
			return v 
      
        # depth cutoff
		if (node == DEPTH_LIMIT):
			v.move_value = self.evaluation_function(state.board, state.player)
			#print("Depth Cutoff. Eval value: "+str(v.move_value))
			return v

		for a in actions:
			newState = AB_State(deepcopy(state.board), 1-state.player, state.origPlayer)
			#eval = self.evaluation_function(self.board, self.turn)
         	#print("Current Evaluation: "+str(eval))
			# RESULT(s,a)
			newState.board.boardMove(a, state.player)
			new_v = self.max_value(newState, alpha, beta, node+1)
			# compute new values for nodes and cutoffs in recursion
			if (new_v.max_depth > v.max_depth):
				v.max_depth = new_v.max_depth
			v.nodes += new_v.nodes
			v.max_cutoff += new_v.max_cutoff
			v.min_cutoff += new_v.min_cutoff
			# v <- Min(v, MAX_VALUE(RESULT(s,a), alpha, beta))
			if (new_v.move_value < v.move_value):
				v.move_value = new_v.move_value
				v.move = a
			if (v.move_value <= alpha):
				v.min_cutoff += 1
				return v
			if (v.move_value < beta):
				beta = v.move_value
		return v

	def evaluation_function(self, board, currPlayer):
		''' Returns a utility value for non-terminal node'''
		
		black_at_white_end = 0
		black_at_white_half = 0
		black_at_self_half = 0
		white_at_black_end = 0
		white_at_black_half = 0
		white_at_self_half = 0

		# black's pieces
		for cell in range(len(board.currPos[0])):
			# black pieces at row = 0
			if (board.currPos[0][cell][0] == 0):
				black_at_white_end += 1
			# black pieces in white's half of the board (i.e) in rows 1 and 2
			elif (0 <= board.currPos[0][cell][0] < BOARD_SIZE/2):
				black_at_white_half += 1
			else:
				black_at_self_half += 1
		
		# white's pieces
		for cell in range(len(board.currPos[1])):
			# white pieces at row = 5 
			if (board.currPos[1][cell][0] == BOARD_SIZE - 1):
				white_at_black_end += 1
			# white pieces in black's half of the board (i.e) in rows 3 and 4
			elif (BOARD_SIZE/2 <= board.currPos[1][cell][0] < BOARD_SIZE):
				white_at_black_half += 1
			else:
				white_at_self_half += 1
			
		eval_score = (100*(black_at_white_end - white_at_black_end)) + (50*(black_at_white_half - white_at_black_half)) + (10*(black_at_self_half - white_at_self_half))
		
		if (currPlayer == 1):
			return -eval_score
		else:
			return eval_score     

# wrapper for alpha-beta info
# v = [move_value, move, max tree depth, # child nodes, # max/beta cutoff, # min/alpha cutoff]
class AB_Value:
	def __init__(self, move_value, move, max_depth, child_nodes, max_cutoff, min_cutoff):
		self.move_value = move_value
		self.move = move
		self.max_depth = max_depth
		self.nodes = child_nodes
		self.max_cutoff = max_cutoff
		self.min_cutoff = min_cutoff


# wrapper for state used in alpha-beta
class AB_State:
	def __init__(self, boardState, currPlayer, originalPlayer):
		self.board = boardState
		self.player = currPlayer
		self.origPlayer = originalPlayer

class Move:
	def __init__(self, start, end, jump=False):
		self.start = start
		self.end = end # tuple (row, col)
		self.jump = jump # bool
		self.jumpOver = [] # array of pieces jumped over

class Board:
	def __init__(self, board=[], currBlack=[], currWhite=[]):
		if (board!=[]):
			self.boardState = board     
		else:
			self.setDefaultBoard()
		self.currPos = [[],[]]
		if (currBlack != []):
			self.currPos[0] = currBlack
		else:
			self.currPos[0] = self.calcPos(0)
		if (currWhite != []):
			self.currPos[1] = currWhite
		else:
			self.currPos[1] = self.calcPos(1)            
	def boardMove(self, move_info, currPlayer):
		move = [move_info.start, move_info.end]
		#print(move)
		#self.drawBoardState()
		remove = move_info.jumpOver
		jump = move_info.jump      
		# start by making old space empty
		self.boardState[move[0][0]][move[0][1]] = -1
		# then set the new space to player who moved
		self.boardState[move[1][0]][move[1][1]] = currPlayer
		if jump:
			#remove jumped over enemies
			for enemy in move_info.jumpOver:
				self.boardState[enemy[0]][enemy[1]] = -1
		# update currPos array
		# if its jump, the board could be in many configs, just recalc it
		if jump:
			self.currPos[0] = self.calcPos(0)
			self.currPos[1] = self.calcPos(1)
		# otherwise change is predictable, so faster to just set it
		else:
			self.currPos[currPlayer].remove((move[0][0], move[0][1]))
			self.currPos[currPlayer].append((move[1][0], move[1][1]))
		#print(self.currPos[currPlayer])

	def calcLegalMoves(self, player): # int array  -> [0] reg, [1] jump
		legalMoves = []
		hasJumps = False
		# next goes up if black or down if white
		next = -1 if player == 0 else 1
		boardLimit = 0 if player == 0 else BOARD_SIZE-1
		# cell refers to a position tuple (row, col)
		for cell in self.currPos[player]:
			if (cell[0] == boardLimit):
				continue
			# diagonal right, only search if not at right edge of board
			if (cell[1]!=BOARD_SIZE-1):
				#empty, regular move
				if (self.boardState[cell[0]+next][cell[1]+1]==-1 and not hasJumps):
					temp = Move((cell[0],cell[1]),(cell[0]+next,cell[1]+1)) 
					legalMoves.append(temp)
				# has enemy, can jump it?
				elif(self.boardState[cell[0]+next][cell[1]+1]==1-player):
					jumps = self.checkJump((cell[0],cell[1]), False, player)
					if (len(jumps)!=0):
						# if first jump, clear out regular moves
						if not hasJumps:
							hasJumps = True
							legalMoves = []
						legalMoves.extend(jumps)
			# diagonal left, only search if not at left edge of board
			if (cell[1]!=0):
				if(self.boardState[cell[0]+next][cell[1]-1]==-1 and not hasJumps):
					temp = Move((cell[0],cell[1]),(cell[0]+next,cell[1]-1)) 
					legalMoves.append(temp)                    
				elif(self.boardState[cell[0]+next][cell[1]-1]==1-player):
					jumps = self.checkJump((cell[0],cell[1]), True, player)
					if (len(jumps)!=0):
						if not hasJumps:
							hasJumps = True
							legalMoves = []                        
						legalMoves.extend(jumps)

		return legalMoves

	# enemy is the square we plan to jump over
	# change later to deal with double jumps
	def checkJump(self, cell, isLeft, player):
		jumps = []
		next = -1 if player == 0 else 1
		# check boundaries!
		if (cell[0]+next == 0 or cell[0]+next == BOARD_SIZE-1):
			return jumps
		#check top left
		if (isLeft):
			if (cell[1]>1 and self.boardState[cell[0]+next+next][cell[1]-2]==-1):
				temp = Move(cell, (cell[0]+next+next, cell[1]-2), True)
				temp.jumpOver = [(cell[0]+next,cell[1]-1)]                   			
				jumps.append(temp)
		else:
		#check top right
			if (cell[1]<BOARD_SIZE-2 and self.boardState[cell[0]+next+next][cell[1]+2]==-1):
				# ([original cell, new cell], enemy cell])
				temp = Move(cell, (cell[0]+next+next, cell[1]+2), True)
				temp.jumpOver = [(cell[0]+next,cell[1]+1)]                  			
				jumps.append(temp)                
		return jumps

	def calcPos(self, player):
		pos = []
		#pieces = 0
		for row in range(BOARD_SIZE):
			for col in range(BOARD_SIZE):
				if (self.boardState[row][col]==player):
					pos.append((row,col))
		return pos

	def drawBoardState(self):
		print('\n')
		for colnum in range(BOARD_SIZE):
			print(str(colnum)+" ",end="")
		print("")
		for row in range(BOARD_SIZE):
			for col in range(BOARD_SIZE):
				if (self.boardState[row][col] == -1):
					print("_ ",end='')
				elif (self.boardState[row][col] == 1):
					print("W ",end='')
				elif (self.boardState[row][col] == 0):
					print("B ",end='')
			print(str(row))
		print('\n')

	def setDefaultBoard(self):
		# resets the board
		# -1 = empty, 0=black, 1=white
		self.boardState = [[-1,1,-1,1,-1,1],
			[1,-1,1,-1,1,-1],
			[-1,-1,-1,-1,-1,-1],
			[-1,-1,-1,-1,-1,-1],
			[-1,0,-1,0,-1,0],
			[0,-1,0,-1,0,-1]]

def main():
	print('You are Black. Do you want to move first? Press Y for Yes (or) N for No.')
	first_player = (input("Enter Y or N:"))
	while not (first_player == 'Y' or first_player == 'y' or first_player == 'N' or first_player == 'n'):
		first_player = (input("Please choose from the given choices: "))
	if first_player =='Y' or first_player == 'y':
		player=0
	elif first_player =='N' or first_player == 'n':
		player=1
	checkers = Checkers(player)
	checkers.play()

main()