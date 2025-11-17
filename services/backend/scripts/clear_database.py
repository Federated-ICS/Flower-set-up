"""
Clear all data from database tables
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text
from app.database import async_session_maker


async def clear_database():
    """Clear all tables"""
    print("🗑️  Clearing database...")
    
    async with async_session_maker() as db:
        try:
            # Delete in correct order (respecting foreign keys)
            await db.execute(text("DELETE FROM predicted_techniques"))
            await db.execute(text("DELETE FROM predictions"))
            await db.execute(text("DELETE FROM alert_sources"))
            await db.execute(text("DELETE FROM alerts"))
            await db.execute(text("DELETE FROM fl_clients"))
            await db.execute(text("DELETE FROM fl_rounds"))
            await db.execute(text("DELETE FROM network_data"))
            
            await db.commit()
            
            print("✅ Database cleared successfully!")
            
        except Exception as e:
            print(f"❌ Error clearing database: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(clear_database())
