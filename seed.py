from datetime import date

from app import create_app
from models import Exercise, Workout, WorkoutExercise, db


def seed():
    with create_app().app_context():
        for name, workout_date, exercise_name, details in (
            ("Full Body", date(2026, 1, 5), "Squat", {"sets": 3, "reps": 10}),
            ("Core", date(2026, 1, 6), "Plank", {"duration_seconds": 45}),
            ("Full Body", date(2026, 1, 5), "Plank", {"duration_seconds": 30}),
        ):
            workout = Workout.query.filter_by(name=name, date=workout_date).first()
            if workout is None:
                workout = Workout(name=name, date=workout_date)
                db.session.add(workout)
            exercise = Exercise.query.filter_by(name=exercise_name).first()
            if exercise is None:
                exercise = Exercise(name=exercise_name)
                db.session.add(exercise)
            db.session.flush()

            if WorkoutExercise.query.filter_by(workout_id=workout.id, exercise_id=exercise.id).first() is None:
                db.session.add(WorkoutExercise(workout=workout, exercise=exercise, **details))

        db.session.commit()


if __name__ == "__main__":
    seed()

