import os
import sys

from sqlalchemy import ForeignKey, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# 1. Nueva forma de definir la Base
class Base(DeclarativeBase):
    pass

# 2. Modelo Restaurant
class Restaurant(Base):
    __tablename__ = 'restaurant' 
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    
    # Relación inversa (opcional, pero recomendada)
    items: Mapped[list["MenuItem"]] = relationship(back_populates="restaurant")


# 3. Modelo MenuItem
class MenuItem(Base):
    __tablename__ = 'menu_item'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=True)
    price: Mapped[str] = mapped_column(String(8), nullable=True)
    course: Mapped[str] = mapped_column(String(250), nullable=True)
    
    # Foreign Key corregida con paréntesis () en lugar de []
    restaurant_id: Mapped[int] = mapped_column(ForeignKey('restaurant.id'))
    
    # Relación corregida
    restaurant: Mapped["Restaurant"] = relationship(back_populates="items")


# 4. Configuración del motor y creación de tablas
engine = create_engine('sqlite:///restaurantmenu.db')

# Corregido: es create_all (con guion bajo)
Base.metadata.create_all(engine)
