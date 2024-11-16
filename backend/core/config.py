import os
from datetime import timedelta
from sqlalchemy import URL
import dotenv




dotenv.load_dotenv()
config = os.environ



class ConfigDatabase:
    connection_scheme="postgresql+psycopg2"
    user = config["POSTGRES_USER"]
    password = config["POSTGRES_PASSWORD"]
    host = config["POSTGRES_HOST"]
    port = config["POSTGRES_PORT"]
    db_name= config["POSTGRES_DB"]
    security_key=config["SECRET_KEY"]
    token_expire_timedelta = timedelta(60 * 60)
    
    @property
    def db_uri(self) -> URL:
        return URL.create(
            drivername=self.connection_scheme,
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.db_name
            )



CONFIG = ConfigDatabase()
    
