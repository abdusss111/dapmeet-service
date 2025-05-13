from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db import Base  # ✅ import Base
from models import *  # ✅ import your models

config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata  # ✅ include model metadata
