"""
Async database operations for write operations
"""

import asyncio
import threading
from typing import Dict, Any
import aiosqlite
import json
import os
from queue import Queue
import time

class AsyncProductDB:
    """Async wrapper for product write operations"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.environ.get('DATABASE_URL', 'sqlite:///products.db')
            if db_path.startswith('sqlite:///'):
                db_path = db_path.replace('sqlite:///', '')
            elif db_path.startswith('sqlite:////'):
                db_path = db_path.replace('sqlite:////', '/')
        self.db_path = db_path
        self.write_queue = Queue()
        self._start_worker_thread()
    
    def _start_worker_thread(self):
        """Start a background thread to process writes"""
        self.worker_thread = threading.Thread(target=self._process_writes, daemon=True)
        self.worker_thread.start()
    
    def _process_writes(self):
        """Background worker that processes writes"""
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        
        while True:
            try:
                # Get next write from queue
                operation = self.write_queue.get(timeout=1)
                
                if operation['type'] == 'create':
                    loop.run_until_complete(self._async_create(operation['data']))
                elif operation['type'] == 'update':
                    loop.run_until_complete(self._async_update(operation['id'], operation['data']))
                
            except:
                # Queue is empty, continue
                continue
    
    async def _async_create(self, product_data: Dict[str, Any]):
        """Asynch DB insert"""
        async with aiosqlite.connect(self.db_path) as db:
            rating_json = None
            if product_data.get("rating"):
                rating_json = json.dumps(product_data.get("rating"))
            
            await db.execute(
                """INSERT INTO products (title, price, description, category, image, rating)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    product_data.get("title"),
                    product_data.get("price"),
                    product_data.get("description"),
                    product_data.get("category"),
                    product_data.get("image"),
                    rating_json
                )
            )
            await db.commit()
            print(f"Async created product: {product_data.get('title')}")
    
    async def _async_update(self, product_id: int, updates: Dict[str, Any]):
        """Asynch DB update"""
        async with aiosqlite.connect(self.db_path) as db:
            update_fields = []
            values = []
            
            for field in ["title", "price", "description", "category", "image"]:
                if field in updates:
                    update_fields.append(f"{field} = ?")
                    values.append(updates[field])
            
            if "rating" in updates:
                update_fields.append("rating = ?")
                values.append(json.dumps(updates["rating"]))
            
            if not update_fields:
                return
            
            values.append(product_id)
            query = f"UPDATE products SET {', '.join(update_fields)} WHERE id = ?"
            
            await db.execute(query, values)
            await db.commit()
            print(f"Async updated product ID: {product_id}")
    
    def create_product_async(self, product_data: Dict[str, Any]):
        """Queue a product creation"""
        self.write_queue.put({
            'type': 'create',
            'data': product_data
        })
        # Return immediately - truly async
        return None
    
    def update_product_async(self, product_id: int, updates: Dict[str, Any]):
        """Queue a product update"""
        self.write_queue.put({
            'type': 'update',
            'id': product_id,
            'data': updates
        })
        # Return immediately - truly async
        return None

# Singleton instance for the app
async_db = AsyncProductDB()

# Wrapper functions
def fire_and_forget_create(product_data: Dict[str, Any]):
    """Fire and forget create - returns None immediately"""
    async_db.create_product_async(product_data)
    return None

def fire_and_forget_update(product_id: int, updates: Dict[str, Any]):
    """Fire and forget update - returns None immediately"""
    async_db.update_product_async(product_id, updates)
    return None
