from rest_framework import serializers
from kanban_app.models import Board, Member, Task, Comment
from rest_framework import serializers, viewsets

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['id', 'email', 'fullname']


class TaskListSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField(read_only=True)
    reviewer = MemberSerializer(many=False, read_only=True)
    assignee = MemberSerializer(many=False, read_only=True)
    reviewer_id = serializers.PrimaryKeyRelatedField(queryset=Member.objects.all(), required=False, allow_null=True, write_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(queryset=Member.objects.all(), required=False, allow_null=True, write_only=True)
    due_date = serializers.DateField(format="%Y-%m-%d", required=False)

    def get_comments_count(self, obj):
        return obj.comments.count()

    class Meta:
        model = Task
        fields = ['id', 'board', 'title', 'description', 'status', 'priority', 'assignee', 'assignee_id', 'reviewer', 'reviewer_id', 'due_date', 'comments_count']


class TaskDetailSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField()

    def get_comments_count(self, obj):
        return obj.comments.count()

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'assignee', 'assignee_id', 'reviewer', 'reviewer_id', 'due_date', 'comments_count']

class BoardListSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        queryset=Member.objects.all(),
        many=True,
        required=True,
        write_only=True
    )
   
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    def create(self, validated_data):
        members = validated_data.pop('members', [])
        board = Board.objects.create(**validated_data)
        board.members.set(members)
        return board

    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status='to_do').count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority='high').count()

    class Meta:
        model = Board
        fields = ['id', 'title', 'members', 'member_count', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id']


class BoardDetailSerializer(serializers.ModelSerializer):
    members = MemberSerializer(many=True, read_only=True)
    tasks = TaskDetailSerializer(many=True, read_only=True)
    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']
