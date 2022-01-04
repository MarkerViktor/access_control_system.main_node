from aiohttp import web
from PIL.Image import Image
import numpy as np

from face_recognition import NumpyImage
from main_node.modules.access_control import AccessControlService
from main_node.modules.authorization import AuthorizationService

from .utils import require, pydantic_response
from .requirements import RoomAuth, AdminAuth, ImageField, PydanticPayload
from .json_models import VisitInfo, FaceDescriptor, TaskPerformingReport, DescriptorAdding
from ..modules.tasks import TasksService


def convert_to_NumpyImage(image: Image) -> NumpyImage:
    return np.array(image)


@require(RoomAuth('room_id'), ImageField('image'))
async def check_access_by_face(r: web.Request, room_id: int, image: Image):
    access_control: AccessControlService = r.app['access_control']
    numpy_image = convert_to_NumpyImage(image)
    access_check = await access_control.check_access_by_face(room_id, numpy_image)
    return pydantic_response(access_check)


@require(RoomAuth('room_id'), PydanticPayload('payload', FaceDescriptor))
async def check_access_by_descriptor(r: web.Request, room_id: int, payload: FaceDescriptor):
    access_control: AccessControlService = r.app['access_control']
    descriptor = np.array(payload.features)
    access_check = await access_control.check_access_by_descriptor(room_id, descriptor)
    return pydantic_response(access_check)


@require(RoomAuth('room_id'), PydanticPayload('payload', VisitInfo))
async def record_visit(r: web.Request, room_id: int, payload: VisitInfo):
    access_control: AccessControlService = r.app['access_control']
    user_id, datetime_ = payload.user_id, payload.datetime
    visit_recording = await access_control.record_visit(room_id, user_id, datetime_)
    return pydantic_response(visit_recording)


@require(RoomAuth('room_id'))
async def get_undone_tasks(r: web.Request, room_id: int):
    tasks_service: TasksService = r.app['tasks']
    task_list = await tasks_service.get_undone_tasks(room_id)
    return pydantic_response(task_list)


@require(RoomAuth('room_id'), PydanticPayload('payload', TaskPerformingReport))
async def report_task_performed(r: web.Request, room_id: int, payload: TaskPerformingReport):
    tasks_service: TasksService = r.app['tasks']
    task_id = payload.task_id
    status = payload.new_status
    result = await tasks_service.report_task_performed(room_id, task_id, status)
    return pydantic_response(result)


async def room_login(r: web.Request):
    auth_service: AuthorizationService = r.app['authorization']
    token_string = r.headers.get('Login-Token')
    if token_string is None:
        return web.HTTPBadRequest(text='Login-Token header is required.')
    room_login_ = await auth_service.log_in_room(token_string)
    return pydantic_response(room_login_)


@require(AdminAuth(), ImageField('image'))
async def calculate_descriptor(r: web.Request, image: Image):
    access_control: AccessControlService = r.app['access_control']
    numpy_image = convert_to_NumpyImage(image)
    descriptor_calculation = await access_control.calculate_descriptor(numpy_image)
    return pydantic_response(descriptor_calculation)
