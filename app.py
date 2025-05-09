from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, AnyOf
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# データベースの初期化
users = {}
activities = {}
achievements = {}

# ユーザーモデル
class User(UserMixin):
    def __init__(self, id, username, password, role):
        self.id = id
        self.username = username
        self.password = password
        self.role = role

# ユーザーの読み込み
@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

# ログインフォーム
class LoginForm(FlaskForm):
    username = StringField('ユーザー名', validators=[DataRequired()])
    password = PasswordField('パスワード', validators=[DataRequired()])
    submit = SubmitField('ログイン')

# 登録フォーム
class RegisterForm(FlaskForm):
    username = StringField('ユーザー名', validators=[DataRequired()])
    password = PasswordField('パスワード', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('パスワードの確認', validators=[DataRequired(), EqualTo('password')])
    role = StringField(
        '役割 (学生or教員)',
        validators=[
            DataRequired(),
            AnyOf(['学生', '教員'], message='役割は「学生」または「教員」を選択してください')
        ]
    )
    submit = SubmitField('登録')

# 活動記録フォーム
class ActivityForm(FlaskForm):
    activity = TextAreaField('活動内容', validators=[DataRequired()])
    days_spent = StringField('日数', validators=[DataRequired()])
    submit = SubmitField('記録')

# 実績記録フォーム
class AchievementForm(FlaskForm):
    achievement = TextAreaField('実績内容', validators=[DataRequired()])
    submit = SubmitField('記録')

# ルートページ
@app.route('/')
def index():
    return render_template('index.html')

# ログインページ
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = None
        for u in users.values():
            if u.username == form.username.data and u.password == form.password.data:
                user = u
                break
        if user:
            login_user(user)
            flash('ログインしました', 'success')
            if user.role == '学生':
                return redirect(url_for('student'))
            elif user.role == '教員':
                return redirect(url_for('faculty'))
            else:
                return redirect(url_for('index'))
        else:
            flash('ユーザー名またはパスワードが違います', 'danger')
    return render_template('login.html', form=form)

# 登録ページ
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.username.data in [u.username for u in users.values()]:
            flash('そのユーザー名は既に使用されています', 'danger')
        else:
            new_user = User(len(users) + 1, form.username.data, form.password.data, form.role.data)
            users[new_user.id] = new_user
            flash('登録が完了しました！', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)

# ログアウト
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('ログアウトしました', 'success')
    return redirect(url_for('index'))

# 学生用ページ
@app.route('/student', methods=['GET', 'POST'])
@login_required
def student():
    if current_user.role != '学生':
        flash('このページへのアクセス権限がありません。', 'danger')
        return redirect(url_for('index'))
    form = ActivityForm()
    if form.validate_on_submit():
        activity = {
            'user': current_user.username,
            'content': form.activity.data,
            'days': form.days_spent.data
        }
        activities[len(activities) + 1] = activity
        flash('活動を記録しました！', 'success')
        return redirect(url_for('student'))
    return render_template('student.html', form=form)

# 教員用ページ
@app.route('/faculty', methods=['GET', 'POST'])
@login_required
def faculty():
    if current_user.role != '教員':
        flash('このページへのアクセス権限がありません。', 'danger')
        return redirect(url_for('index'))
    form = AchievementForm()
    if form.validate_on_submit():
        achievement = {
            'user': current_user.username,
            'content': form.achievement.data,
        }
        achievements[len(achievements) + 1] = achievement
        flash('実績を記録しました！', 'success')
        return redirect(url_for('faculty'))
    return render_template('faculty.html', form=form)

# データ閲覧ページ
@app.route('/view_data')
@login_required
def view_data():
    return render_template('view_data.html', activities=activities, achievements=achievements)

if __name__ == '__main__':
    app.run(debug=True)
