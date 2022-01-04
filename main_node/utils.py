from abc import ABC, abstractmethod
from typing import TypedDict, Optional, TypeVar, Generic

from aiohttp import web
from asyncpg import connect, Connection
from pydantic import BaseModel


class DatabaseConfig(TypedDict):
    host: str
    port: int
    database: str
    user: str
    password: str


class DatabaseManager:
    def __init__(self, config: DatabaseConfig):
        self._config = config
        self._database_connection: Optional[Connection] = None

    async def launch_connection(self, _):
        self._database_connection = await connect(**self._config)

    async def close_connection(self, _):
        if self._database_connection is not None:
            await self._database_connection.close()

    @property
    def database_connection(self):
        assert self._database_connection is not None, \
            'Connection must be launched by .launch_connection() method before getting.'
        return self._database_connection


class Repository(ABC):
    def __init__(self, manager: DatabaseManager):
        self.__db_manager = manager

    @property
    def _conn(self):
        assert self.__db_manager is not None, \
            'Database manager is set for repository.'
        return self.__db_manager.database_connection


class Service(ABC):

    @property
    @abstractmethod
    def SERVICE_NAME(self) -> str: ...

    @abstractmethod
    async def init_service(self, app: web.Application) -> None: ...

    @abstractmethod
    async def deinit_service(self, app: web.Application) -> None: ...


RE = TypeVar('RE', bound=BaseModel)

class Result(BaseModel, Generic[RE]):
    success: bool

class Ok(Result):
    result: RE
    success = True

class Error(Result):
    cause: str
    success = False
