import pygame as pg, sys
from pygame.locals import *
from random import choice

# Color definitions (RGB).
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
SEA_GREEN = (46, 139, 87)

# Window resolution.
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 300

# Primary display surface.
DISPLAY_SURF = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# Display parameters.
LINE_THICKNESS = 10
PADDLE_HEIGHT = 50
PADDLE_WIDTH = LINE_THICKNESS
PADDLE_OFFSET = 20

# Frames per second.
FPS_CLOCK = pg.time.Clock()
FPS = 40

# Game speeds.
# AI_DELAY retards the AI return speed.
SPEED = 5
AI_DELAY = 0.35

# Font information.
FONT_SIZE = 20

# Sound library.
global _sounds
_sounds = {}


class Game():
	"""Main game class.
	"""
	def __init__(self, line_thickness=LINE_THICKNESS, speed=SPEED):
		"""Creates a new instance of the game.

		:param line_thickness:	Defines the thickness of the borders, ball, and paddles
		:param speed: 			Defines the base speed at which the ball and paddles move
		"""
		self.line_thickness = line_thickness
		self.speed = speed
		self.score_1 = 0
		self.score_2 = 0

		# Initiate variables and set starting positions.
		# Any future changes are made within the Rectangle parameters.

		# Ball.
		ball_pos_x = (WINDOW_WIDTH - LINE_THICKNESS) / 2
		ball_pos_y = (WINDOW_HEIGHT - LINE_THICKNESS) / 2
		self.ball = Ball(ball_pos_x, ball_pos_y, self.line_thickness, self.line_thickness, self.speed)
		
		# Paddles.
		self.paddles = {}
		p1_pos_x = PADDLE_OFFSET
		p2_pos_x = WINDOW_WIDTH - (LINE_THICKNESS + PADDLE_OFFSET)
		self.paddles['user'] = Paddle(p1_pos_x, PADDLE_WIDTH, PADDLE_HEIGHT)
		self.paddles['computer'] = AIPaddle(p2_pos_x, PADDLE_WIDTH, PADDLE_HEIGHT, self.ball, self.speed)

		# Scoreboards.
		self.scoreboard_1 = Scoreboard(150, 50)
		self.scoreboard_2 = Scoreboard(WINDOW_WIDTH - 150, 50)

	def draw_board(self):
		"""Draws the board."""
		# Color the playing field.
		DISPLAY_SURF.fill(SEA_GREEN)
		# Draws the outline of the board.
		pg.draw.rect(DISPLAY_SURF, WHITE, ((0,0),(WINDOW_WIDTH, WINDOW_HEIGHT)), self.line_thickness*2)
		# Draws the center line.
		pg.draw.line(DISPLAY_SURF, WHITE, (WINDOW_WIDTH/2,0), (WINDOW_WIDTH/2,WINDOW_HEIGHT),self.line_thickness//4)

	def update(self):
		"""'Refreshes' the game periodically based on the pre-defined framerate."""
		self.ball.move()
		self.paddles['computer'].move()

		# Check if the ball collided with Paddle 2.
		if self.ball.hit_paddle(self.paddles['computer']):
			self.ball.bounce('x')
		# Check if the ball collided with Paddle 1.
		elif self.ball.hit_paddle(self.paddles['user']):			
			self.ball.bounce('x')
		# Check if a point has been scored.
		if self.ball.cross_p2_wall():
			_sounds['score'].play()			
			self.score_1 += 1
			self.reset_board(1)
		elif self.ball.cross_p1_wall():
			_sounds['score'].play()			
			self.score_2 += 1
			self.reset_board(2)

		# Render all graphical elements in their updated states.
		self.draw_board()
		self.ball.draw()
		self.paddles['user'].draw(BLUE)
		self.paddles['computer'].draw(RED)
		self.scoreboard_1.display(self.score_1)
		self.scoreboard_2.display(self.score_2)

	def reset_board(self, n):
		"""Resets the board for the next volley after a point has been scored."""
		if n == 1:
			self.ball.transpose_to_center()
			self.ball.dx = 1
			self.ball.dy = choice([-1,1])
		elif n == 2:
			self.ball.transpose_to_center()
			self.ball.dx = -1
			self.ball.dy = choice([-1,1])


class Paddle(pg.sprite.Sprite):
	"""The Paddle is represented as a Rectangle with sprite behavior and that is controlled by the mouse."""

	def __init__(self, x, w, h):
		"""Creates a new Paddle object.

		:param x:	x-coordinate of the center of the Paddle
		:param w:	Width of the Paddle
		:param h:	Height ...
		"""
		self.x = x
		self.width = w
		self.height = h
		self.y = (WINDOW_HEIGHT - self.height) / 2
		# Create a Rectangle for the Paddle.
		self.rect = pg.Rect(self.x, self.y, self.width, self.height)

	def draw(self, color):
		"""Draws the paddle."""
		# Prevents the paddle from moving too low (below the lower boundary of the window).
		if self.rect.bottom > (WINDOW_HEIGHT - self.width):
			self.rect.bottom = WINDOW_HEIGHT - self.width
		# Prevents the paddle from moving too high (above the upper boundary of the window).
		elif self.rect.top < self.width:
			self.rect.top = self.width
		# Draws the paddle.
		pg.draw.rect(DISPLAY_SURF, color, self.rect)

	def move(self, pos):
		"""Moves the paddle."""
		self.rect.y = pos[1]


class AIPaddle(Paddle):
	"""The computer-controlled paddle moves in response to the Ball's movement and with user-defined handicaps."""

	def __init__(self, x, w, h, ball, speed):
		"""Creates a new computer-controlled Paddle object.

		:param ball: 	Gives the paddle an attribute that mirrors the actual Ball object's state
		:param speed:	The speed at which the paddle moves (tweak to change 'difficulty')
		"""
		super().__init__(x, w, h)
		self.ball = ball
		self.speed = speed

	def move(self):
		"""Moves the paddle in response to the movement of the ball."""
		# If the ball is moving away from the paddle, center the paddle.
		if self.ball.dx == -1:
			if self.rect.centery < (WINDOW_HEIGHT / 2):
				self.rect.y += (self.speed * AI_DELAY)
			elif self.rect.centery > (WINDOW_HEIGHT / 2):
				self.rect.y -= (self.speed * AI_DELAY)
		# Else, track the ball's movement.
		elif self.ball.dx == 1:
			if self.rect.centery < self.ball.rect.centery:
				self.rect.y += self.speed
			else:
				self.rect.y -= self.speed
		

class Ball(pg.sprite.Sprite):
	"""The Ball is represented as a Rectangle with sprite behavior."""

	def __init__(self, x, y, w, h, speed):
		"""Creates a new Ball object.

		:param x:		x-coordinate of the center of the ball
		:param y:		y-coordinate ...
		:param w:		Width of the ball
		:param h:		Height ...
		:param speed:	Speed ...
		"""
		self.x = x
		self.y = y
		self.width = w
		self.height = h
		self.speed = speed
		# Initial direction is chosen at random.
		self.dx = choice([-1, 1])	# -1 is left, +1 is right.
		self.dy = choice([-1, 1])	# -1 is down, +1 is up.
		# Cast the Ball as a Rectangle.
		self.rect = pg.Rect(self.x, self.y, self.width, self.height)

	def draw(self):
		"""Draws the ball."""
		pg.draw.rect(DISPLAY_SURF, YELLOW, self.rect)

	def move(self):
		"""Moves the ball."""
		self.rect.x += (self.dx * self.speed)
		self.rect.y += (self.dy * self.speed)

		# Checks for collisions with the edges.
		if self.hit_edge():
			self.bounce('y')

	def bounce(self, axis):
		"""Reverses the ball's direction upon collision."""
		if axis == 'x':
			_sounds['hit'].play()			
			self.dx = -self.dx
		elif axis == 'y':
			_sounds['bounce'].play()			
			self.dy = -self.dy

	def hit_paddle(self, paddle):
		"""Checks if the ball has collided with the paddle."""
		if pg.sprite.collide_rect(self, paddle):
			return True
		else:
			return False
		
	def hit_edge(self):
		"""Checks if the ball has collided with a wall."""
		if (self.rect.top <= LINE_THICKNESS) or (self.rect.bottom >= (WINDOW_HEIGHT - LINE_THICKNESS)):
			return True
		else:
			return False

	def cross_p1_wall(self):
		"""Checks if the ball has crossed the left wall, thereby scoring a point for the computer."""
		if self.rect.right == 0:
			return True
		else:
			return False

	def cross_p2_wall(self):
		"""Checks if the ball has crossed the right wall, thereby scoring a point for the user."""
		if self.rect.left == WINDOW_WIDTH:
			return True
		else:
			return False

	def transpose_to_center(self):
		"""Moves the ball back to the center of the board."""
		self.rect.x = (WINDOW_WIDTH - LINE_THICKNESS) / 2
		self.rect.y = (WINDOW_HEIGHT - LINE_THICKNESS) / 2
		self.draw()
		pg.time.delay(350)


class Scoreboard():
	"""Scoreboard banner display."""

	def __init__(self, x, y, score=0, font_size=FONT_SIZE):
		"""Creates a new Scoreboard object.

		:param score:		Running score to be printed and continuously displayed
		:param x:			x-coordinate of the center of the scoreboard surface
		:param y:			y-coordinate ...
		:param font_size:	Size of the printed score
		"""
		self.score = score
		self.x = x
		self.y = y
		self.font = pg.font.Font('freesansbold.ttf', FONT_SIZE)

	def display(self, score):
		"""Displays the current score on the screen."""
		self.score = score
		RESULT_SURF = self.font.render('%s' %(self.score), True, BLACK)
		result_rect = RESULT_SURF.get_rect()
		result_rect.center = (self.x, self.y)
		DISPLAY_SURF.blit(RESULT_SURF, result_rect)
		

def main():
	pg.init()						# Initialize Pygame
	pg.mixer.init()					# Initialize sounds
	pg.display.set_caption('Pong') 	# Name the game window
	pg.mouse.set_visible(0) 		# Make the cursor invisible

	# Create sound library.
	_sounds['hit'] = pg.mixer.Sound("sounds/pong_hit.ogg")
	_sounds['bounce'] = pg.mixer.Sound("sounds/pong_bounce.ogg")
	_sounds['score'] = pg.mixer.Sound("sounds/pong_score.ogg")

	game = Game()

	# Main game loop. Runs until the client quits manually.
	while True:
		for event in pg.event.get():
			if event.type == QUIT:
				pg.quit()
				pg.mixer.quit()
				sys.exit()
			# Mouse movement control.
			elif event.type == MOUSEMOTION:
				game.paddles['user'].move(event.pos)

		game.update()
		pg.display.update()
		FPS_CLOCK.tick(FPS)

if __name__ == '__main__':
	main()