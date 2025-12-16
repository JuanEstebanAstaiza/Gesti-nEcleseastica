#!/usr/bin/env python3
"""Script para arreglar las contraseñas en la base de datos"""

import asyncio
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

pwd = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Genera hashes
admin_hash = pwd.hash('admin123')
member_hash = pwd.hash('member123')
super_hash = pwd.hash('superadmin123')

print(f'Admin hash: {admin_hash}')
print(f'Member hash: {member_hash}') 
print(f'Super hash: {super_hash}')

async def update_passwords():
    # Actualiza la base de datos de usuarios
    engine = create_async_engine('postgresql+asyncpg://ekklesia:ekklesia@db:5432/ekklesia')
    async with engine.begin() as conn:
        await conn.execute(text("UPDATE users SET hashed_password = :hash WHERE role = 'admin'"), {"hash": admin_hash})
        await conn.execute(text("UPDATE users SET hashed_password = :hash WHERE role = 'member'"), {"hash": member_hash})
        result = await conn.execute(text('SELECT email, substring(hashed_password,1,15) as hash FROM users LIMIT 5'))
        for row in result:
            print(f'Updated user: {row}')
    await engine.dispose()

    # Base de datos master (superadmins)
    engine_master = create_async_engine('postgresql+asyncpg://ekklesia:ekklesia@db_master:5432/ekklesia_master')
    async with engine_master.begin() as conn:
        await conn.execute(text("UPDATE super_admins SET hashed_password = :hash"), {"hash": super_hash})
        result = await conn.execute(text('SELECT email, substring(hashed_password,1,15) as hash FROM super_admins'))
        for row in result:
            print(f'Updated superadmin: {row}')
    await engine_master.dispose()

    print('Done! All passwords updated.')

asyncio.run(update_passwords())

