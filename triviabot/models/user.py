# -*- coding: utf-8 -*-

from db import session_scope, Base
from sqlalchemy import Column, Integer, String

class User(Base):
    __tablename__ = 'users'

    id    = Column(Integer, primary_key=True)
    name  = Column(String)
    score = Column(Integer)

    def __repr__(self):
        return '<User(name=\'%s\', score=\'%s\')>' % (self.name, self.score)

    @staticmethod
    def get_or_create(nickname):
        """
            Helper function, gets an user or create it if it doesn't
            exist already in the database.
        """
        with session_scope() as session:
            return session.query(User).filter(User.name.ilike(nick)).one()

    def add_score(self, score):
        """
            Adds score to the score. Automatically wraps the write in
            a transaction
        """
        with session_scope() as session:
            self.score += score
        return self.score

