from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()

class Agent(db.Model):
    __tablename__ = 'agents'
    
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.String(100), unique=True, nullable=False)
    hostname = db.Column(db.String(100))
    username = db.Column(db.String(100))
    operating_system = db.Column(db.String(100))
    last_online = db.Column(db.DateTime, default=datetime.utcnow)
    remote_ip = db.Column(db.String(45))
    geolocation = db.Column(db.String(100))
    output = db.Column(db.Text, default='')
    last_seen = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='offline')
    
    # Relationship with commands
    commands = db.relationship('Command', backref='agent', lazy='dynamic', cascade='all, delete-orphan')

    
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.output = ''
    
    def push_command(self, cmdline):
        """Add a command to the agent's queue"""
        cmd = Command(agent_id=self.id, cmdline=cmdline)
        db.session.add(cmd)
        db.session.commit()
    
    def rename(self, new_name):
        """Rename the agent"""
        self.hostname = new_name
        db.session.commit()
    
    @property
    def display_name(self):
        """Return display name for the agent"""
        return self.hostname or self.agent_id or 'Unknown'
    
    def is_online(self):
        """Check if agent is online (last seen within 5 minutes)"""
        if not self.last_online:
            return False
        from datetime import datetime, timedelta
        return (datetime.utcnow() - self.last_online) < timedelta(minutes=5)

class Command(db.Model):
    __tablename__ = 'commands'
    
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agents.id'), nullable=False)
    cmdline = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    executed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    output = db.Column(db.Text)
    error = db.Column(db.Text)
    return_code = db.Column(db.Integer)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    salt = db.Column(db.String(100))
    last_login_time = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(45))

class Smartphone(db.Model):
    __tablename__ = 'smartphones'
    id = db.Column(db.Integer, primary_key=True)
    phone_model = db.Column(db.String(100))
    android_version = db.Column(db.String(50))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

class Backup(db.Model):
    __tablename__ = 'backups'
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(200))
    file_size = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

