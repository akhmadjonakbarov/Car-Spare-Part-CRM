from typing import Optional

from fastapi_pagination.ext.sqlalchemy import paginate

from sqlalchemy import select, desc, func, Select
from sqlalchemy.ext.asyncio import AsyncSession


class Pagination:

    @staticmethod
    async def get_paginated_data(
            db: AsyncSession, model, serializer_class, query, page, page_size,
    ):
        total_result = await db.execute(
            select(func.count()).select_from(model).where(model.deleted_at.is_(None))
        )
        total = total_result.scalar_one()

        offset = (page - 1) * page_size

        result = await db.execute(
            query.offset(offset).limit(page_size)
        )

        items = result.scalars().all()
        serializer = serializer_class(many=True)

        return {
            "data": {
                "pagination": {
                    "total": total,
                    "page": page,
                    "size": page_size,
                    "pages": (total + page_size - 1) // page_size,  # total pages

                },
                "list": serializer.dump(items),
            }
        }


def pagination_info(paginated_result) -> dict:
    total = paginated_result.total
    page = paginated_result.page
    size = paginated_result.size
    pages = paginated_result.pages
    pagination = {
        'total': total,
        'page': page,
        'size': size,
        'pages': pages,
    }
    return pagination


class PaginatedResponse:
    def __init__(
            self,
            db_session,
            model,
            serializer_class,
            params,
            order_by_fun=desc,
            order_field="created_at",
            base_query: Optional[Select] = None,
    ):
        self.db_session = db_session
        self.model = model
        self.serializer_class = serializer_class
        self.params = params
        self.order_by_fun = order_by_fun
        self.order_field = order_field
        self.base_query = base_query

    def get_query(self):
        """For sync or default async pagination"""
        field = getattr(self.model, self.order_field)
        return select(self.model).where(self.model.is_deleted == False).order_by(self.order_by_fun(field))

    async def get_paginated_response_async(self):
        """
        Asynchronous pagination for SQLAlchemy AsyncSession.
        Supports Marshmallow serializer and custom base query.
        """
        try:
            # ✅ Explicit None check
            if self.base_query is not None:
                query = self.base_query
            else:
                query = self.get_query()

            # perform async pagination
            paginated_result = await paginate(self.db_session, query, self.params)

            # serialize results
            serializer = self.serializer_class(many=True)
            serialized_data = serializer.dump(paginated_result.items)

            # structure pagination metadata
            pagination = {
                "total": paginated_result.total,
                "page": paginated_result.page,
                "size": paginated_result.size,
                "pages": paginated_result.pages,
            }

            return {
                "items": serialized_data,
                "pagination": pagination,
            }

        except Exception as e:
            print(f"Pagination error: {e}")
            raise
