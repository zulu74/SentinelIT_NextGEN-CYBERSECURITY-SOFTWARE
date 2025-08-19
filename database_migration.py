# database_migration_fixed.py - Fixed version that works properly
import os
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

def backup_and_recreate_database():
    """Backup existing data and recreate database with new schema"""
    
    database_path = 'sentinelit.db'
    backup_path = 'sentinelit_backup.db'
    
    print("🔄 Starting database migration...")
    
    # Step 1: Backup existing data if database exists
    existing_users = []
    existing_threats = []
    
    if os.path.exists(database_path):
        print("📦 Backing up existing database...")
        
        # Make a backup copy first
        import shutil
        shutil.copy2(database_path, backup_path)
        print(f"✅ Database backed up to {backup_path}")
        
        # Connect directly to SQLite to backup data
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        
        # Backup existing users if table exists
        try:
            cursor.execute("SELECT * FROM user")
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            existing_users = [dict(zip(columns, row)) for row in rows]
            print(f"✅ Backed up {len(existing_users)} existing users")
        except sqlite3.OperationalError as e:
            print(f"ℹ️  No existing user table found: {e}")
        
        # Backup existing threat logs if table exists
        try:
            cursor.execute("SELECT * FROM threat_log")
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            existing_threats = [dict(zip(columns, row)) for row in rows]
            print(f"✅ Backed up {len(existing_threats)} existing threat logs")
        except sqlite3.OperationalError as e:
            print(f"ℹ️  No existing threat_log table found: {e}")
        
        conn.close()
        
        # Remove old database
        os.remove(database_path)
        print("🗑️  Old database removed")
    
    # Step 2: Create new database with proper schema using raw SQL
    print("🆕 Creating new database with updated schema...")
    
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    
    # Create user table with all new columns
    cursor.execute('''
        CREATE TABLE user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(120) UNIQUE NOT NULL,
            password VARCHAR(256) NOT NULL,
            role VARCHAR(50) DEFAULT 'user',
            last_seen DATETIME,
            security_profile VARCHAR(50) DEFAULT 'standard',
            department VARCHAR(100) DEFAULT 'IT Security',
            endpoints_count INTEGER DEFAULT 0,
            threats_detected INTEGER DEFAULT 0,
            status VARCHAR(50) DEFAULT 'active'
        )
    ''')
    
    # Create threat_log table
    cursor.execute('''
        CREATE TABLE threat_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            threat_type VARCHAR(120),
            severity VARCHAR(50),
            source_ip VARCHAR(50),
            target_ip VARCHAR(50),
            description TEXT,
            status VARCHAR(50) DEFAULT 'new',
            user_id INTEGER,
            module_source VARCHAR(100),
            FOREIGN KEY (user_id) REFERENCES user (id)
        )
    ''')
    
    # Create system_metrics table
    cursor.execute('''
        CREATE TABLE system_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            cpu_usage FLOAT,
            memory_usage FLOAT,
            disk_usage FLOAT,
            network_in INTEGER,
            network_out INTEGER,
            active_threats INTEGER,
            module_name VARCHAR(100)
        )
    ''')
    
    # Create security_module table
    cursor.execute('''
        CREATE TABLE security_module (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) UNIQUE NOT NULL,
            status VARCHAR(50) DEFAULT 'active',
            last_update DATETIME,
            threats_detected INTEGER DEFAULT 0,
            alerts_generated INTEGER DEFAULT 0,
            description TEXT
        )
    ''')
    
    print("✅ All tables created successfully")
    
    # Step 3: Restore backed up users with new schema
    if existing_users:
        print(f"🔄 Migrating {len(existing_users)} users...")
        for user_data in existing_users:
            try:
                cursor.execute('''
                    INSERT INTO user (email, password, role, last_seen, security_profile, 
                                    department, endpoints_count, threats_detected, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_data.get('email', 'unknown@example.com'),
                    user_data.get('password', generate_password_hash('password123')),
                    user_data.get('role', 'user'),
                    datetime.now().isoformat(),
                    'enterprise',  # New column with default
                    'IT Security',  # New column with default
                    0,  # New column with default
                    0,  # New column with default
                    'active'  # New column with default
                ))
                print(f"✅ Migrated user: {user_data.get('email', 'unknown')}")
            except Exception as e:
                print(f"⚠️  Error migrating user {user_data.get('email', 'unknown')}: {e}")
    
    # Step 4: Restore backed up threat logs
    if existing_threats:
        print(f"🔄 Migrating {len(existing_threats)} threat logs...")
        for threat_data in existing_threats:
            try:
                cursor.execute('''
                    INSERT INTO threat_log (threat_type, severity, source_ip, target_ip, 
                                          description, status, user_id, module_source, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    threat_data.get('threat_type'),
                    threat_data.get('severity'),
                    threat_data.get('source_ip'),
                    threat_data.get('target_ip'),
                    threat_data.get('description'),
                    threat_data.get('status', 'new'),
                    threat_data.get('user_id'),
                    threat_data.get('module_source', 'Unknown'),
                    threat_data.get('timestamp', datetime.now().isoformat())
                ))
            except Exception as e:
                print(f"⚠️  Error migrating threat log: {e}")
        print(f"✅ Migrated {len(existing_threats)} threat logs")
    
    # Step 5: Create admin user if it doesn't exist
    cursor.execute("SELECT * FROM user WHERE email = ?", ('admin@sentinelit.com',))
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO user (email, password, role, last_seen, security_profile, 
                            department, endpoints_count, threats_detected, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'admin@sentinelit.com',
            generate_password_hash('admin123'),
            'admin',
            datetime.now().isoformat(),
            'enterprise',
            'IT Security',
            5,
            0,
            'active'
        ))
        print("✅ Created admin user (admin@sentinelit.com / admin123)")
    else:
        print("ℹ️  Admin user already exists")
    
    # Step 6: Add sample threat logs if none exist
    cursor.execute("SELECT COUNT(*) FROM threat_log")
    threat_count = cursor.fetchone()[0]
    
    if threat_count == 0:
        sample_threats = [
            ('Malware Detection', 'high', '203.0.113.45', '10.0.0.10', 
             'WannaCry variant detected by ThreatDNA module', 'quarantined', 'ThreatDNA'),
            ('Suspicious USB Activity', 'medium', '192.168.1.100', '10.0.0.5',
             'Unauthorized USB device detected by USBWatch', 'investigating', 'USBWatch'),
            ('IoT Device Anomaly', 'medium', '192.168.1.50', '10.0.0.1',
             'IoT device showing suspicious network behavior', 'isolated', 'IoTMonitor')
        ]
        
        for threat in sample_threats:
            cursor.execute('''
                INSERT INTO threat_log (threat_type, severity, source_ip, target_ip, 
                                      description, status, module_source, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', threat + (datetime.now().isoformat(),))
        
        print("✅ Added sample threat logs")
    
    # Step 7: Add security modules
    security_modules = [
        ('ThreatDNA', 'active', 'Advanced malware fingerprint detection'),
        ('IoTMonitor', 'active', 'IoT device monitoring with auto-isolation'),
        ('WatchdogAI', 'active', 'AI-powered behavioral analysis'),
        ('MemoryWatch', 'active', 'Memory usage and leak detection'),
        ('CloudWatch', 'active', 'Cloud infrastructure monitoring'),
        ('PowerWatch', 'active', 'Power grid stability monitoring'),
        ('PacketShield', 'active', 'Network packet analysis and filtering'),
        ('StealthCam', 'active', 'Webcam activity monitoring'),
        ('PhantomStaff', 'active', 'AI Helpdesk and security monitoring'),
        ('Quarantine', 'active', 'Automated threat isolation system'),
        ('MailWatch', 'active', 'Email security and phishing detection'),
        ('PatchCheckV2', 'active', 'Vulnerability assessment and patching'),
        ('SIEMCore', 'active', 'Security information and event management'),
        ('ResurgWatch', 'active', 'Advanced persistent threat detection'),
        ('TravelTrap', 'active', 'Email security and phishing prevention'),
        ('PatternEngine', 'active', 'Behavioral pattern analysis'),
        ('USBWatch', 'active', 'USB device monitoring and control'),
        ('KernelWatch', 'active', 'Kernel-level security monitoring'),
        ('FTPWatch', 'active', 'FTP traffic monitoring and analysis')
    ]
    
    for module in security_modules:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO security_module 
                (name, status, description, last_update, threats_detected, alerts_generated)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', module + (datetime.now().isoformat(), 0, 0))
        except Exception as e:
            print(f"⚠️  Error adding security module {module[0]}: {e}")
    
    print("✅ Added security modules")
    
    # Commit all changes and close
    conn.commit()
    conn.close()
    
    print("💾 Database migration completed successfully!")
    print("\n🔐 Login credentials:")
    print("   Email: admin@sentinelit.com")
    print("   Password: admin123")
    print(f"\n📁 Original database backed up as: {backup_path}")
    print("🚀 You can now run your app.py safely!")

if __name__ == "__main__":
    backup_and_recreate_database()