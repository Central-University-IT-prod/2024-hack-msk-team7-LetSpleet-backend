from sqlmodel import SQLModel, create_engine
from backend.core.config import CONFIG, ConfigDatabase



#config_db = ConfigDatabase()
engine = create_engine(CONFIG.db_uri)
#SQLModel.metadata.create_all()

def build_db():
    SQLModel.metadata.create_all(engine)

