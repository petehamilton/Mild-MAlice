#Singleton class modelled on http://code.activestate.com/recipes/52558-the-singleton-pattern-implemented-with-python/
class UniqueIDGenerator:
    class __impl:
        currentID = 1
        
        def getNextUniqueID(self):
            id = self.currentID
            currentID += 1
            return id

    # storage for the instance reference
    __instance = None

    def __init__(self):
        # Check whether we already have an instance
        if UniqueIDGenerator.__instance is None:
            # Create and remember instance
            UniqueIDGenerator.__instance = UniqueIDGenerator.__impl()

        # Store instance reference as the only member in the handle
        self.__dict__['_Singleton__instance'] = UniqueIDGenerator.__instance
    
    #Delegate Getters and Setters to singleton instance
    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)