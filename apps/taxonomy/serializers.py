from rest_framework import serializers

from apps.taxonomy.models import TaxonomicLevel, Authorship


class AuthorshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Authorship
        fields = ['id', 'name']


class TaxonomicLevelSerializer(serializers.ModelSerializer):
    authorship = AuthorshipSerializer()
    rank = serializers.SerializerMethodField()
    parent_level = serializers.SerializerMethodField()

    def get_rank(self, obj):
        return obj.readable_rank()

    def get_parent_level(self, obj):
        if obj.parent:
            return TaxonomicLevelSerializer(obj.parent).data
        else:
            return None

    class Meta:
        model = TaxonomicLevel
        fields = ['id', 'name', 'rank', 'authorship', 'parent_level']
