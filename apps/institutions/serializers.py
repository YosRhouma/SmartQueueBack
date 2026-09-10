from rest_framework import serializers

from .models import Institution


class InstitutionProfileSerializer(serializers.ModelSerializer):
    officialName = serializers.CharField(source='name')
    sector = serializers.CharField(source='category')
    logo = serializers.ImageField(required=False, allow_empty_file=False)
    website = serializers.URLField(required=False, allow_blank=True)
    Localisation = serializers.JSONField(write_only=True)
    Horaire = serializers.JSONField(write_only=True)

    class Meta:
        model = Institution
        fields = (
            'officialName', 'description', 'logo', 'sector', 'website', 'email', 'phone',
            'Localisation', 'Horaire',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['Localisation'] = {
            'governorate': instance.city,
            'address': instance.address,
            'postalCode': instance.postal_code,
        }
        data['Horaire'] = {
            'openingHours': instance.opening_hours,
            'closingHours': instance.closing_hours,
            'workingDays': instance.working_days,
            'isCurrentlyOpen': instance.is_currently_open,
        }
        return data

    def validate_Localisation(self, value):
        required = {'governorate', 'address', 'postalCode'}
        missing = required - value.keys()
        if missing:
            raise serializers.ValidationError(f"Missing fields: {', '.join(sorted(missing))}.")
        return value

    def validate_Horaire(self, value):
        required = {'openingHours', 'closingHours', 'workingDays', 'isCurrentlyOpen'}
        missing = required - value.keys()
        if missing:
            raise serializers.ValidationError(f"Missing fields: {', '.join(sorted(missing))}.")
        if not isinstance(value['workingDays'], list):
            raise serializers.ValidationError({'workingDays': 'Must be a list.'})
        if not isinstance(value['isCurrentlyOpen'], bool):
            raise serializers.ValidationError({'isCurrentlyOpen': 'Must be a boolean.'})
        return value

    def _flatten_nested_data(self, validated_data):
        localisation = validated_data.pop('Localisation', None)
        horaire = validated_data.pop('Horaire', None)
        if localisation:
            validated_data.update({
                'city': localisation['governorate'],
                'address': localisation['address'],
                'postal_code': localisation['postalCode'],
            })
        if horaire:
            validated_data.update({
                'opening_hours': horaire['openingHours'],
                'closing_hours': horaire['closingHours'],
                'working_days': horaire['workingDays'],
                'is_currently_open': horaire['isCurrentlyOpen'],
            })
        return validated_data

    def create(self, validated_data):
        return super().create(self._flatten_nested_data(validated_data))

    def update(self, instance, validated_data):
        return super().update(instance, self._flatten_nested_data(validated_data))
