from enum import Enum
from typing import Any

from pydantic import BaseModel

from main_node.utils import Service, Ok, Error, Result

from .tasks_entities import Task, Status
from .tasks_repository import TasksRepository


class TasksService(Service):
    SERVICE_NAME = 'tasks'

    def __init__(self, repository: 'TasksRepository'):
        self._repository = repository

    async def get_undone_tasks(self, room_id: int) -> Result['TaskList']:
        # TODO: Возвращать только содержимое body
        tasks = await self._repository.get_room_tasks(room_id, Status.UNDONE)
        return Ok(result=TaskList(tasks=tasks))

    async def report_task_performed(self, room_id: int, task_id: int, new_status: str) -> Result:
        # Get task by id
        task = await self._repository.get_task(task_id)
        if task is None:
            return Error(cause='No task with provided id.')
        # Check the task bounded to the room
        if task.room_id != room_id:
            return Error(cause="Room hasn't task with provided id.")
        # Check new status valid
        if new_status not in iter(Status):
            return Error(cause=f'Unknown status. Possible statuses: {", ".join(map(lambda s: s.value, Status))}.')
        await self._repository.update_task_status(new_status, task_id)
        return Result(success=True)

    async def add_task(self, manager_id: int, room_id: int, task_body: str) -> Result[Task]:
        # Check manager exist
        if not self._repository.check_manager_exist(manager_id):
            return Error(cause="Unknown manager.")
        # Check room exist
        if not self._repository.check_room_exist(room_id):
            return Error(cause='Unknown room.')
        task = await self._repository.create_task(room_id, manager_id, task_body)
        return Ok(result=task)

    async def init_service(self, _):
        pass

    async def deinit_service(self, _):
        pass


class TaskList(BaseModel):
    tasks: list[Task]
