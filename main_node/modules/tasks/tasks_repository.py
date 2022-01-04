from typing import Optional

from main_node.utils import Repository

from .tasks_entities import Task, Status


class TasksRepository(Repository):
    async def get_room_tasks(self, room_id: int, status: str) -> list[Task]:
        query = 'select * from "RoomTask" where "room_id" = $1 and "status" = $2'
        records = await self._conn.fetch(query, room_id, status)
        return [Task.parse_obj(r) for r in records]

    async def check_manager_exist(self, id_: int):
        query = 'select from "Manager" where "id" = $1'
        return await self._conn.fetchrow(query, id_) is not None

    async def check_room_exist(self, id_: int):
        query = 'select from "Room" where "id" = $1'
        return await self._conn.fetchrow(query, id_) is not None

    async def update_task_status(self, new_status: str, *task_ids: int) -> None:
        query = 'update "RoomTask" set "status" = $1 where "id" = $2'
        args = ((new_status, task_id) for task_id in task_ids)
        await self._conn.executemany(query, args)

    async def create_task(self, room_id: id, manager_id: id, body: str) -> Task:
        query = 'insert into "RoomTask" ("room_id", "manager_id", "body", "status")' \
                'values ($1, $2, $3, $4) returning *'
        record = self._conn.fetchrow(query, room_id, manager_id, body, Status.UNDONE)
        return Task.parse_raw(record)

    async def get_task(self, id_: int) -> Optional[Task]:
        query = 'select * from "RoomTask" where "id" = $1'
        if record := await self._conn.fetchrow(query, id_):
            return Task.parse_obj(record)
        else:
            return None
