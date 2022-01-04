import json
from typing import Union, Any, Type

from aiohttp import web
from aiohttp.web_request import FileField
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, ValidationError

from .utils import ControllerRequirement
from main_node.modules.authorization import AuthorizationService


class RoomAuth(ControllerRequirement):
    async def prepare_requirement(self, request: web.Request) -> Union[Any, web.Response]:
        auth_service: AuthorizationService = request.app['authorization']

        token_string = request.headers.get('Room-Token')
        if token_string is None:
            return web.HTTPBadRequest(text='Room-Token header is required.')

        auth = await auth_service.authorize_room(token_string)
        if not auth.token_check.known:
            return web.HTTPUnauthorized(text='Unknown Room-Token value.')

        if not auth.token_check.valid:
            return web.HTTPUnauthorized(text='Token is already invalid.')

        return auth.room_id


class AdminAuth(ControllerRequirement):
    async def prepare_requirement(self, request: web.Request) -> Union[Any, web.Response]:
        auth_service: AuthorizationService = request.app['authorization']

        token_string = request.headers.get('Admin-Token')
        if token_string is None:
            return web.HTTPBadRequest(text='Admin-Token header is required.')

        auth = await auth_service.authorize_admin(token_string)
        if not auth.token_check.known:
            return web.HTTPUnauthorized(text='Unknown token.')

        return auth.admin_id


class ImageField(ControllerRequirement):
    async def prepare_requirement(self, request: web.Request) -> Union[Any, web.Response]:
        if request.content_type != 'multipart/form-data':
            return web.HTTPBadRequest(text="Send image as multipart/form-data in field named «image».")

        post_data = await request.post()

        image_field = post_data.get('image')
        if image_field is None:
            return web.HTTPBadRequest(text="Required «image» multipart field.")

        if not isinstance(image_field, FileField):
            return web.HTTPBadRequest(text="Field «image» doesn't contain an image file.")

        try:
            image = Image.open(image_field.file)
        except UnidentifiedImageError:
            return web.HTTPBadRequest(text="Cannot identify image file. It's invalid.")

        return image


class PydanticPayload(ControllerRequirement):
    def __init__(self, keyword_argument_name: str, pydantic_model: Type[BaseModel]):
        super().__init__(keyword_argument_name)
        self._pydantic_model = pydantic_model

    async def prepare_requirement(self, r: web.Request) -> Union[Any, web.Response]:
        if r.content_type != 'application/json':
            return web.HTTPBadRequest(text="Required application/json Content-Type.")

        json_raw = await r.text()
        try:
            pydantic_data = self._pydantic_model.parse_raw(json_raw)
        except ValidationError as e:
            return web.HTTPBadRequest(text=f"Json data has wrong schema or types.")

        return pydantic_data
