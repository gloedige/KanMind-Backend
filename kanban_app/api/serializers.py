from rest_framework import serializers
from kanban_app.models import Board, Member, Task, Comment
from rest_framework import serializers, viewsets

class MemberSerializer(serializers.ModelSerializer):
    """
    Serializer for the Member model.
    Fields
    ------
    id : int
        The unique identifier of the member.
    email : str
        The email address of the member.
    fullname : str
        The full name of the member.
    """
    class Meta:
        model = Member
        fields = ['id', 'email', 'fullname']


class TaskListSerializer(serializers.ModelSerializer):
    """
    Serializer for the Task model used in list views.
    Fields
    ------
    id : int
        The unique identifier of the task.
    board : int
        The ID of the board the task belongs to.
    title : str
        The title of the task.
    description : str
        The description of the task.
    status : str
        The status of the task.
    priority : str
        The priority of the task.
    assignee : MemberSerializer
        The member assigned to the task.
    assignee_id : int
        The ID of the member assigned to the task.
    reviewer : MemberSerializer
        The member reviewing the task.
    reviewer_id : int
        The ID of the member reviewing the task.
    due_date : str
        The due date of the task in YYYY-MM-DD format.
    comments_count : int
        The number of comments on the task.
    Methods
    -------
    get_comments_count(self, obj)
        Returns the number of comments on the task.
    """
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
    """
    Serializer for the Task model used in detail views.
    Fields
    ------
    id : int
        The unique identifier of the task.
    title : str
        The title of the task.
    description : str
        The description of the task.
    status : str
        The status of the task.
    priority : str
        The priority of the task.
    assignee : MemberSerializer
        The member assigned to the task.
    assignee_id : int
        The ID of the member assigned to the task.
    reviewer : MemberSerializer
        The member reviewing the task.
    reviewer_id : int
        The ID of the member reviewing the task.
    due_date : str
        The due date of the task in YYYY-MM-DD format.
    comments_count : int
        The number of comments on the task.
    Methods
    -------
    get_comments_count(self, obj)
        Returns the number of comments on the task.
    """
    comments_count = serializers.SerializerMethodField()

    def get_comments_count(self, obj):
        return obj.comments.count()

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'assignee', 'assignee_id', 'reviewer', 'reviewer_id', 'due_date', 'comments_count']

class BoardListSerializer(serializers.ModelSerializer):
    """
    Serializer for the Board model used in list views.
    Fields
    ------
    id : int
        The unique identifier of the board.
    title : str
        The title of the board.
    members : list of int
        The list of member IDs associated with the board.
    member_count : int
        The number of members in the board.
    ticket_count : int
        The number of tasks in the board.
    tasks_to_do_count : int
        The number of tasks with status 'to_do' in the board.
    tasks_high_prio_count : int
        The number of tasks with priority 'high' in the board.
    owner_id : int
        The ID of the owner of the board.
    Methods
    -------
    get_member_count(self, obj)
        Returns the number of members in the board.
    get_ticket_count(self, obj)
        Returns the number of tasks in the board.
    get_tasks_to_do_count(self, obj)
        Returns the number of tasks with status 'to_do' in the board.
    get_tasks_high_prio_count(self, obj)
        Returns the number of tasks with priority 'high' in the board.
    """
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
    """
    Serializer for the Board model used in detail views.
    Fields
    ------
    id : int
        The unique identifier of the board.
    title : str
        The title of the board.
    owner_id : int
        The ID of the owner of the board.
    members : list of MemberSerializer
        The list of members associated with the board.
    tasks : list of TaskDetailSerializer
        The list of tasks associated with the board.
    """
    members = MemberSerializer(many=True, read_only=True)
    tasks = TaskDetailSerializer(many=True, read_only=True)
    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']
