#!/usr/bin/env python3
"""
Wisespend Database Setup Script
Initializes the MySQL database and verifies connection
"""

import os
import sys
from db_config import DB_CONFIG, init_connection_pool, test_connection
from db_init import init_database

def main():
    print("\n" + "="*60)
    print("  WISESPEND DATABASE SETUP")
    print("="*60 + "\n")
    
    print("📋 Current Configuration:")
    print(f"   Host: {DB_CONFIG['host']}")
    print(f"   User: {DB_CONFIG['user']}")
    print(f"   Database: {DB_CONFIG['database']}")
    print(f"   Port: {DB_CONFIG['port']}\n")
    
    response = input("Is this configuration correct? (y/n): ").strip().lower()
    if response != 'y':
        print("\n❌ Please edit 'db_config.py' and update your MySQL credentials.")
        print("   Then run this script again.\n")
        return False
    
    print("\n🔄 Initializing database...\n")
    if init_database():
        print("\n✅ Initializing connection pool...\n")
        if init_connection_pool() and test_connection():
            print("\n✅ Setup complete! Your database is ready.\n")
            print("📚 Next steps:")
            print("   1. (Optional) Edit db_config.py if you need to change credentials")
            print("   2. Run: python wisespend.py")
            print("   3. Create an account or login\n")
            return True
    
    print("\n❌ Setup failed. Please check your MySQL server and configuration.\n")
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
