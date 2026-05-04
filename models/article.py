from typing import Optional

from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.user import Base


class Article(Base):
    __tablename__ = 'article'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('user.id'), nullable=True)
    
    user: Mapped[Optional["User"]] = relationship("User", backref="articles")

    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title}', user_id={self.user_id})>"
