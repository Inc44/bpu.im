from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any, Dict, List

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
from sqlalchemy import cast
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()
login_manager = LoginManager()


class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(63), unique=True, nullable=False)
	password_hash = db.Column(db.String(255), nullable=False)

	def set_password(self, password: str) -> None:
		self.password_hash = generate_password_hash(password)

	def check_password(self, password: str) -> bool:
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
	toc = db.Column(db.Text, default="[]")
	quiz = db.Column(db.Text, default="[]")

	def get_table_of_contents(self) -> List[str]:
		return json.loads(self.toc or "[]")

	def get_quiz(self) -> List[Dict[str, Any]]:
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
def load_user(id: str):
	return User.query.get(int(id))


def register_routes(app: Flask) -> None:
	@app.route("/")
	def index():
		articles = Article.query.order_by(Article.modified_at.desc()).all()
		return render_template("index.html", articles=articles)

	@app.route("/a/<slug>")
	def article(slug: str):
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
					cast(Article.modified_at, db.String).ilike(pattern),
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
			return make_response(
				render_template("login.html", error="Invalid credentials"), 401
			)
		return render_template("login.html")

	@app.route("/register", methods=["GET", "POST"])
	def register():
		if request.method == "POST":
			username = request.form.get("username", "").strip()
			password = request.form.get("password", "")
			if not username or not password:
				return render_template("register.html", error="Missing fields")
			if User.query.filter_by(username=username).first():
				return render_template("register.html", error="Username taken")
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
	def mark_read(slug: str):
		if not current_user.is_authenticated:
			return "", 204
		a = Article.query.filter_by(slug=slug).first()
		if not a:
			return "", 404
		if not Read.query.filter_by(user_id=current_user.id, article_id=a.id).first():
			db.session.add(Read(user_id=current_user.id, article_id=a.id))
			db.session.commit()
		return "", 204


def read_text(path: Path) -> str:
	with open(path, "r", encoding="utf-8") as file:
		return file.read()


def read_title(path: Path) -> str:
	return path.stem.strip().title()


def parse_table_of_contents(lines: List[str]) -> List[str]:
	toc = []
	for line in lines:
		line = line.lstrip()
		if line.startswith("#"):
			hash_count = len(line) - len(line.lstrip("#"))
			if 1 <= hash_count <= 6:
				header_text = line[hash_count:].strip()
				if header_text:
					header_anchor = header_text.replace(" ", "_")
					header_level = f"h{hash_count}"
					toc.append(
						{
							"text": header_text,
							"anchor": header_anchor,
							"level": header_level,
						}
					)
	return toc


def parse_article(path: Path) -> Dict[str, Any]:
	title = path.stem.strip().title()
	lines = read_text(path).splitlines()
	in_tags = False
	tags = []
	content_lines = []
	for line in lines:
		if line.strip() == "---":
			in_tags = not in_tags
			continue
		if in_tags:
			if line.strip().lower() == "tags:":
				continue
			if line.lstrip().startswith("-"):
				tag = line.lstrip()[1:].strip()
				if tag:
					tags.append(tag)
			continue
		content_lines.append(line)
	content = "\n".join(content_lines)
	toc = parse_table_of_contents(content_lines)
	return {
		"title": title,
		"slug": slugify(title),
		"modified_at": datetime.datetime.fromtimestamp(
			path.stat().st_mtime, tz=datetime.timezone.utc
		),
		"tags": ", ".join(tags),
		"content": content,
		"toc": toc,
	}


def parse_quiz(path: Path):
	pass


def load_articles(root: Path) -> None:
	for article_path in root.glob("*.md"):
		article_data = parse_article(article_path)
		quiz_path = article_path.parent / "quizzes" / f"{article_path.stem}.md"
		quiz_data = parse_quiz(quiz_path)
		article = Article.query.filter_by(slug=article_data["slug"]).first()
		if article is None:
			article = Article(slug=article_data["slug"], file_path=str(article_path))
			db.session.add(article)
		article.title = article_data["title"]
		article.modified_at = article_data["modified_at"]
		article.tags = article_data["tags"]
		article.content = article_data["content"]
		article.toc = json.dumps(article_data["toc"], indent="\t", ensure_ascii=False)
		article.quiz = json.dumps(quiz_data, indent="\t", ensure_ascii=False)
	db.session.commit()


def quiz_result(score: int, answers: List[Dict[str, bool]]) -> str:
	results = [
		f"<li>Q{idx+1}: {'Correct' if answer['ok'] else 'Incorrect'}</li>"
		for idx, answer in enumerate(answers)
	]
	return (
		f'<div class="border border-green-400 p-4 mt-4">'
		f'<p class="mb-2">Score: {score}%</p>'
		f'<ul class="list-disc pl-6 space-y-1">{"".join(results)}</ul></div>'
	)


if __name__ == "__main__":
	app = Flask(__name__)
	app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bpu.im.db"
	app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
	db.init_app(app)
	login_manager.init_app(app)
	with app.app_context():
		db.create_all()
		load_articles(Path(__file__).parent / "articles")
	register_routes(app)
	app.run()
