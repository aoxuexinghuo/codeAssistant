from .extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(64), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "token": self.token,
            "createdAt": self.created_at.isoformat(),
        }


class UserProfile(db.Model):
    __tablename__ = "user_profile"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    nickname = db.Column(db.String(80), nullable=False, default="学习者")
    level = db.Column(db.String(40), nullable=False, default="初级")
    focus = db.Column(db.String(80), nullable=False, default="C语言")
    goal = db.Column(db.String(80), nullable=False, default="课程学习")
    answer_style = db.Column(db.String(80), nullable=False, default="简洁直接")
    weak_preference = db.Column(db.String(80), nullable=False, default="自动记录")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nickname": self.nickname,
            "level": self.level,
            "focus": self.focus,
            "goal": self.goal,
            "answerStyle": self.answer_style,
            "weakPreference": self.weak_preference,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }


class ConversationHistory(db.Model):
    __tablename__ = "conversation_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    mode = db.Column(db.String(32), nullable=False, index=True)
    mode_label = db.Column(db.String(64), nullable=False)
    question = db.Column(db.Text, nullable=False)
    reply = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "mode": self.mode,
            "modeLabel": self.mode_label,
            "question": self.question,
            "reply": self.reply,
            "createdAt": self.created_at.isoformat(),
        }


class MistakeRecord(db.Model):
    __tablename__ = "mistake_records"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    topic = db.Column(db.String(64), nullable=False, index=True)
    mode = db.Column(db.String(32), nullable=False, index=True)
    question = db.Column(db.Text, nullable=False)
    user_answer = db.Column(db.Text, nullable=False)
    reference_answer = db.Column(db.Text, nullable=False)
    mistake_type = db.Column(db.String(32), nullable=False, index=True)
    mistake_reason = db.Column(db.Text, nullable=False)
    improvement_suggestion = db.Column(db.Text, nullable=False)
    sort_order = db.Column(db.Integer, nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "topic": self.topic,
            "mode": self.mode,
            "question": self.question,
            "userAnswer": self.user_answer,
            "referenceAnswer": self.reference_answer,
            "mistakeType": self.mistake_type,
            "mistakeReason": self.mistake_reason,
            "improvementSuggestion": self.improvement_suggestion,
            "sortOrder": self.sort_order,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }
