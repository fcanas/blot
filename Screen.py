from ButtonInput import *

class Screen:
	def __init__(self, title):
		
		def aA():
			self.aAction()
		def bA():
			self.bAction()
		def abA():
			self.abAction()
		
		self.title = title
		self._needsUpdate = True
		self.input = ButtonInput(aA, bA, abA)
		self.navStack = None
	
	@property
	def needsUpdate(self):
		return self._needsUpdate
	
	@needsUpdate.setter
	def needsUpdate(self, newValue):
		self._needsUpdate = newValue
	
	def render(self, screen):
		self.needsUpdate = False
		
	def aAction(self):
		pass
	
	def bAction(self):
		pass
		
	def abAction(self):
		pass
		

class NavigationStack(Screen):
	def __init__(self, root, screenDevice):
		Screen.__init__(self, root.title)
		root.navStack = self
		self.stack = []
		self.push(root)
		self.screenDevice = screenDevice
		
	@Screen.needsUpdate.getter
	def needsUpdate(self):
		top = self.stack[-1]
		return top.needsUpdate
	
	def render(self, screen):
		top = self.stack[-1]
		top.render(screen)
	
	def push(self, top):
		top.navStack = self
		self.stack.append(top)
		top.needsUpdate = True
		self.input = x.input
		self.input.active = True
	
	def pop(self):
		
		if len(self.stack) == 1:
			self.screenDevice.backlight.off()
			quit()
		
		self.input.active = False
		self.stack.pop()
		top = self.stack[-1]
		self.input = top.input
		self.input.active = True
		top.needsUpdate = True
		

class Menu(Screen):
	def __init__(self, title, options, selectedIndex=0):
		Screen.__init__(self, title)
		self.options = options
		
		def pop_():
			self.pop()
		
		self.options.append(MenuAction("Exit", pop_))
		self.selectedIndex = selectedIndex
	
	def pop(self):
		if self.navStack is not None:
			self.navStack.pop()
	
	def render(self, screen):
		Screen.render(self, screen)
		screen.blank()
		screen.printLn(self.title, "#AAAAAA")
		for idx in range(len(self.options)):
			screen.printLn(self.options[idx].title, selected=(idx==self.selectedIndex))
		screen.commit()
	
	def aAction(self):
		self.selectedIndex = max(self.selectedIndex - 1, 0)
		print(self.selectedIndex)
		self.needsUpdate = True

	def bAction(self):
		self.selectedIndex = min(self.selectedIndex + 1, len(self.options) - 1)
		print(self.selectedIndex)
		self.needsUpdate = True
		
	def abAction(self):
		option = self.options[self.selectedIndex]
		if isinstance(option, Screen):
			if self.navStack is not None:
				self.navStack.push(option)
		elif isinstance(option, MenuAction):
			option.action()

class MenuAction:
	def __init__(self, title, action):
		self.title = title
		self.action = action
