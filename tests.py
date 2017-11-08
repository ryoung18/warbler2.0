import unittest
from flask_testing import TestCase
from project import app, db
from project.users.models import User

class TestCase(TestCase):

    def create_app(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testing.db'
        app.config['ENV'] = 'testing'
        return app

    def setUp(self):
        db.drop_all()
        db.create_all()
        u1 = User(email='john@example.com', username='john', name='john', password='john')
        u2 = User(email='susan@example.com', username='susan', name='susan', password='susan')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

    def tearDown(self):
        db.drop_all()

    def test_initial(self):
        u1 = User.query.filter(User.id == 1).first()
        u2 = User.query.filter(User.id == 2).first()
        self.assertIsNone(u1.unfollow(u2))

    def test_follow(self):
        u1 = User.query.filter(User.id == 1).first()
        u2 = User.query.filter(User.id == 2).first()
        u = u1.follow(u2)
        db.session.add(u)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'susan')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'john')

    # def test_unfollow(self):
    #     u1 = User.query.filter(User.id == 1).first()
    #     u2 = User.query.filter(User.id == 2).first()
    #     u = u1.unfollow(u2)
    #     db.session.add(u)
    #     db.session.commit()
    #     self.assertFalse(u1.is_following(u2))
    #     self.assertEqual(u1.followed.count(), 0)
    #     self.assertEqual(u2.followers.count(), 0)

if __name__ == "__main__":
    unittest.main()
