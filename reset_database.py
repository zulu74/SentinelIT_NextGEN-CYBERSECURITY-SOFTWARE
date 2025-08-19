#!/usr/bin/env python3
"""
Database reset script for SentinelIT
Drops and recreates all database tables with sample data
"""

import os
import sys
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone

def reset_database():
    try:
        # Import your app and models
        from app import app, db, User, ThreatLog
        
        print("🔄 Resetting SentinelIT database...")
        
        with app.app_context():
            # Drop all tables
            print("📝 Dropping existing tables...")
            db.drop_all()
            
            # Create all tables
            print("🏗️  Creating fresh tables...")
            db.create_all()
            
            # Create default admin user
            admin_user = User(
                email='admin@sentinelit.com',
                password=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin_user)
            
            # Create sample regular user
            regular_user = User(
                email='user@sentinelit.com',
                password=generate_password_hash('user123'),
                role='user'
            )
            db.session.add(regular_user)
            
            # Create sample threat logs
            sample_threats = [
                ThreatLog(
                    threat_type='Port Scan',
                    severity='medium',
                    source_ip='192.168.1.100',
                    target_ip='10.0.0.5',
                    description='Suspicious port scanning activity detected',
                    status='new'
                ),
                ThreatLog(
                    threat_type='Malware Detection',
                    severity='high',
                    source_ip='203.0.113.45',
                    target_ip='10.0.0.10',
                    description='Malicious file detected in network traffic',
                    status='investigating'
                ),
                ThreatLog(
                    threat_type='Failed Login Attempt',
                    severity='low',
                    source_ip='198.51.100.23',
                    target_ip='10.0.0.1',
                    description='Multiple failed login attempts from external IP',
                    status='resolved'
                )
            ]
            
            for threat in sample_threats:
                db.session.add(threat)
            
            # Commit all changes
            db.session.commit()
            
            print("✅ Database reset successfully!")
            print("👤 Default users created:")
            print("   Admin: admin@sentinelit.com / admin123")
            print("   User:  user@sentinelit.com / user123")
            print("📊 Sample threat logs created")
            
    except ImportError as e:
        print(f"❌ Failed to import app modules: {e}")
        print("Make sure you're running this script from your SentinelIT project directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Database reset failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ app.py not found in current directory")
        print("Please run this script from your SentinelIT project directory")
        sys.exit(1)
    
    reset_database()