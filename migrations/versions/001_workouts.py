"""Create workouts, exercises, and their associations."""

from alembic import op
import sqlalchemy as sa

revision = "001_workouts"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "workouts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.CheckConstraint("length(trim(name)) BETWEEN 1 AND 100", name="workout_name_length"),
    )
    op.create_table(
        "exercises",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.CheckConstraint("length(trim(name)) BETWEEN 1 AND 100", name="exercise_name_length"),
    )
    op.create_table(
        "workout_exercises",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("workout_id", sa.Integer(), sa.ForeignKey("workouts.id"), nullable=False),
        sa.Column("exercise_id", sa.Integer(), sa.ForeignKey("exercises.id"), nullable=False),
        sa.Column("sets", sa.Integer()),
        sa.Column("reps", sa.Integer()),
        sa.Column("duration_seconds", sa.Integer()),
        sa.UniqueConstraint("workout_id", "exercise_id", name="unique_workout_exercise"),
        sa.CheckConstraint("sets > 0 AND reps > 0 OR sets IS NULL AND reps IS NULL", name="positive_set_rep_pair"),
        sa.CheckConstraint("duration_seconds > 0", name="positive_duration"),
        sa.CheckConstraint(
            "(sets IS NOT NULL AND reps IS NOT NULL) OR "
            "(sets IS NULL AND reps IS NULL AND duration_seconds IS NOT NULL)",
            name="required_exercise_details",
        ),
    )
    op.create_index("ix_workout_exercises_exercise_id", "workout_exercises", ["exercise_id"])


def downgrade():
    op.drop_index("ix_workout_exercises_exercise_id", table_name="workout_exercises")
    op.drop_table("workout_exercises")
    op.drop_table("exercises")
    op.drop_table("workouts")
