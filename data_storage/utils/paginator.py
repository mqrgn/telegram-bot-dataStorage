from typing import List, Dict, Any, Optional
import aiosqlite


class DatabasePaginator:
    def __init__(
        self,
        db_path: str,
        user_id: int,
        items_per_page: int = 4,
        id_column: str = "user_file_id",
        type_column: str = "file_type",
    ):
        self.db_path = db_path
        self.user_id = user_id
        self.items_per_page = items_per_page
        self.id_column = id_column
        self.type_column = type_column
        self.current_page = 0
        self.total_items = 0
        self.current_items: List[Dict] = []
        self.additional_filters: Dict[str, Any] = {}  # Фильтры по другим колонкам

    def set_filters(self, filters: Optional[Dict[str, Any]] = None):
        """Задать дополнительные фильтры (например, {'file_type': 'pdf'})"""
        self.additional_filters = filters or {}

    async def count_files(self):
        """Подсчитать общее число файлов с учётом фильтров"""
        async with aiosqlite.connect(self.db_path) as db:
            where_clause = "WHERE user_id = ?"
            params = [self.user_id]

            for col, val in self.additional_filters.items():
                where_clause += f" AND {col} = ?"
                params.append(val)

            query = f"SELECT COUNT(*) FROM user_files {where_clause}"

            async with db.execute(query, params) as cursor:
                result = await cursor.fetchone()
                self.total_items = result[0] if result else 0

        return self.total_items

    async def _load_current_page(self):
        """Загрузить текущую страницу"""
        offset = self.current_page * self.items_per_page
        async with aiosqlite.connect(self.db_path) as db:
            where_clause = "WHERE user_id = ?"
            params = [self.user_id]

            for col, val in self.additional_filters.items():
                where_clause += f" AND {col} = ?"
                params.append(val)

            query = f'''
                SELECT {self.id_column}, {self.type_column}
                FROM user_files
                {where_clause}
                LIMIT ? OFFSET ?
            '''
            params.extend([self.items_per_page, offset])

            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                self.current_items = [
                    {
                        'id': row[0],
                        'type': row[1],
                        'global_number': offset + i + 1
                    }
                    for i, row in enumerate(rows)
                ]

    async def load(self):
        """Загрузить начальное состояние: пересчитать и загрузить первую страницу"""
        self.current_page = 0
        await self.count_files()
        await self._load_current_page()

    async def next(self) -> bool:
        """Перейти к следующей странице"""
        if not self.has_next():
            return False
        self.current_page += 1
        await self._load_current_page()
        return True

    async def prev(self) -> bool:
        """Перейти к предыдущей странице"""
        if not self.has_prev():
            return False
        self.current_page -= 1
        await self._load_current_page()
        return True

    def has_next(self) -> bool:
        return (self.current_page + 1) * self.items_per_page < self.total_items

    def has_prev(self) -> bool:
        return self.current_page > 0

    def get_current_items(self) -> List[Dict[str, Any]]:
        return self.current_items

    def get_page_info(self) -> Dict[str, int]:
        return {
            'current_page': self.current_page + 1,
            'total_pages': max(1, (self.total_items + self.items_per_page - 1) // self.items_per_page),
            'total_items': self.total_items,
            'start_item': self.current_page * self.items_per_page + 1,
            'end_item': min((self.current_page + 1) * self.items_per_page, self.total_items)
        }

    def get_pagination_buttons(self) -> List[Dict[str, str]]:
        buttons = []
        if self.has_prev():
            buttons.append({'text': '⬅️ Назад', 'callback_data': 'prev_page'})

        info = self.get_page_info()
        buttons.append({'text': f"{info['current_page']}/{info['total_pages']}", 'callback_data': 'page_info'})

        if self.has_next():
            buttons.append({'text': 'Вперед ➡️', 'callback_data': 'next_page'})

        return buttons
