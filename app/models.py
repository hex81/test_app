from . import db
# from . import login_manager
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_login import UserMixin, AnonymousUserMixin
# from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# from flask import current_app
from datetime import datetime
# from markdown import markdown
# import bleach


class TRTFailedRecord(db.Model):
    __tablename__ = 'trt_failed_record'
    id = db.Column(db.Integer, primary_key=True)
    job = db.Column(db.String(200))
    case_name = db.Column(db.String(300))
    url = db.Column(db.String(300))
    category = db.Column(db.String(300), default='')
    nvbug = db.Column(db.String(64), default='')
    version = db.Column(db.String(64))
    trt = db.Column(db.String(64))
    driver = db.Column(db.String(64))
    cuda = db.Column(db.String(64))
    cudnn = db.Column(db.String(64))
    platform = db.Column(db.String(64))
    os = db.Column(db.String(64))
    arch = db.Column(db.String(64))
    date = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def insert_cases(records):
        for r in records:
            job = r['job']
            case_name = r['case_name']
            url = r['url']
            trt = r['trt']
            driver = r['driver']
            cuda = r['cuda']
            cudnn = r['cudnn']
            platform = r['gpu']
            os = r['os']
            arch = r['arch']
            version = ".".join(trt.split(".")[:2])

            case_record = TRTFailedRecord.query.filter_by(
                job=r['job'], case_name=r['case_name']).first()
            if case_record is None:
                case_record = TRTFailedRecord(job=job, case_name=case_name, 
                    url=url, version=version, trt=trt, driver=driver,
                    cuda=cuda, cudnn=cudnn, platform=platform, os=os, arch=arch)
            else:
                case_record.category = r.get('category', '')
                case_record.nvbug = r.get('nvbug', '')

            db.session.add(case_record)

        db.session.commit()

        return

    @staticmethod
    def update_case(id, category=None, nvbug=None):
        record = TRTFailedRecord.query.filter_by(id=id).first()

        if record:
            if category:
                record.category = category

            if nvbug:
                record.nvbug = nvbug

            db.session.add(record)
            db.session.commit()

        return


# class Follow(db.Model):
#     __tablename__ = 'follows'
#     follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
#                             primary_key=True)
#     followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
#                             primary_key=True)
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# class User(UserMixin, db.Model):
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(64), unique=True, index=True)
#     username = db.Column(db.String(64), unique=True, index=True)
#     password_hash = db.Column(db.String(128))
#     role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
#     confirmed = db.Column(db.Boolean, default=False)
#     name = db.Column(db.String(64))
#     location = db.Column(db.String(64))
#     about_me = db.Column(db.Text())
#     member_since = db.Column(db.DateTime(), default=datetime.utcnow)
#     last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
#     posts = db.relationship('Post', backref='author', lazy='dynamic')
#     followed = db.relationship('Follow',
#                                foreign_keys=[Follow.follower_id],
#                                backref=db.backref('follower', lazy='joined'),
#                                lazy='dynamic',
#                                cascade='all, delete-orphan')

#     followers = db.relationship('Follow',
#                                 foreign_keys=[Follow.followed_id],
#                                 backref=db.backref('followed', lazy='joined'),
#                                 lazy='dynamic',
#                                 cascade='all, delete-orphan')
#     comments = db.relationship('Comment', backref='author', lazy='dynamic')

#     def __init__(self, **kwargs):
#         super(User, self).__init__(**kwargs)
#         if self.role is None:
#             if self.email == current_app.config['FLASKY_ADMIN']:
#                 self.role = Role.query.filter_by(name='Administrator').first()
#             if self.role is None:
#                 self.role = Role.query.filter_by(default=True).first()
#         self.follow(self)
#         return

#     def __repr__(self):
#         return '<User %r>' % self.username

#     @property
#     def password(self):
#         raise AttributeError('password is not a readable attribute')

#     @password.setter
#     def password(self, password):
#         self.password_hash = generate_password_hash(password)

#     @property
#     def followed_posts(self):
#         return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
#             .filter(Follow.follower_id == self.id)

#     @staticmethod
#     def add_self_follows():
#         for user in User.query.all():
#             if not user.is_following(user):
#                 user.follow(user)
#                 db.session.add(user)
#                 db.session.commit()

#     def verify_password(self, password):
#         return check_password_hash(self.password_hash, password)

#     def generate_confirmation_token(self, expiration=3600):
#         s = Serializer(current_app.config['SECRET_KEY'], expiration)
#         return s.dumps({'confirm': self.id}).decode('utf-8')

#     def confirm(self, token):
#         s = Serializer(current_app.config['SECRET_KEY'])
#         try:
#             data = s.loads(token.encode('utf-8'))
#         except Exception as e:
#             print ('Exception: {}').format(e)
#             return False

#         if data.get('confirm') != self.id:
#             return False
#         self.confirmed = True
#         db.session.add(self)
#         return True

#     def can(self, perm):
#         return self.role is not None and self.role.has_permission(perm)

#     def is_administrator(self):
#         return self.can(Permission.ADMIN)

#     def ping(self):
#         self.last_seen = datetime.utcnow()
#         db.session.add(self)
#         db.session.commit()

#     def follow(self, user):
#         if not self.is_following(user):
#             f = Follow(follower=self, followed=user)
#             db.session.add(f)

#     def unfollow(self, user):
#         f = self.followed.filter_by(followed_id=user.id).first()
#         if f:
#             db.session.delete(f)

#     def is_following(self, user):
#         if user.id is None:
#             return False
#         return self.followed.filter_by(followed_id=user.id).first() is not None

#     def is_followed_by(self, user):
#         if user.id is None:
#             return False
#         return self.followers.filter_by(follower_id=user.id).first() is not None


# class Post(db.Model):
#     __tablename__ = 'posts'
#     id = db.Column(db.Integer, primary_key=True)
#     body = db.Column(db.Text)
#     body_html = db.Column(db.Text)
#     timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
#     author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#     comments = db.relationship('Comment', backref='post', lazy='dynamic')

#     @staticmethod
#     def on_changed_body(target, value, oldvalue, initiator):
#         allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
#          'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1',
#          'h2', 'h3', 'p']
#         target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'), tags=allowed_tags, strip=True))


# db.event.listen(Post.body, 'set', Post.on_changed_body)


# class Comment(db.Model):
#     __tablename__ = 'comments'
#     id = db.Column(db.Integer, primary_key=True)
#     body = db.Column(db.Text)
#     body_html = db.Column(db.Text)
#     timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
#     disabled = db.Column(db.Boolean)
#     author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#     post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

#     @staticmethod
#     def on_change_body(target, value, oldvalue, initiator):
#         allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
#                         'strong']
#         target.body_html = bleach.linkify(bleach.clean(
#             markdown(value, output_format='html'),
#             tags=allowed_tags, strip=True))


# db.event.listen(Comment.body, 'set', Comment.on_change_body)


# class AnonymousUser(AnonymousUserMixin):

#     def can(self, permissions):
#         return False

#     def is_administrator(self):
#         return False


# login_manager.anonymous_user = AnonymousUser


# class Permission:
#     FOLLOW = 1
#     COMMENT = 2
#     WRITE = 4
#     MODERATE = 8
#     ADMIN = 16


# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))
