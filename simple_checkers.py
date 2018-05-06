import random
from copy import deepcopy
import numpy as np

BOARD_SIZE = 6
NUM_OF_PIECES = 6
PLAYERS = ["Black", "White"]

class Board:
	def __init__(self, board=[], blackPositions=[], whitePositions=[]):
		if (board==[]):
			self.defaultBoard()     
		else:
			self.boardState = board
		self.currPos = [[],[]]
		self.currPos[1] = whitePositions if (whitePositions != []) else self.calculatePositions(1)
		self.currPos[0] = blackPositions if (blackPositions != []) else self.calculatePositions(0)

	def defaultBoard(self):
		''' Resets the board to initial position '''

		# -1 = empty, 0=black, 1=white
		self.boardState = [[-1,1,-1,1,-1,1],
			[1,-1,1,-1,1,-1],
			[-1,-1,-1,-1,-1,-1],
			[-1,-1,-1,-1,-1,-1],
			[-1,0,-1,0,-1,0],
			[0,-1,0,-1,0,-1]]

	def showBoard(self):
		''' Prints the current positions on the board'''

		print('\n')
		for col in range(BOARD_SIZE):
			print(str(col)+" ",end='')
		print("")
		for row in range(BOARD_SIZE):
			for col in range(BOARD_SIZE):
				if (self.boardState[row][col] == 0):
					print("B ",end='')
				elif (self.boardState[row][col] == -1):
					print("_ ",end='')
				elif (self.boardState[row][col] == 1):
					print("W ",end='')
			print(str(row))
		print('\n')

	def calculatePositions(self, player):
		''' Returns the (row,col) positions as a list of a particular player '''
		playerPositions = []
		for col in range(BOARD_SIZE):
			for row in range(BOARD_SIZE):
				if (self.boardState[row][col]==player):
					playerPositions.append((row,col))
		return playerPositions

	def legalMoves(self, player): 
		''' Returns the legal moves available'''

		hasjumpsAvailable = False
		legalMoves = []
		# since white is in the upper half of the board(rows 0 and 1), their moves have to be towards rows 2,3,4 and 5. Similarly for blacks.
		if player == 1:
			boardEnd = BOARD_SIZE-1
			forwardMoveAdd = 1
		else:
			boardEnd = 0
			forwardMoveAdd = -1

		for square in self.currPos[player]: # square is position(row#, col#) of the piece

			if (square[0] == boardEnd): # pieces cant be moved once they reach opponents end
				continue
			# diagonal left, only search if not at left edge of board
			if (square[1]!=0):
				# regular move
				if(hasjumpsAvailable == False and self.boardState[square[0]+forwardMoveAdd][square[1]-1]==-1):
					temp = Move((square[0],square[1]),(square[0]+forwardMoveAdd,square[1]-1)) 
					legalMoves.append(temp)
				# capture move                    
				elif(self.boardState[square[0]+forwardMoveAdd][square[1]-1]==1-player):
					jumpsAvailable = self.areJumpsAvailable((square[0],square[1]), False, player)
					if (len(jumpsAvailable)>0):
						if hasjumpsAvailable == False: # clearing out regular moves in the first jump
							legalMoves = []          
							hasjumpsAvailable = True
						legalMoves.extend(jumpsAvailable)

			# diagonal right, only search if not at right edge of board
			if (square[1]!=BOARD_SIZE-1):
				# regular move
				if (hasjumpsAvailable == False and self.boardState[square[0]+forwardMoveAdd][square[1]+1]==-1):
					temp = Move((square[0],square[1]),(square[0]+forwardMoveAdd,square[1]+1)) 
					legalMoves.append(temp)
				# capture move
				elif(self.boardState[square[0]+forwardMoveAdd][square[1]+1]==1-player):
					jumpsAvailable = self.areJumpsAvailable((square[0],square[1]), True, player)
					if (len(jumpsAvailable)>0):
						if hasjumpsAvailable == False: # clearing out regular moves in the first jump
							legalMoves = []
							hasjumpsAvailable = True
						legalMoves.extend(jumpsAvailable)
			
		return legalMoves

	def areJumpsAvailable(self, square, isRight, player):
		''' Returns all the available jumps'''

		jumpsAvailable = []
		if player == 1:
			forwardMoveAdd = 1
		else:
			forwardMoveAdd = -1

		# check boundaries!
		if (square[0]+forwardMoveAdd == 0 or square[0]+forwardMoveAdd == BOARD_SIZE-1):
			return jumpsAvailable

		#check top right
		if (isRight):
			if (square[1]<BOARD_SIZE-2 and self.boardState[square[0]+forwardMoveAdd+forwardMoveAdd][square[1]+2]==-1):
				# ([original square, new square], enemy square])
				temp = Move(square, (square[0]+forwardMoveAdd+forwardMoveAdd, square[1]+2), True)
				temp.jumpedOver = [(square[0]+forwardMoveAdd,square[1]+1)]                  			
				jumpsAvailable.append(temp) 
			
		else:
		#check top left
			if (square[1]>1 and self.boardState[square[0]+forwardMoveAdd+forwardMoveAdd][square[1]-2]==-1):
				temp = Move(square, (square[0]+forwardMoveAdd+forwardMoveAdd, square[1]-2), True)
				temp.jumpedOver = [(square[0]+forwardMoveAdd,square[1]-1)]                   			
				jumpsAvailable.append(temp)

		return jumpsAvailable
		            
	def moveFromTo(self, start_end_info, currPlayer):
		''' Moves a piece from one square to other '''
		jump = start_end_info.jump      
		move = [start_end_info.start, start_end_info.end]
		remove = start_end_info.jumpedOver
		
		self.boardState[move[0][0]][move[0][1]] = -1 # emptying the old space
		self.boardState[move[1][0]][move[1][1]] = currPlayer # allot the new space to the player who moved
		if jump:
			for enemy in start_end_info.jumpedOver:
				self.boardState[enemy[0]][enemy[1]] = -1 # remove the pieces that got jumped over
			# calculating the black and white positions since jump can alter many positions
			self.currPos[1] = self.calculatePositions(1)
			self.currPos[0] = self.calculatePositions(0)
		else:
			# otherwise just set the positions according to the changes
			self.currPos[currPlayer].remove((move[0][0], move[0][1]))
			self.currPos[currPlayer].append((move[1][0], move[1][1]))

		return 0

