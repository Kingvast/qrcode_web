from marshmallow import Schema, ValidationError, fields, post_load


class RequestFormSchema(Schema):
    app_name = fields.Str(required=True)
    version = fields.Str(required=True)
    type = fields.Str(required=True)
    bundle_id = fields.Str(missing='')
    package_name = fields.Str(missing='')
    md5 = fields.Str(required=True)

    def get_attribute(self, obj, key, default):
        return obj.get(key, default)[0]

    @post_load
    def validate_one_of_unique_field_must_exist(self, validate_form_data):
        try:
            if bool(validate_form_data['bundle_id']) != bool(
                    validate_form_data['package_name']):
                return validate_form_data
        except KeyError:
            raise ValidationError(
                "Only one of bundle_id and package_name must exist")
