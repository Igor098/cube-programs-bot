import asyncio
from typing import Dict, List
from models import ProgramWithId

class ProgramStore:
    def __init__(self, page_size: int):
        self._programs: List[ProgramWithId] = []
        self._by_id: Dict[int, ProgramWithId] = {}
        self._version: int = 0
        self._page_size: int = max(1, int(page_size))
        self._lock = asyncio.Lock()
        
    def _page_count_unlocked(self) -> int:
        return (len(self._programs) + self._page_size - 1) // self._page_size

    def _clamp_page_index_unlocked(self, i: int) -> int:
        pages = self._page_count_unlocked()
        if pages == 0:
            return 0
        return min(max(i, 0), pages - 1)

    async def get_programs(self) -> List[ProgramWithId]:
        async with self._lock:
            return self._programs.copy()

    async def get_program_by_id(self, program_id: int) -> ProgramWithId | None:
        async with self._lock:
            return self._by_id.get(program_id, None)
    
    async def get_programs_by_age(self, age: int):
        result = []
        pages = await self.page_count()
        for i in range(pages):
            for p in await self.get_page(i):
                if getattr(p, "is_active", True) and getattr(p, "min_age", 0) <= age <= getattr(p, "max_age", 99):
                    result.append(p)
        return result

    async def add_program(self, program: ProgramWithId) -> None:
        async with self._lock:
            if program.id in self._by_id:
                raise ValueError(f"Такая программа уже существует.")

            self._programs.append(program)
            self._by_id[program.id] = program
            self._programs.sort(key=lambda p: p.id)
            self._version += 1

    async def add_programs(self, programs: List[ProgramWithId]) -> None:
        async with self._lock:
            seen_ids = set()
            for p in programs:
                if not isinstance(p, ProgramWithId):
                    raise ValueError("Все программы должны быть экземплярами ProgramWithId.")
                if p.id in seen_ids:
                    raise ValueError(f"Дубликат id во входных данных: {p.id}")
                seen_ids.add(p.id)

            for p in programs:
                if p.id in self._by_id:
                    raise ValueError(f"Программа с id {p.id} уже существует.")

            self._programs.extend(programs)
            self._programs.sort(key=lambda p: p.id)
            self._by_id.update({p.id: p for p in programs})
            self._version += 1

    async def remove_by_id(self, program_id: int) -> bool:
        async with self._lock:
            program = self._by_id.get(program_id)
            if program is None:
                return False

            self._programs.remove(program)
            self._by_id.pop(program.id, None)
            self._version += 1
            
            return True

    async def reset_programs(self, programs: List[ProgramWithId]) -> None:
        async with self._lock:
            ids = set()
            for p in programs:
                if p.id in ids:
                    raise ValueError(f"Дубликат id во входных данных: {p.id}")
                ids.add(p.id)

            self._programs[:] = programs
            self._programs.sort(key=lambda p: p.id)
            self._by_id.clear()
            self._by_id.update({p.id: p for p in programs})
            self._version += 1

    async def clear_programs(self) -> None:
        async with self._lock:
            self._programs.clear()
            self._by_id.clear()
            self._version += 1

    async def get_version(self) -> int:
        async with self._lock:
            return self._version

    async def page_count(self) -> int:
        async with self._lock:
            return self._page_count_unlocked()

    async def get_page(self, i: int) -> List[ProgramWithId]:
        async with self._lock:
            i = self._clamp_page_index_unlocked(i)
            start = i * self._page_size
            end = start + self._page_size
            return self._programs[start:end]

    async def count(self) -> int:
        async with self._lock:
            return len(self._programs)

    async def list(self, offset: int = 0, limit: int = 8) -> List[ProgramWithId]:
        async with self._lock:
            return self._programs[max(offset, 0):max(offset, 0)+max(0, min(limit, self._page_size))]