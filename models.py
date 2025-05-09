from sqlalchemy import Column, String, create_engine, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Mapped, mapped_column, relationship
from typing import List
from datetime import datetime
import os
import shutil

# --- Android-compatible DB path logic ---
try:
    from kivy.utils import platform
    if platform == "android":
        from android.storage import app_storage_path
        from kivy.resources import resource_find

        app_path = app_storage_path()
        db_path = os.path.join(app_path, "hub01.db")

        if not os.path.exists(db_path):
            bundled = resource_find("hub01.db")
            if bundled:
                shutil.copy(bundled, db_path)
    else:
        # Desktop environment
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "hub01.db")
except Exception as e:
    print(f"⚠️ Failed to set up DB path: {e}")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "hub01.db")



#db_url='sqlite:///hub01.db'

engine = create_engine(f"sqlite:///{db_path}")



Session=sessionmaker(bind=engine)
session=Session()
Base=declarative_base()


class Client(Base):
    __tablename__='clients'

    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column()
    
    device:Mapped[List['Device']]=relationship(back_populates='client' ,uselist=True)
    transaction:Mapped[List['Transaction']]=relationship(back_populates='client')

class Device(Base):
    __tablename__='devices'

    id:Mapped[int]=mapped_column(primary_key=True)
    device_type:Mapped[str]=mapped_column(nullable=True)         #divecType [Battery ,mobile ,laptop ,lighter ,Etc]
    brand:Mapped[str]=mapped_column(nullable=True)               #Brand name (e.g., Samsung, Dell, Xiaomi)
    
    

    client_id:Mapped[int]=mapped_column(ForeignKey('clients.id'))


    client:Mapped['Client']=relationship(back_populates='device')

class Transaction(Base):
    __tablename__='transactions'

    id:Mapped[int] =mapped_column(primary_key=True)
    amount:Mapped[float]=mapped_column(nullable=True)
    time:Mapped[datetime]=mapped_column(nullable=True)
    NumberOfDevices:Mapped[int]=mapped_column(nullable=True)
    notes: Mapped[str] = mapped_column(nullable=True)
    client_id:Mapped[int]=mapped_column(ForeignKey('clients.id'))

    client:Mapped['Client']=relationship(back_populates='transaction')


# Only create schema if database file doesn't exist (e.g. on desktop for testing)
if not os.path.exists(db_path):
    Base.metadata.create_all(engine)

    