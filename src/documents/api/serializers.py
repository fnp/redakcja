from rest_framework import serializers
from .. import models


class TextField(serializers.Field):
    def get_attribute(self, instance):
        return instance

    def to_representation(self, value):
        return value.materialize()

    def to_internal_value(self, data):
        return data


class BookSerializer(serializers.ModelSerializer):
    id = serializers.HyperlinkedIdentityField(view_name='documents_api_book')

    class Meta:
        model = models.Book
        fields = [
            'id',
            'title'
        ]


class ChunkSerializer(serializers.ModelSerializer):
    id = serializers.HyperlinkedIdentityField(view_name='documents_api_chunk')
    book = serializers.HyperlinkedRelatedField(view_name='documents_api_book', read_only=True)
    revisions = serializers.HyperlinkedIdentityField(view_name='documents_api_chunk_revision_list')
    head = serializers.HyperlinkedRelatedField(view_name='documents_api_revision', read_only=True)
    ## RelatedField

    class Meta:
        model = models.Chunk
        fields = ['id', 'book', 'revisions', 'head', 'user', 'stage']


class RHRF(serializers.HyperlinkedRelatedField):
    def get_queryset(self):
        return self.context['chunk'].change_set.all();

  
class RevisionSerializer(serializers.ModelSerializer):
    id = serializers.HyperlinkedIdentityField(view_name='documents_api_revision')
    parent = RHRF(
        view_name='documents_api_revision',
        queryset=models.Chunk.change_model.objects.all()
    )
    merge_parent = RHRF(
        view_name='documents_api_revision',
        read_only=True
    )
    chunk = serializers.HyperlinkedRelatedField(view_name='documents_api_chunk', read_only=True, source='tree')
    author = serializers.SerializerMethodField()

    class Meta:
        model = models.Chunk.change_model
        fields = ['id', 'chunk', 'created_at', 'author', 'author_email', 'author_name', 'parent', 'merge_parent']
        read_only_fields = ['author_email', 'author_name']

    def get_author(self, obj):
        return obj.author.username if obj.author is not None else None
        

class BookDetailSerializer(BookSerializer):
    chunk = ChunkSerializer(many=True, source='chunk_set')

    class Meta:
        model = models.Book
        fields = BookSerializer.Meta.fields + ['chunk']



class ChunkDetailSerializer(ChunkSerializer):
    pass


class RevisionDetailSerializer(RevisionSerializer):
    text = TextField()

    class Meta(RevisionSerializer.Meta):
        fields = RevisionSerializer.Meta.fields + ['description', 'text']

    def create(self, validated_data):
        chunk = self.context['chunk']
        return chunk.commit(
            validated_data['text'],
            author=self.context['request'].user, # what if anonymous?
            description=validated_data['description'],
            parent=validated_data.get('parent'),
        )
