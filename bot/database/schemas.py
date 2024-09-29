from sqlalchemy.ext.asyncio import AsyncEngine


async def proceed_schemas(engine: AsyncEngine, metadata: object) -> None:
    """Create migrations for tables in metadata object"""
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
