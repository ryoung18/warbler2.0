from project import db
import datetime

class Warbler(db.Model):
    __tablename__ = 'warblers'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id')
        )
    img_url = db.Column(db.Text)

    def __init__(self, message, img_url, user_id) :
        self.message = message
        self.img_url = img_url
        self.user_id = user_id

