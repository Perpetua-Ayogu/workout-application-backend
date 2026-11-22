# Workout Application Backend

I built this API to keep workouts and exercises organized. An exercise can be reused in multiple workouts, and each workout tracks its own sets, reps, or duration for that exercise.

## Set up and run

Use Python 3.8.13 or newer and Pipenv. From the project folder, run:

```bash
pipenv install
pipenv run flask --app app db upgrade
pipenv run python seed.py
pipenv run flask --app app run
```

The server runs at http://127.0.0.1:5000. SQLite stores the local database in the instance folder. The seed script adds a full-body workout and a core workout with a shared plank exercise.

| Method | Path | What it does |
| --- | --- | --- |
| GET | /workouts | List workouts with their exercises |
| GET | /workouts/<id> | View one workout |
| POST | /workouts | Create a workout with a name and ISO date |
| DELETE | /workouts/<id> | Delete a workout and its links |
| GET | /exercises | List reusable exercises |
| GET | /exercises/<id> | View one exercise |
| POST | /exercises | Create an exercise with a name |
| DELETE | /exercises/<id> | Delete an exercise and its links |
| POST | /workouts/<id>/exercises | Add an existing exercise to a workout |

Example JSON to create a workout:

```json
{"name": "Leg Day", "date": "2026-01-07"}
```

Example JSON to add exercise 1 to a workout:

```json
{"exercise_id": 1, "sets": 3, "reps": 10}
```

For a timed exercise, send a positive integer in `duration_seconds`. Sets and reps must be supplied together. Validation errors return 400, missing records return 404, and conflicting records return 409.

