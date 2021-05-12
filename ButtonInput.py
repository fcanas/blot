import board
import digitalio

class ButtonInput:
	def __init__(self, aAction, bAction, abAction):
		self.active = False
		self.aAction = aAction
		self.bAction = bAction
		self.abAction = abAction
		self.buttonA = digitalio.DigitalInOut(board.D23)
		self.buttonB = digitalio.DigitalInOut(board.D24)
		self.buttonA.switch_to_input()
		self.buttonB.switch_to_input()
		self.needsClear = False
		
		self.lastA = self.buttonA.value
		self.lastB = self.buttonB.value
	
	def poll(self):
		valueChanged = False
		
		newA = self.buttonA.value
		if self.lastA != newA:
			valueChanged = True
			print("A:{}".format(newA))
			self.lastA = newA
			
		newB = self.buttonB.value
		if self.lastB != newB:
			valueChanged = True
			print("B:{}".format(newB))
			self.lastB = newB
			
		if valueChanged:
			print("------")
		else:
			return
		
		# print("needs clear: {}".format(self.needsClear))
		if not newA and not newB and not self.needsClear: # both A and B pressed:
			self.abAction()
			self.needsClear = True
		elif newB and not newA and not self.needsClear:  # just button A pressed:
			self.aAction()
			self.needsClear = True
		elif newA and not newB and not self.needsClear:  # just button B pressed
			self.bAction()
			self.needsClear = True
		else :
			self.needsClear = False
