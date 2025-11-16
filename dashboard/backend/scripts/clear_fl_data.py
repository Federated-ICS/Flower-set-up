#!/usr/bin/env python3
"""
Clear FL Data from Database
Removes all FL rounds and clients for clean testing
"""
import asyncio
import sys
sys.path.insert(0, '.')

from sqlalchemy import select, delete
from app.database import async_session_maker
from app.models import FLRound, FLClient


async def clear_fl_data():
    """Clear all FL rounds and clients from database"""
    async with async_session_maker() as db:
        try:
            print("\n🗑️  Clearing FL Data from Database")
            print("=" * 60)
            
            # Count before deletion
            rounds_result = await db.execute(select(FLRound))
            rounds_count = len(rounds_result.scalars().all())
            
            clients_result = await db.execute(select(FLClient))
            clients_count = len(clients_result.scalars().all())
            
            print(f"\n📊 Current Data:")
            print(f"   - FL Rounds: {rounds_count}")
            print(f"   - FL Clients: {clients_count}")
            
            if rounds_count == 0 and clients_count == 0:
                print("\n✅ Database is already empty!")
                return
            
            # Delete all clients
            await db.execute(delete(FLClient))
            print(f"\n🗑️  Deleted {clients_count} FL clients")
            
            # Delete all rounds
            await db.execute(delete(FLRound))
            print(f"🗑️  Deleted {rounds_count} FL rounds")
            
            # Commit changes
            await db.commit()
            
            print("\n" + "=" * 60)
            print("✅ FL Data Cleared Successfully!")
            print("=" * 60)
            print("\nDatabase is now empty. You can test with:")
            print("1. Pure WebSocket data (no database)")
            print("2. Fresh API data")
            print("\nTo test WebSocket-only:")
            print("  - Open: http://localhost:3000/fl-status")
            print("  - Run: curl -X POST http://localhost:8000/api/test/fl-progress")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Clear FL data from database")
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Skip confirmation prompt",
    )
    
    args = parser.parse_args()
    
    if not args.confirm:
        print("\n⚠️  WARNING: This will delete all FL rounds and clients from the database!")
        response = input("Are you sure? (yes/no): ")
        if response.lower() != "yes":
            print("❌ Cancelled")
            sys.exit(0)
    
    asyncio.run(clear_fl_data())
