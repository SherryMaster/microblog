from datetime import datetime, timedelta, timezone
import os
import unittest

# Set these before importing the Flask application.  Flask-SQLAlchemy creates
# its engine during application initialization, so changing the database URI
# afterward would be too late and could accidentally target app.db.
os.environ['DATABASE_URL'] = 'sqlite://'
os.environ['FLASK_DEBUG'] = '1'

from app import app, db
from app.models import Post, User


class UserModelCase(unittest.TestCase):
    def setUp(self):
        # The in-memory database is isolated from the development app.db.
        app.config['TESTING'] = True
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_password_hashing(self):
        with app.app_context():
            user = User(username='susan')
            user.set_password('cat')
            self.assertFalse(user.check_password('dog'))
            self.assertTrue(user.check_password('cat'))

    def test_avatar(self):
        with app.app_context():
            user = User(username='john', email='john@example.com')
            self.assertEqual(
                user.avatar(128),
                'https://www.gravatar.com/avatar/'
                'd4c74594d841139328695756648b6bd6'
                '?d=identicon&s=128',
            )

    def test_follow(self):
        with app.app_context():
            user1 = User(username='john', email='john@example.com')
            user2 = User(username='susan', email='susan@example.com')
            db.session.add_all([user1, user2])
            db.session.commit()

            self.assertEqual(user1.followed.all(), [])
            self.assertEqual(user1.followers.all(), [])

            user1.follow(user2)
            db.session.commit()
            self.assertTrue(user1.is_following(user2))
            self.assertEqual(user1.followed.count(), 1)
            self.assertEqual(user1.followed.first().username, 'susan')
            self.assertEqual(user2.followers.count(), 1)
            self.assertEqual(user2.followers.first().username, 'john')

            # Repeating follow must not create another relationship row.
            user1.follow(user2)
            db.session.commit()
            self.assertEqual(user1.followed.count(), 1)

            user1.unfollow(user2)
            db.session.commit()
            self.assertFalse(user1.is_following(user2))
            self.assertEqual(user1.followed.count(), 0)
            self.assertEqual(user2.followers.count(), 0)

    def test_follow_posts(self):
        with app.app_context():
            user1 = User(username='john', email='john@example.com')
            user2 = User(username='susan', email='susan@example.com')
            user3 = User(username='mary', email='mary@example.com')
            user4 = User(username='david', email='david@example.com')
            db.session.add_all([user1, user2, user3, user4])

            now = datetime.now(timezone.utc).replace(tzinfo=None)
            post1 = Post(
                body='post from john',
                author=user1,
                timestamp=now + timedelta(seconds=1),
            )
            post2 = Post(
                body='post from susan',
                author=user2,
                timestamp=now + timedelta(seconds=4),
            )
            post3 = Post(
                body='post from mary',
                author=user3,
                timestamp=now + timedelta(seconds=3),
            )
            post4 = Post(
                body='post from david',
                author=user4,
                timestamp=now + timedelta(seconds=2),
            )
            db.session.add_all([post1, post2, post3, post4])
            db.session.commit()

            user1.follow(user2)  # john follows susan
            user1.follow(user4)  # john follows david
            user2.follow(user3)  # susan follows mary
            user3.follow(user4)  # mary follows david
            db.session.commit()

            self.assertEqual(user1.followed_posts().all(), [post2, post4, post1])
            self.assertEqual(user2.followed_posts().all(), [post2, post3])
            self.assertEqual(user3.followed_posts().all(), [post3, post4])
            self.assertEqual(user4.followed_posts().all(), [post4])


if __name__ == '__main__':
    unittest.main(verbosity=2)
