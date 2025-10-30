from **future** import annotations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def make_engine(url: str, echo: bool = False):
eng = create_engine(url, future=True, echo=echo)
return eng, sessionmaker(bind=eng, future=True)
