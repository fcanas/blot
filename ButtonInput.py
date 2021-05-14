import board
import digitalio
import time
from enum import Enum

# This file handles input on two "button" states as read from digital IO pins
# and detects three possible "gestures":
#
# 1. First Button Pressed
# 2. Second Button Pressed
# 3. Both Buttons Pressed Together
#
# Handling cases 1 and 2 are trivial with a fast enough polling interval.
# Case 3 proves problematic because the two buttons are unlikely to be
# pressed within the same polling interval when it's fast, and the
# interactivity experience suffers for all cases when input polling is
# slow. So we have to carefully manage expectations of button interaction.
#
# The first thing to note is that the action is committed / detected / 
# accepted when the button(s) for the gesture become un-pressed. The 
# second is that the first and second button may become depressed on two
# separate poll passes, but within some interval τ, they should be treated
# as if they were pressed together.
#
# While both buttons are pressed, the two may become unpressed in separate
# polling passes. Within a time interval τ, this should be treated as if
# they were released together. 
#
# The opportunity exists to encode more "gestures" taking advantage of the
# aforementioned timeouts and combinations of presses and holds. This
# system instead allows for any state with any button down to be carefully
# converted into any other gesture. The only thing you can't do is cancel
# all possible actions. In that way, the interface is as as forgiving of
# mistakes in input as I could make it.
#
# These requirements are modeled as a state machine:
#
#  -==[ Meaningful States ]==-
#
#   ω  →  empty state. No buttons pressed
#  [A] →  Accepted A state: "first button pressed"
#  [B] →  Accepted B state: "second button pressed"
#  [C] →  Accepted C state: "first button and second buttons pressed together"
#
#     Other states can be described, but don't necessarily have short,
#     intuitive labels.
#
#  -==[    Transitions    ]==-
#
#  +α  →  first button pressed
#  +β  →  second button pressed
#   τ  →  timeout elapses - Check `ca` and `cb` states: time elapse is 
#		  evaluated before checking for +/-:α/β. The order isn't
#		  critical but should be consistent.
#
#               ╔═══╗
#    ┌──┐   -α  ║ A ║
#   τ│  │   ┌──▶╚═══╝    τ     ┌───┐
#    │  │   │        ┌─────────│ca │─────────┐
#    └─▶┌───┐        │         └───┘         │
#       │ α │◀───────┘         ▲   │         │
#       └───┘╲                 │   │       -α│
#       ▲     ╲               -β   +β        │
#       │+α    ╲─────+β─────╲  │   │         ▼
#       │                    ╲ │   ▼   -αβ   ╔═══╗
#  ┌──┏━━━┓                   ▼┌───┐────────▶║ C ║
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
