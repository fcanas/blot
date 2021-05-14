import board
import digitalio
import time
from enum import Enum

#               ╔═══╗
#    ┌──┐   -α  ║ A ║
#   τ│  │   ┌──▶╚═══╝    τ     ┌───┐
#    │  │   │        ┌─────────│ca │─────────┐
#    └─▶┌───┐        │         └───┘         │
#       │ α │◀───────┘         ▲   │         │
#       └───┘╲                 │   │       -α│
#       ▲     ╲               -β   +β        │
#       │+α    ╲─────+β─────╲  │   │         ▼
#       │                    ╲ │   ▼         ╔═══╗
#  ┌──┏━━━┓                   ▼┌───┐───-αβ──▶║ C ║
# τ│  ┃ ω ┃─────+αβ───────────▶│ c │───┐     ╚═══╝
#  └─▶┗━━━┛                   ▲└───┘◀──┘τ    ▲
#       │                    ╱ │   ▲         │
#       │+β    ╱─────+α─────╱  │   │         │
#       ▼     ╱               -α   +α      -β│
#       ┌───┐╱                 │   │         │
#       │ β │◀───────┐         ▼   │         │
#    ┌─▶└───┘        │         ┌───┐         │
#    │  │   │        └─────────│cb │─────────┘
#   τ│  │   └──▶╔═══╗    τ     └───┘
#    └──┘   -β  ║ B ║
#               ╚═══╝

class ButtonState(Enum):
	OMEGA = 1
	ALPHA = 2
	A_ACCEPT = 4
	BETA  = 3
	B_ACCEPT = 5
	CA = 6
	C = 7
	CB = 8
	C_ACCEPT = 9

class ButtonInput:
	def __init__(self, aAction, bAction, abAction):
		self.active = False
		self.aAction = aAction
		self.bAction = bAction
		self.abAction = abAction
		
		self.buttonA = digitalio.DigitalInOut(board.D23)
		self.buttonB = digitalio.DigitalInOut(board.D24)
		
		self.buttonState = ButtonState.OMEGA
		self.lastState = ButtonState.OMEGA
		self.captureTime = None
		
		# with both buttons pressed, letting go of one, you have tau seconds to let go of
		# the second in order to count as having "pressed" both buttons at the same time.
		self.tau = 0.5
	
	def poll(self):
		
		a = not self.buttonA.value
		b = not self.buttonB.value
		
		def omega(a,b):
			if a and b:
				self.buttonState = ButtonState.C
			elif a:
				self.buttonState = ButtonState.ALPHA
			elif b:
				self.buttonState = ButtonState.BETA
		
		def alpha(a,b):
			self.captureTime = None
			if a and b:
				self.buttonState = ButtonState.C
				return
			elif not a:
				self.buttonState = ButtonState.A_ACCEPT
		
		def a_accept(a,b):
			self.aAction()
			self.buttonState = ButtonState.OMEGA
		
		def beta(a,b):
			self.captureTime = None
			if a and b:
				self.buttonState = ButtonState.C
				return
			elif not b:
				self.buttonState = ButtonState.B_ACCEPT
		
		def b_accept(a,b):
			self.bAction()
			self.buttonState = ButtonState.OMEGA
		
		def ca(a,b):
			if self.captureTime is None:
				# first transition into ca
				self.captureTime = time.time()
				return
			elif (time.time() - self.captureTime) > self.tau:
				self.buttonState = ButtonState.ALPHA
			elif not a:
				self.buttonState = ButtonState.C_ACCEPT
		
		def c(a,b):
			self.captureTime = None
			if not a and not b:
				self.buttonState = ButtonState.C_ACCEPT
			elif not a:
				self.buttonState = ButtonState.CB
			elif not b:
				self.buttonState = ButtonState.CA
		
		def cb(a,b):
			if self.captureTime is None:
				# first transition into cb
				self.captureTime = time.time()
				return
			elif (time.time() - self.captureTime) > self.tau:
				self.buttonState = ButtonState.BETA
			elif not b:
				self.buttonState = ButtonState.C_ACCEPT
				
				
		def c_accept(a,b):
			self.captureTime = None
			self.abAction()
			self.buttonState = ButtonState.OMEGA
			
		# TODO : make functions for each of these
		transitions = {
			ButtonState.OMEGA	 : omega,
			ButtonState.ALPHA 	 : alpha,
			ButtonState.A_ACCEPT : a_accept,
			ButtonState.BETA 	 : beta,
			ButtonState.B_ACCEPT : b_accept,
			ButtonState.CA		 : ca,
			ButtonState.C		 : c,
			ButtonState.CB		 : cb,
			ButtonState.C_ACCEPT : c_accept
		}
		
		transitions[self.buttonState](a,b)
