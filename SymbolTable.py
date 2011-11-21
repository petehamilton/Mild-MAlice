class SymbolTable(object):
	def __init__(self, symbolTable = None):
		self.symbolTable = symbolTable
		self.dictionary = {}
	
	def add(self, name, obj):
		dictionary[name] = obj
	
	def lookupCurrLevelOnly(name):
		return dictionary[name]
		
	def loopupCurrLevelAndEnclosingLevels(name):
		S = self
		while S != None:
			obj = S.lookupCurrLevelOnly(name)
			if obj != None:
				return obj
				S = S.symbolTable
			return None
			 