from abc import ABC, abstractmethod

class AuthPort(ABC):

    @abstractmethod
    async def login(self, credentials):
        raise NotImplementedError
    
    @abstractmethod
    async def signup(self, user):
        raise NotImplementedError
