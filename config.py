import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "mysql+pymysql://root:DmRAFbxJAuoroDekTYiWQBiTMndpFcXr@junction.proxy.rlwy.net:32757/railway"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False