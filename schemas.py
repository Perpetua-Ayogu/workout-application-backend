from marshmallow import Schema, ValidationError, fields, pre_load, validate, validates_schema


class NamedSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))

    @pre_load
    def strip_name(self, data, **kwargs):
        if isinstance(data, dict) and isinstance(data.get("name"), str):
            return {**data, "name": data["name"].strip()}
        return data


class ExerciseSchema(NamedSchema):
    pass


class EntrySchema(Schema):
    id = fields.Integer(dump_only=True)
    exercise_id = fields.Integer(required=True, strict=True, validate=validate.Range(min=1))
    sets = fields.Integer(strict=True, validate=validate.Range(min=1))
    reps = fields.Integer(strict=True, validate=validate.Range(min=1))
    duration_seconds = fields.Integer(strict=True, validate=validate.Range(min=1))
    exercise = fields.Nested(ExerciseSchema, dump_only=True)

    @validates_schema
    def validate_details(self, data, **kwargs):
        if ("sets" in data) != ("reps" in data):
            raise ValidationError("Send sets and reps together.")
        if "sets" not in data and "duration_seconds" not in data:
            raise ValidationError("Send sets and reps, a duration, or both.")


class WorkoutSchema(NamedSchema):
    date = fields.Date(required=True)
    entries = fields.List(fields.Nested(EntrySchema), dump_only=True)

