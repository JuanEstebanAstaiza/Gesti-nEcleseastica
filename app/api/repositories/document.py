from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document


class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **data) -> Document:
        doc = Document(**data)
        self.session.add(doc)
        await self.session.commit()
        await self.session.refresh(doc)
        return doc

    async def get(self, doc_id: int) -> Document | None:
        result = await self.session.execute(select(Document).where(Document.id == doc_id))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Document]:
        result = await self.session.execute(select(Document))
        return list(result.scalars().all())
