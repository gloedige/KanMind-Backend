from rest_framework import serializers
from kanban_app.models import Board, Member, Task, Comment
from django.contrib.auth import get_user_model

User = get_user_model()

class MemberSerializer(serializers.ModelSerializer):
    """
    Serializer for the Member representation of the User model.
    """
    fullname = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'email', 'fullname')

    def get_fullname(self, obj):
        """
        Returns the full name of the user.
        """
        return obj.get_username()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class TaskListSerializer(serializers.ModelSerializer):
    """
    Serializer for the Task model used in list views.
    Provides a summary representation of the task, including counts of associated comments.
    """
    comments_count = serializers.SerializerMethodField(read_only=True)
    reviewer = MemberSerializer(many=False, read_only=True)
    assignee = MemberSerializer(many=False, read_only=True)
    reviewer_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    assignee_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    owner_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    due_date = serializers.DateField(format="%Y-%m-%d", required=False)

    def validate_assignee_id(self, value):
        """
        Validates that the assignee ID is a valid member of the board.
        Raises a ValidationError if the assignee is not a valid member.
        """
        board_id = self.context['request'].data.get('board', None)
        if value is not None and board_id is not None:
            board = Board.objects.get(pk=board_id)
            if not board.members.filter(id=value).exists():
                raise serializers.ValidationError("Assignee must be a valid member of the board.")
        return value

    def validate_reviewer_id(self, value):
        """
        Validates that the reviewer ID is a valid member of the board.
        Raises a ValidationError if the reviewer is not a valid member.
        """
        board_id = self.context['request'].data.get('board', None)
        if value is not None and board_id is not None:
            board = Board.objects.get(pk=board_id)
            if not board.members.filter(id=value).exists():
                raise serializers.ValidationError("Reviewer must be a valid member of the board.")
        return value

    def get_comments_count(self, obj):
        """
        Returns the number of comments associated with the task.
        """
        return obj.comments.count()

    class Meta:
        model = Task
        fields = ('id', 'board', 'title', 'description', 'status', 'priority', 'assignee', 'assignee_id', 'reviewer', 'reviewer_id', 'owner_id', 'due_date', 'comments_count')


class TaskDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for the Task model used in detail views.
    Provides detailed representation of the task, including assignee, reviewer, and owner information.
    """
    reviewer = MemberSerializer(many=False, read_only=True)
    assignee = MemberSerializer(many=False, read_only=True)
    reviewer_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    assignee_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    owner_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)

    def validate_assignee_id(self, value):
        """
        Validates that the assignee ID is a valid member of the board.
        Raises a ValidationError if the assignee is not a valid member.
        """
        if value is not None and not Task.objects.get(pk=self.instance.pk).board.members.filter(id=value).exists():
            raise serializers.ValidationError("Assignee must be a valid member of the board.")
        return value

    def validate_reviewer_id(self, value):
        """
        Validates that the reviewer ID is a valid member of the board.
        Raises a ValidationError if the reviewer is not a valid member.
        """
        if value is not None and not Task.objects.get(pk=self.instance.pk).board.members.filter(id=value).exists():
            raise serializers.ValidationError("Reviewer must be a valid member of the board.")
        return value

    def update(self, instance, validated_data):
        """
        Updates the task instance with the validated data, including handling changes to assignee and reviewer IDs.
        """
        new_assignee_id = validated_data.pop('assignee_id', None)
        new_reviewer_id = validated_data.pop('reviewer_id', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if new_assignee_id is not None:
            instance.assignee_id = new_assignee_id
        if new_reviewer_id is not None:
            instance.reviewer_id = new_reviewer_id
        instance.save()
        return instance

    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'status', 'priority', 'assignee', 'assignee_id', 'reviewer', 'reviewer_id', 'owner_id', 'due_date')

class BoardListSerializer(serializers.ModelSerializer):
    """
    Serializer for the Board model used in list views.
    Provides a summary of the board, including member count, ticket count, and task statistics.
    """
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=True,
        write_only=True,
        error_messages={
                    'does_not_exist': 'At least one of the specified members does not exist.',
                    'required': 'This field is required.',
                }
    )
   
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    def create(self, validated_data):
        """
        Creates a new board instance with the specified members.
        The creator of the board is set as the owner.
        """
        creator = self.context['request'].user
        members_data = validated_data.pop('members', [])
        board = Board.objects.create(owner_id=creator.id, **validated_data)

        if members_data:
            board_members = [
                Member(user=member_user, board=board)
                for member_user in members_data
            ]
            Member.objects.bulk_create(board_members)
        return board

    def validate_members(self, value):
        """
        Validates that at least one member is specified for the board.
        Raises a ValidationError if no members are provided.
        """
        if not value:
            raise serializers.ValidationError("At least one member must be specified.")
        return value

    def get_member_count(self, obj):
        """
        Returns the number of members in the board.
        """
        return obj.members.count()
    
    def get_ticket_count(self, obj):
        """
        Returns the number of tasks in the board.
        """
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        """
        Returns the number of tasks with status 'to_do' in the board.
        """
        return obj.tasks.filter(status='to_do').count()

    def get_tasks_high_prio_count(self, obj):
        """
        Returns the number of tasks with priority 'high' in the board.
        """
        return obj.tasks.filter(priority='high').count()

    class Meta:
        model = Board
        fields = ('id', 'title', 'members', 'member_count', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id')


class BoardDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for the Board model used in detail views.
    """
    members = MemberSerializer(many=True, read_only=True)
    tasks = TaskDetailSerializer(many=True, read_only=True)
    class Meta:
        model = Board
        fields = ('id', 'title', 'owner_id', 'members', 'tasks')

class BoardUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating the Board model.
    """
    owner_data = MemberSerializer(source='owner', read_only=True)
    members_data = MemberSerializer(source='members', many=True, read_only=True)

    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=True,
        write_only=True,
        error_messages={
            'does_not_exist': 'At least one of the specified members does not exist.',
            'required': 'This field is required.',
        }
    ) 

    def validate_members(self, value):
        """
        Validates that at least one member is specified for the board.
        Raises a ValidationError if no members are provided.
        """
        if not value:
            raise serializers.ValidationError("At least one member is required.")
        return value
    
    def update(self, instance, validated_data):
        """
        Updates the board instance with the provided validated data.
        Handles updating the title and members of the board.
        """
        members_data = validated_data.pop('members', None)
        instance.title = validated_data.get('title', instance.title)
        instance.save()
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
         
        self.update_members(instance, members_data)

        return instance

    def update_members(self, instance, members_data):
        """
        Updates the members associated with the board instance.
        Adds new members and removes members that are no longer part of the board.
        """
        if members_data is not None:
            new_user = set(members_data)
            existing_memberships = Member.objects.filter(board=instance)
            existing_users = {m.user for m in existing_memberships}

            users_to_remove = existing_users - new_user
            Member.objects.filter(board=instance, user__in=users_to_remove).delete()
            
            users_to_add = new_user - existing_users
            new_memberships = [
                Member(board=instance, user_id=user.id) 
                for user in users_to_add
                ]
            Member.objects.bulk_create(new_memberships)
                   

    class Meta:
        model = Board
        fields = ('id','title', 'owner_data', 'members_data', 'members')


class CommentListSerializer(serializers.ModelSerializer):
    """
    Serializer for the Comment model used in comment list views.
    """
    author = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)

    class Meta:
        model = Comment
        fields = ('id', 'created_at', 'author', 'content')

    