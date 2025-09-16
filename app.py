from __future__ import annotations

import datetime
import json
import os

from flask import (
	Flask,
	abort,
	make_response,
	redirect,
	render_template,
	url_for,
	request,
)
from flask_login import (
	LoginManager,
	UserMixin,
	login_user,
	login_required,
	logout_user,
	current_user,
)
from flask_sqlalchemy import SQLAlchemy
from slugify import slugify
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
	title = db.Column(db.String(255), nullable=False)
	slug = db.Column(db.String(255), unique=True, nullable=False)
	modified_at = db.Column(
		db.DateTime, default=datetime.datetime.now(datetime.timezone.utc)
	)
	tags = db.Column(db.String(255), default="")
	content = db.Column(db.Text, default="")
	table_of_contents = db.Column(db.Text, default="[]")
	quiz = db.Column(db.Text, default="[]")

	def get_table_of_contents(self):
		return json.loads(self.table_of_contents or "[]")

	def get_quiz(self):
		return json.loads(self.quiz or "[]")


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


def register_routes(app):
	@app.route("/")
	def index():
		articles = Article.query.order_by(Article.modified_at.desc()).all()
		return render_template("index.html", articles=articles)

	@app.route("/a/<slug>")
	def article(slug):
		a = Article.query.filter_by(slug=slug).first()
		if not a:
			abort(404)
		return render_template("components/article.html", article=a)

	@app.route("/search")
	def search():
		q = request.args.get("q", "").strip()
		if not q:
			return render_template("search.html", query=q, results=[])
		pattern = f"%{q}%"
		results = (
			Article.query.filter(
				db.or_(
					Article.title.ilike(pattern),
					Article.modified_at.ilike(pattern),
					Article.tags.ilike(pattern),
					Article.content.ilike(pattern),
				)
			)
			.order_by(Article.modified_at.desc())
			.all()
		)
		return render_template("search.html", query=q, results=results)

	@app.route("/login", methods=["GET", "POST"])
	def login():
		if request.method == "POST":
			username = request.form.get("username", "").strip()
			password = request.form.get("password", "")
			user = User.query.filter_by(username=username).first()
			if user and user.check_password(password):
				login_user(user)
				return redirect(url_for("index"))
			return make_response(render_template("login.html"))
		return render_template("login.html")

	@app.route("/register", methods=["GET", "POST"])
	def register():
		if request.method == "POST":
			username = request.form.get("username", "").strip()
			password = request.form.get("password", "")
			if not username or not password:
				return render_template("register.html")
			user = User.query.filter_by(username=username).first()
			if user:
				return render_template("register.html")
			user = User(username=username)
			user.set_password(password)
			db.session.add(user)
			db.session.commit()
			login_user(user)
			return redirect(url_for("index"))
		return render_template("register.html")

	@app.route("/logout")
	@login_required
	def logout():
		logout_user()
		return redirect(url_for("index"))

	@app.route("/profile")
	@login_required
	def profile():
		read_articles = (
			db.session.query(Article)
			.join(Read, Article.id == Read.article_id)
			.filter(Read.user_id == current_user.id)
			.order_by(Article.modified_at.desc())
			.all()
		)
		taken_quizzes = (
			Quiz.query.filter_by(user_id=current_user.id)
			.order_by(Quiz.taken_at.desc())
			.all()
		)
		average_score = 0
		if taken_quizzes:
			total_score = sum(taken_quiz.score for taken_quiz in taken_quizzes)
			average_score = round(total_score / len(taken_quizzes))
		return render_template(
			"profile.html",
			read_articles=read_articles,
			taken_quizzes=taken_quizzes,
			average_score=average_score,
		)

	@app.route("/new_password", methods=["POST"])
	@login_required
	def new_password():
		password = request.form.get("password", "")
		if password:
			current_user.set_password(password)
			db.session.commit()
		return redirect(url_for("profile"))

	@app.route("/mark_read/<slug>", methods=["POST"])
	def mark_read(slug):
		if not current_user.is_authenticated:
			return "", 204
		a = Article.query.filter_by(slug=slug).first()
		if not a:
			return "", 404
		marked = Read.query.filter_by(user_id=current_user.id, article_id=a.id).first()
		if not marked:
			db.session.add(Read(user_id=current_user.id, article_id=a.id))
			db.session.commit()
		return "", 204


def read_text(path):
	with open(path, "r", encoding="utf-8") as file:
		return file.read()


def read_title(path):
	return str(os.path.splitext(os.path.basename(path))[0]).strip().title()


def parse_table_of_contents(lines):
	table = []
	for line in lines:
		line = line.lstrip()
		if line.startswith("#"):
			hash_count = 0
			while hash_count < len(line) and line[hash_count] == "#":
				hash_count += 1
			if 1 <= hash_count <= 6:
				header_text = line[hash_count:].strip()
				header_level = f"h{hash_count}"
				table.append((header_level, header_text))
	return table


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
	register_routes(app)
	app.run()
