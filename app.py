from __future__ import annotations

import datetime

from flask import Flask
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()
login_manager = LoginManager()


class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(63), unique=True, nullable=False)
	password_hash = db.Column(db.String(255), nullable=False)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)


class Article(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	file_path = db.Column(db.String(260), nullable=False)


class Read(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
	article_id = db.Column(db.Integer, db.ForeignKey("article.id"), nullable=False)
	read_at = db.Column(
		db.DateTime, default=datetime.datetime.now(datetime.timezone.utc)
	)
	__table_args__ = (
		db.UniqueConstraint("user_id", "article_id", name="unique_user_article_read"),
	)


class Quiz(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
	article_id = db.Column(db.Integer, db.ForeignKey("article.id"), nullable=False)
	score = db.Column(db.Integer, nullable=False)
	taken_at = db.Column(
		db.DateTime, default=datetime.datetime.now(datetime.timezone.utc)
	)


@login_manager.user_loader
def load_user(id):
	return User.query.get(int(id))


def quiz_result(score, answers):
	results = []
	for idx, answer in enumerate(answers, start=1):
		state = "Correct" if answer["ok"] else "Incorrect"
		results.append(f"<li>Q{idx}: {state}</li>")
	result = '<ul class="list-disc pl-6 space-y-1">' + "".join(results) + "</ul>"
	return f'<div class="border border-green-400 p-4 mt-4"><p class="mb-2">Score: {score}%</p>{result}</div>'


if __name__ == "__main__":
	app = Flask(__name__)
	app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bpu.im.db"
	app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
	db.init_app(app)
	login_manager.init_app(app)
	with app.app_context():
		db.create_all()
	app.run()
