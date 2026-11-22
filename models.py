from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

db = SQLAlchemy()


def clean_name(value):
    if not isinstance(value, str) or not 1 <= len(value.strip()) <= 100:
        raise ValueError("Name must contain 1 to 100 characters.")
    return value.strip()


class Workout(db.Model):
    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    entries = db.relationship(
        "WorkoutExercise", back_populates="workout", cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.CheckConstraint("length(trim(name)) BETWEEN 1 AND 100", name="workout_name_length"),
    )

    @validates("name")
    def validate_name(self, key, value):
        return clean_name(value)


class Exercise(db.Model):
    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    entries = db.relationship(
        "WorkoutExercise", back_populates="exercise", cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.CheckConstraint("length(trim(name)) BETWEEN 1 AND 100", name="exercise_name_length"),
    )

    @validates("name")
    def validate_name(self, key, value):
        return clean_name(value)


class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercises"

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.ForeignKey("workouts.id"), nullable=False)
    exercise_id = db.Column(db.ForeignKey("exercises.id"), nullable=False, index=True)
    sets = db.Column(db.Integer)
    reps = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)
    workout = db.relationship("Workout", back_populates="entries")
    exercise = db.relationship("Exercise", back_populates="entries")

    __table_args__ = (
        db.UniqueConstraint("workout_id", "exercise_id", name="unique_workout_exercise"),
        db.CheckConstraint("sets > 0 AND reps > 0 OR sets IS NULL AND reps IS NULL", name="positive_set_rep_pair"),
        db.CheckConstraint("duration_seconds > 0", name="positive_duration"),
        db.CheckConstraint(
            "(sets IS NOT NULL AND reps IS NOT NULL) OR "
            "(sets IS NULL AND reps IS NULL AND duration_seconds IS NOT NULL)",
            name="required_exercise_details",
        ),
    )

    @validates("sets", "reps", "duration_seconds")
    def validate_count(self, key, value):
        if value is not None and (type(value) is not int or value < 1):
            raise ValueError(f"{key} must be a positive integer.")
        return value