class Checkers:
	def __init__(self, turn=0, difficulty = 1, depth_limit=4):
		self.board = Board() # creates a board with given board_size and number of black and white pieces
		self.turn = turn # maintains the state of player's turn
		self.difficulty = difficulty
		self.leftOnBoard = [NUM_OF_PIECES, NUM_OF_PIECES] # shows the remaining pieces on the board in the order [black,white]
		self.depth_limit = depth_limit
	def play(self):
		while (self.isGameOver(self.board)) == False: # checking if game is still alive
			self.board.showBoard()
			print("Current Player: "+PLAYERS[self.turn])

			# Computer's turn
			if (self.turn == 1):
				legal = self.board.legalMoves(self.turn) # calculate legal moves
				if (len(legal) == 0):
					print("No legal moves available, forfeitting Computer's turn")
				elif (len(legal)>0):
					if (len(legal)==1): # if only 1 legal move is available, it has to be picked for sure.
						choice = legal[0]
					else:
						state = AB_Board_Player(self.board, self.turn, self.turn)
						choice = self.alpha_beta_search(state)
					self.makeAMove(choice)
					print("Computer chooses ("+str(choice.start)+", "+str(choice.end)+")")

			# Human's turn
			else:
				# calculate legal moves
				legal = self.board.legalMoves(self.turn)
				if (len(legal) == 0):
					print("No legal moves available, forfeitting your turn")
				else:
					move = self.pickAMove(legal)
					self.makeAMove(move)
					
			# changing player's turn
			if self.turn == 0:
				self.turn = 1
			else:
				self.turn = 0
		self.board.showBoard()
		print("------------------- Game OVER ---------------------- \n")
		print("Your pieces remained on the board = "+str(self.leftOnBoard[0]))
		print("Computer pieces remained on the board = "+str(self.leftOnBoard[1]))
		print('\n')
		if (self.leftOnBoard[1] > self.leftOnBoard[0]):
			print("Computer wins!")
		elif (self.leftOnBoard[0] > self.leftOnBoard[1]):
			print("You win! \n")
		else:
			print("It's a draw!")

	def makeAMove(self, move):
		self.board.moveFromTo(move, self.turn)
		if move.jump:
			self.leftOnBoard[1-self.turn] -= len(move.jumpedOver) # decrease pieces leftOnBoard counter after removing a piece
			print("Removed "+str(len(move.jumpedOver))+" "+PLAYERS[1-self.turn]+" pieces")

	def pickAMove(self, legal):
		'''Returns a move picked by the player'''
		pick = -1
		while pick not in range(len(legal)): # repeats until player picks move on the list
			print("Legal moves available: ")
			print('\n')
			for i in range(0,len(legal)):
				print(str(i+1)+": ",end='')
				print(str(legal[i].start)+" "+str(legal[i].end))
			print('\n')
			print('The displayed moves are in the form (row#, col#)')
			selectedMove = input("Pick a move: ")
			if (selectedMove == ''): 
				pick = -1 
			else:
				pick = (int(selectedMove)-1)
			if pick not in range(0,len(legal)):
				print("Invalid move selected. Choose from the available moves")
		return (legal[pick])

	def isGameOver(self, board):
		'''Returns True if all pieces of a player are captured or if there are no legal moves available'''

		countOfBlacks = len(board.currPos[0])
		countOfWhites = len(board.currPos[1])

		if (countOfWhites == 0 or countOfBlacks == 0): # All pieces of any player captured
			return True
		elif (len(board.legalMoves(1)) == 0 and len(board.legalMoves(0)) == 0): # No legal moves available
			return True
		else:
			return False

	def utility(self, board):
		''' Returns the utility value for a terminal node'''

		countOfBlacks = len(board.currPos[0])
		countOfWhites = len(board.currPos[1])
		
		# white wins, return utility value of +1000
		if countOfWhites > countOfBlacks:
			return 1000
		# black wins, return utility value of -1000
		elif countOfBlacks > countOfWhites:
			return -1000
		# game is a draw
		else:
			return 0

	def alpha_beta_search(self, state):
		''' Returns the best action'''

		outputOfAction = self.max_value(state, -1000, 1000, 0)
		print("Max depth: "+str(outputOfAction.max_depth))
		print("Total nodes generated: "+str(outputOfAction.nodes))
		print("#Pruning in minvalue function: "+str(outputOfAction.min_cutoff))
		print("#Pruning in maxvalue function: "+str(outputOfAction.max_cutoff))
		return outputOfAction.action

	def max_value(self, state, alpha, beta, node):
		''' Returns the object of AB_Properties class having maximum value(v) and the associated action(action)'''

		# v <- -inf
		# self, v, action, max_depth, total_nodes, max_cutoff, min_cutoff
		ab = AB_Properties(-1000, None, node, 1, 0, 0)

		# if TERMINAL-TEST(state) then return utility(state)
		actions = state.board.legalMoves(state.player)
		num_act = len(actions)

		if (num_act==0): 
			ab.v = self.utility(state.board)
			return ab

		# depth cutoff
		if (node == self.depth_limit):
			ab.v = self.evaluation_function(state.board, state.origPlayer)
			return ab    
		
		for a in actions:
			newState = AB_Board_Player(deepcopy(state.board), 1-state.player, state.origPlayer)
			# RESULT(s,a)
			newState.board.moveFromTo(a, state.player)
			new_ab = self.min_value(newState, alpha, beta, node+1)
			# compute new values for nodes and cutoffs in recursion
			ab.max_depth = max(new_ab.max_depth, ab.max_depth)        
			ab.min_cutoff += new_ab.min_cutoff
			ab.max_cutoff += new_ab.max_cutoff
			ab.nodes += new_ab.nodes
			# v <- Max(v, MIN_VALUE(outputOfAction(s,a), alpha, beta))
			if (new_ab.v > ab.v):
				ab.v = new_ab.v
				ab.action = a
			if (ab.v >= beta):
				ab.max_cutoff += 1
				return ab
			alpha = max(ab.v, alpha)
		if ab.action == None:
			ab.action = np.random.choice(actions)
		return ab

	# returns min value
	def min_value(self, state, alpha, beta, node):
		''' Returns the object of AB_Properties class having minimum value(v) and the associated action(action)'''

		# v.move_value <- inf
		# self, v, action, max_depth, total_nodes, max_cutoff, min_cutoff
		ab = AB_Properties(1000, None, node, 1, 0, 0)

		# if TERMINAL-TEST(state) then return utility(state)
		actions = state.board.legalMoves(state.player)
		num_act = len(actions)
		if (num_act==0): 
			ab.v = self.utility(state.board)
			return ab 
      
        # depth cutoff
		if (node == self.depth_limit):
			ab.v = self.evaluation_function(state.board, state.player)
			return ab

		for a in actions:
			newState = AB_Board_Player(deepcopy(state.board), 1-state.player, state.origPlayer)
			# RESULT(s,a)
			newState.board.moveFromTo(a, state.player)
			new_ab = self.max_value(newState, alpha, beta, node+1)
			# compute new values for nodes and cutoffs in recursion
			ab.nodes += new_ab.nodes
			ab.max_depth = max(new_ab.max_depth, ab.max_depth)
			ab.max_cutoff += new_ab.max_cutoff
			ab.min_cutoff += new_ab.min_cutoff
			# v <- Min(v, MAX_VALUE(outputOfAction(s,a), alpha, beta))
			if (new_ab.v < ab.v):
				ab.v = new_ab.v
				ab.action = a
			if (ab.v <= alpha):
				ab.min_cutoff += 1
				return ab
			beta = min(ab.v, beta)
		if ab.action == None:
			ab.action = np.random.choice(actions) 
		return ab

	def evaluation_function(self, board, currPlayer):
		''' Returns a utility value for non-terminal node'''

		black_at_white_end = 0
		black_at_white_half = 0
		black_at_self_half = 0
		white_at_black_end = 0
		white_at_black_half = 0
		white_at_self_half = 0

		# black's pieces
		for square in range(len(board.currPos[0])):
			# black pieces at row = 0
			if (board.currPos[0][square][0] == 0):
				black_at_white_end += 1
			# black pieces in white's half of the board (i.e) in rows 1 and 2
			elif (0 <= board.currPos[0][square][0] < BOARD_SIZE/2):
				black_at_white_half += 1
			else:
				black_at_self_half += 1
		
		# white's pieces
		for square in range(len(board.currPos[1])):
			# white pieces at row = 5 
			if (board.currPos[1][square][0] == BOARD_SIZE-1):
				white_at_black_end += 1
			# white pieces in black's half of the board (i.e) in rows 3 and 4
			elif (BOARD_SIZE/2 <= board.currPos[1][square][0] < BOARD_SIZE):
				white_at_black_half += 1
			else:
				white_at_self_half += 1
			
		eval_score = (70*(black_at_white_end - white_at_black_end)) + (50*(black_at_white_half - white_at_black_half)) + (30*(black_at_self_half - white_at_self_half))
		random_score = random.randint(-500, 500)
		my_list = [eval_score, random_score]
		np_my_list = np.array(my_list)
		#print('random_score = '+str(random_score))

		if (self.difficulty == 1):
			random_eval_score = np.random.choice(np_my_list,p=[0,1])
			#print('Score = ',random_eval_score)
			return random_eval_score

		elif (self.difficulty == 2):
			random_eval_score = np.random.choice(np_my_list, p=[0.5,0.5])
			if (currPlayer == 0):
				#print('Score = ',random_eval_score)
				return random_eval_score
			else:
				#print('Score = ',-random_eval_score)
				return -random_eval_score

		else:
			random_eval_score = np.random.choice(np_my_list, p=[1,0])
			if (currPlayer == 0):
				#print('Score = ',random_eval_score)
				return random_eval_score
			else:
				#print('Score = ',-random_eval_score)
				return -random_eval_score    

