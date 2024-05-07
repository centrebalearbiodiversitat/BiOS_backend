from rest_framework import serializers

from apps.taxonomy.models import TaxonomicLevel, Authorship

class ParentSerializer(serializers.ModelSerializer):
	scientificNameAuthorship = serializers.CharField(source = 'verbatim_authorship')
	taxonRank = serializers.CharField(source = 'rank')
	parent = serializers.SerializerMethodField()

	def get_parent(self, obj):
		if obj.parent:
			parent = TaxonomicLevelSerializer(obj.parent).data
			del parent['children']
			return parent
		else: 
			return None


	class Meta:
		model = TaxonomicLevel
		fields = ['id', 'name', 'taxonRank', 'scientificNameAuthorship', 'parent']

class ChildrenSerializer(serializers.ModelSerializer):
	scientificNameAuthorship = serializers.CharField(source='verbatim_authorship')
	taxonRank = serializers.CharField(source='rank')

	def get_children(self, obj):
		if obj.children:
			return TaxonomicLevelSerializer(obj.children).data
		else: 
			return None


	class Meta:
		model = TaxonomicLevel
		fields = ['id', 'name', 'taxonRank', 'scientificNameAuthorship']


class TaxonomicLevelSerializer(serializers.ModelSerializer):
	children = ChildrenSerializer(many = True)
	parent = ParentSerializer(many = False)
	scientificNameAuthorship = serializers.CharField(source='verbatim_authorship')
	taxonRank = serializers.CharField(source='rank')

	class Meta:
		model = TaxonomicLevel
		fields = ['id', 'name', 'taxonRank', 'scientificNameAuthorship', 'parent', 'children']

