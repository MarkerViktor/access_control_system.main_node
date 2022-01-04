from aiohttp import web

from face_recognition.two_step import FaceRecognizer, FaceImageNormalizer
from face_recognition.backends.dlib_ import DlibRecognizer, DlibDetector, DlibNormalizer

from .utils import DatabaseManager
from .modules.access_control import AccessControlService, AccessControlRepository
from .modules.authorization import AuthorizationService, AuthorizationRepository
from .modules.tasks import TasksService, TasksRepository
from main_node.controllers import handlers

import config


def init() -> web.Application:
    app = web.Application()
    manager = DatabaseManager(config.database_config)

    init_database(app, manager)
    init_access_control_service(app, manager)
    init_authorization_service(app, manager)
    init_tasks_service(app, manager)

    app.add_routes([
        web.post('/access/check/face', handlers.check_access_by_face),
        web.post('/access/check/descriptor', handlers.check_access_by_descriptor),
        web.post('/access/visit/new', handlers.record_visit),
        web.post('/access/descriptor/calculate', handlers.calculate_descriptor),

        web.get('/tasks/undone', handlers.get_undone_tasks),
        web.post('/tasks/report', handlers.report_task_performed),

        web.post('/authorization/room/login', handlers.room_login),
    ])
    return app


def init_database(app: web.Application, manager: DatabaseManager):
    app.on_startup.append(manager.launch_connection)
    app.on_shutdown.append(manager.close_connection)


def init_access_control_service(app: web.Application, manager: DatabaseManager):
    repository = AccessControlRepository(manager)
    access_control = AccessControlService(
        repository=repository,
        face_recognizer=FaceRecognizer(
            recognizer=DlibRecognizer()
        ),
        face_image_normalizer=FaceImageNormalizer(
            detector=DlibDetector(),
            normalizer=DlibNormalizer()
        ),
    )
    app[access_control.SERVICE_NAME] = access_control
    app.on_startup.append(access_control.init_service)
    app.on_shutdown.append(access_control.deinit_service)


def init_authorization_service(app: web.Application, manager: DatabaseManager):
    repository = AuthorizationRepository(manager)
    authorization = AuthorizationService(
        repository=repository,
    )
    app[authorization.SERVICE_NAME] = authorization
    app.on_startup.append(authorization.init_service)
    app.on_shutdown.append(authorization.deinit_service)


def init_tasks_service(app: web.Application, manager: DatabaseManager):
    repository = TasksRepository(manager)
    tasks_service = TasksService(
        repository=repository
    )
    app[tasks_service.SERVICE_NAME] = tasks_service
    app.on_startup.append(tasks_service.init_service)
    app.on_shutdown.append(tasks_service.deinit_service)