class AB_Properties:
	''' Maintains the alpha beta related properties'''

	def __init__(self, v, action, max_depth, child_nodes, max_cutoff, min_cutoff):
		self.action = action
		self.max_depth = max_depth
		self.max_cutoff = max_cutoff
		self.min_cutoff = min_cutoff
		self.nodes = child_nodes
		self.v = v


class AB_Board_Player:
	''' Wrapper for state used in alpha-beta'''
	def __init__(self, boardState, currPlayer, originalPlayer):
		self.board = boardState
		self.origPlayer = originalPlayer
		self.player = currPlayer

class Move:
	''' Maintains the start, end squares of each move'''
	def __init__(self, start_square, end_square, jump=False):
		self.jumpedOver = [] # array of pieces jumped over
		self.jump = jump # True or False
		self.start = start_square # (row,col) tuple of square
		self.end = end_square # (row,col) tuple of square
		

def main():
	#Select difficulty
	print('Select Difficulty Level: For Easy mode, press 1. For Normal mode, press 2. For Hard mode, press 3.')
	difficulty = int(input('Enter 1, 2 or 3: '))
	while not(difficulty == 1 or difficulty == 2 or difficulty == 3):
		difficulty = int(input("Please choose from the given choices: "))
	if difficulty == 1:
		depth_limit = 4
	elif difficulty == 2:
		depth_limit = 10
	else:
		depth_limit = 13

	#Select if you want to move first or second
	print('You are Black. Do you want to move first? Press Y for Yes (or) N for No.')
	first_player = (input("Enter Y or N:"))
	while not (first_player == 'Y' or first_player == 'y' or first_player == 'N' or first_player == 'n'):
		first_player = (input("Please choose from the given choices: "))
	if first_player =='Y' or first_player == 'y':
		player=0
	elif first_player =='N' or first_player == 'n':
		player=1
	checkers = Checkers(player, difficulty, depth_limit)
	checkers.play()

main()