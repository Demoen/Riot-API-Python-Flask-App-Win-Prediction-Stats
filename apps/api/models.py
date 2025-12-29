from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, JSON, BigInteger
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    puuid = Column(String, primary_key=True, index=True)
    game_name = Column(String, index=True)
    tag_line = Column(String, index=True)
    region = Column(String) # platform region e.g. euw1
    profile_icon_id = Column(Integer)
    summoner_level = Column(Integer)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

class Match(Base):
    __tablename__ = "matches"

    match_id = Column(String, primary_key=True, index=True)
    platform_id = Column(String)
    game_creation = Column(BigInteger)
    game_duration = Column(Integer)
    game_version = Column(String)
    queue_id = Column(Integer)
    # Store full JSON for future proofing / raw access
    data = Column(JSON) 
    
    participants = relationship("Participant", back_populates="match", cascade="all, delete-orphan")

class Participant(Base):
    __tablename__ = "participants"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(String, ForeignKey("matches.match_id"))
    puuid = Column(String, index=True)
    
    # Core stats for ML
    champion_id = Column(Integer)
    team_id = Column(Integer)
    win = Column(Boolean)
    
    kills = Column(Integer)
    deaths = Column(Integer)
    assists = Column(Integer)
    
    # ML Features (from ml_model.py)
    gold_per_minute = Column(Float)
    total_minions_killed = Column(Integer)
    vision_score = Column(Float)
    damage_dealt_to_champions = Column(Integer)
    
    # Store other relevant stats as JSON to avoid 100 columns if schema changes
    stats_json = Column(JSON)
    
    match = relationship("Match", back_populates="participants")

