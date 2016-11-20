# -*- coding: utf-8 -*-

from db import session_scope, Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm.exc import NoResultFound

class User(Base):
    __tablename__ = 'users'

    id    = Column(Integer, primary_key=True)
    name  = Column(String)
    score = Column(Integer)

    def __repr__(self):
        return '<User(name=\'%s\', score=\'%s\')>' % (self.name, self.score)

    @staticmethod
    def find_or_create(nickname):
        """
            Helper function, gets an user or create it if it doesn't
            exist already in the database.
        """
        with session_scope() as session:
            try:
                return session.query(User) \
                    .filter(User.name.ilike(nickname)) \
                    .one()
            except NoResultFound:
                user = User(name=nickname, score=0)
                session.add(user)
                return user

    def add_score(self, score):
        """
            Adds score to the score. Automatically wraps the write in
            a transaction
        """
        with session_scope() as session:
            self.score += score
            session.add(self)
        return self.score

