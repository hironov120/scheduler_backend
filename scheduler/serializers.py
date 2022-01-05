from rest_framework import serializers

from .models import User, Task, TaskProcessed, Note, NoteProcessed

### SerializerはModelとＤＢの情報交換のみを行う

### 基本シリアライザ定義 ###

class UserSerializer(serializers.ModelSerializer):
    """this provides methods for specific model

    """

    class Meta:
        model = User
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    """this provides methods for specific model

    """

    id = serializers.IntegerField(read_only=True) # idだけここでもread_only指定（しないとcreateの時に求められる） 

    class Meta:
        model = Task
        fields = '__all__'

        # DRFを使う場合、Serializerには書き換え防止のために以下の項目を設定する
        read_only_fields = ('id', 'createdDateTime', 'updateDateTime')


class TaskProcessedSerializer(serializers.ModelSerializer):
    """this provides methods for specific model

    """

    id = serializers.IntegerField(read_only=True) # TaskProcessed全体で振られるシーケンス。使わない

    class Meta:
        model = TaskProcessed
        fields = '__all__'


class NoteSerializer(serializers.ModelSerializer):
    """this provides methods for specific model

    """

    id = serializers.IntegerField(read_only=True) # idだけここでもread_only指定（しないとcreateの時に求められる） 

    class Meta:
        model = Note
        fields = '__all__'

        # DRFを使う場合、Serializerには書き換え防止のために以下の項目を設定する
        read_only_fields = ('id', 'createdDateTime', 'updateDateTime')


class NoteProcessedSerializer(serializers.ModelSerializer):
    """this provides methods for specific model

    """

    id = serializers.IntegerField(read_only=True) # NaskProcessed全体で振られるシーケンス。使わない

    class Meta:
        model = NoteProcessed
        fields = '__all__'

