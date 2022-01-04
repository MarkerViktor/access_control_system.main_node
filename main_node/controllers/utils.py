from abc import ABC, abstractmethod
from functools import wraps
from typing import Callable, Union, Any

from aiohttp.web import Request, Response, StreamResponse, json_response
from pydantic import BaseModel

Handler = Callable


class require:
    def __init__(self, *requirements: 'ControllerRequirement'):
        self._requirements = requirements

    def __call__(self, handler: Handler) -> Handler:
        requirements = self._requirements

        @wraps(handler)
        async def wrapper_handler(request: Request, *args, **kwargs) -> Union[Response, StreamResponse]:
            nonlocal requirements, handler

            requirements_kwargs = {}
            for req in requirements:
                preparing_result = await req.prepare_requirement(request)

                if isinstance(preparing_result, Response):
                    return preparing_result

                if req.name is not None:
                    requirements_kwargs[req.name] = preparing_result

            return await handler(request, *args, **kwargs, **requirements_kwargs)

        return wrapper_handler


class ControllerRequirement(ABC):
    def __init__(self, keyword_argument_name: str = None):
        self.name = keyword_argument_name

    @abstractmethod
    async def prepare_requirement(self, request: Request) -> Union[Any, Response]: ...


def pydantic_response(model: BaseModel) -> Response:
    return json_response(text=model.json(exclude_none=True))
