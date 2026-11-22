from flask import Flask, abort, jsonify, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from werkzeug.exceptions import HTTPException

from models import Exercise, Workout, WorkoutExercise, db
from schemas import EntrySchema, ExerciseSchema, WorkoutSchema


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(SQLALCHEMY_DATABASE_URI="sqlite:///workouts.db")
    app.config.update(config or {})
    db.init_app(app)
    with app.app_context():
        if db.engine.dialect.name == "sqlite":
            @event.listens_for(db.engine, "connect")
            def enable_foreign_keys(connection, _):
                connection.execute("PRAGMA foreign_keys=ON")

    Migrate(app, db)

    @app.errorhandler(HTTPException)
    def http_error(error):
        return jsonify(error=error.description), error.code

    @app.errorhandler(ValidationError)
    def invalid_payload(error):
        return jsonify(errors=error.messages), 400

    @app.errorhandler(IntegrityError)
    def invalid_database_change(error):
        db.session.rollback()
        return jsonify(error="This change conflicts with an existing record or a database constraint."), 409

    def find(model, record_id):
        record = db.session.get(model, record_id)
        if record is None:
            abort(404, description=f"{model.__name__} {record_id} was not found.")
        return record

    def create(model, schema):
        data = schema.load(request.get_json())
        record = model(**data)
        db.session.add(record)
        db.session.commit()
        return jsonify(schema.dump(record)), 201

    def delete(model, record_id):
        db.session.delete(find(model, record_id))
        db.session.commit()
        return "", 204

    workout_schema = WorkoutSchema()
    exercise_schema = ExerciseSchema()
    entry_schema = EntrySchema()

    @app.get("/workouts")
    def list_workouts():
        query = db.select(Workout).order_by(Workout.id).options(
            selectinload(Workout.entries).selectinload(WorkoutExercise.exercise)
        )
        return jsonify(workout_schema.dump(db.session.scalars(query).all(), many=True))

    @app.get("/workouts/<int:workout_id>")
    def get_workout(workout_id):
        return jsonify(workout_schema.dump(find(Workout, workout_id)))

    @app.post("/workouts")
    def create_workout():
        return create(Workout, workout_schema)

    @app.delete("/workouts/<int:workout_id>")
    def delete_workout(workout_id):
        return delete(Workout, workout_id)

    @app.get("/exercises")
    def list_exercises():
        records = db.session.scalars(db.select(Exercise).order_by(Exercise.id)).all()
        return jsonify(exercise_schema.dump(records, many=True))

    @app.get("/exercises/<int:exercise_id>")
    def get_exercise(exercise_id):
        return jsonify(exercise_schema.dump(find(Exercise, exercise_id)))

    @app.post("/exercises")
    def create_exercise():
        return create(Exercise, exercise_schema)

    @app.delete("/exercises/<int:exercise_id>")
    def delete_exercise(exercise_id):
        return delete(Exercise, exercise_id)

    @app.post("/workouts/<int:workout_id>/exercises")
    def add_exercise(workout_id):
        workout = find(Workout, workout_id)
        data = entry_schema.load(request.get_json())
        exercise = find(Exercise, data.pop("exercise_id"))
        entry = WorkoutExercise(workout=workout, exercise=exercise, **data)
        db.session.add(entry)
        db.session.commit()
        return jsonify(entry_schema.dump(entry)), 201

    return app


