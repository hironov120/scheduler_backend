from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
import datetime

from .models import User, Task, TaskProcessed, Note, NoteProcessed
from .serializers import UserSerializer, TaskSerializer, TaskProcessedSerializer, NoteSerializer, NoteProcessedSerializer

class UserViewSet(viewsets.ModelViewSet):
    """User情報を返却する。

    """
    serializer_class = UserSerializer # おまじない
    #permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """userIdを指定した場合のみUser情報を返却する。

        Returns:
            ・User１レコード（/users/?user_pk=***)
            これ以外の指定方法は受け付けない。
        """

        return User.objects.all()


class TaskViewSet(viewsets.ModelViewSet):
    """
    　URL:/tasks/[id]
    　Userについて進行中のタスク情報を表示、更新、追加、削除するViewSet。

    """
    serializer_class = TaskSerializer # シリアライザはTaskとして定義する（おまじない）
    
    def _add_task_history(self, pk=None, taskInstance=None, processedFlag=None):
        """Taskのidを指定し、昔のTask情報を履歴番号付きでTaskProcessedに保存する。

        Args:
            request ([type]): [description]
            taskInstance: 更新前のTask
            processedFlag: 1 更新 2 完了 3 削除
        """

        # 履歴として保存するフィールド情報を設定
        taskProcessed_data = {
                'taskProcessedId' : pk,
                'tasktitle' : taskInstance.tasktitle,
                'detail' : taskInstance.detail,
                'priority' : taskInstance.priority,
                'deadline' : taskInstance.deadline,
                'createDateTime' : taskInstance.createDateTime, # 元のTaskのcreateDateTimeが入る
                'updateDateTime' : taskInstance.updateDateTime, # 元のTaskのupdateDateTimeが入る
                'processedFlag' : processedFlag,
                'user' : taskInstance.user.userId, 
            }

        # 過去のTaskProcessedに同じPKのデータが既に保存されているかを見に行く
        taskProcessed_last = TaskProcessed.objects.filter(taskProcessedId=pk).order_by('-historySeq').first()
        if taskProcessed_last is None: # 初保存（＝初更新）の場合
            taskProcessed_data['historySeq'] = 1
            
        else : # 二回目以降の更新の場合
            taskProcessed_data['historySeq'] = taskProcessed_last.historySeq + 1
        
        # 履歴の保存
        taskProcessed_serializer = TaskProcessedSerializer(instance = None, data=taskProcessed_data)
        if taskProcessed_serializer.is_valid(raise_exception=True):
            taskProcessed_serializer.save() # Tips serializer.dataを呼んだあとにsave()は呼べない（is_validしたらすぐsaveする）
        

    def get_queryset(self):
            """Taskのidを指定し、Taskを更新する。

            Returns:
                ・Taskの全レコード、またはidで指定された1レコード
            """

            return Task.objects.all()

    def create(self, request):
        """Taskを新規作成する。

        Args:
            request ([type]): [description]
        """

        task_serializer = self.get_serializer(data=request.data)
        
        if task_serializer.is_valid():
            
            self.perform_create(task_serializer)

            return Response(task_serializer.data, status=status.HTTP_201_CREATED)

        else:
            
            print(task_serializer.errors)

            return Response(task_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def update(self, request, pk=None): # updateはmixinモジュールのメソッドをオーバーライドしてる argsとkwargsは可変長変数なので実質任意
        """Taskのidを指定し、Taskを更新する。

        １．指定されたTaskについて、昔の情報を履歴番号付きでTaskProcessedに保存する。
        ２．指定されたTask情報自体を更新する。

        Args:
            request : ＰＯＳＴで受け取ったデータを含む、rest_framework.request.Request

        """

        # ＤＢにある更新前のTask情報を取得（なぜこれで取得できるのかは不明）
        instance = self.get_object() 

        # シリアライズ
        task_serializer = self.get_serializer(instance=instance, data=request.data) # get_serializerは上で定義したserializer_classを呼んでるだけ

        if task_serializer.is_valid(): # Tips is_validだった場合のみその下でserializer.validated_dataが使えるようになる

            # 更新前のTask情報をTaskProcessedに保存する
            self._add_task_history(pk=pk, taskInstance=instance, processedFlag=1)

            # Task自体を更新
            self.perform_update(task_serializer) # update実行(内部ではserializer.save()が実行される)

            response_data = task_serializer.data

        else:

            print(task_serializer.errors)
            
            response_data = task_serializer.errors

        return Response(response_data)


    def destroy(self, request, pk=None):
        """Taskのidを指定し、Taskを完了、または削除する。

        １．指定されたTaskについて、昔の情報を履歴番号付きでTaskProcessedに保存する。
        ２．指定されたTask情報自体を完了、または削除する。

        """

        # ＤＢにある更新前のTask情報を取得
        instance = self.get_object()

        # 更新前のTask情報をTaskProcessedに保存する
        self._add_task_history(pk=pk, taskInstance=instance, processedFlag=2) # TODO ここの実装

        # Task自体は削除
        self.perform_destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT) 


    @action(detail=False, methods=['get']) # detailをどっちにするかはSimpleRouterのコード読むとわかるよ
    def get_tasks_for_user(self, request):
        """（自作URL）getをルーティングして、userIdに紐づく進行中タスク全量を返却する

        """
        
        if ('id' in request.GET) & ('sort_state' in request.GET) & ('display_state' in request.GET):
            task_data = Task.objects.filter(user=request.GET['id'])

            if request.GET['display_state']=='1':
                task_data = task_data.exclude(
                    Q(priority=3) & Q(deadline='2099-12-31')
                )

            if request.GET['sort_state']=='0':
                task_data = task_data.order_by('priority', 'deadline', 'id')
            
            else:
                task_data = task_data.order_by('deadline', 'priority', 'id')
            
            dt_now = datetime.datetime.now()
            
            due_today_count = task_data.filter(
                Q(deadline__lte=dt_now.strftime(r'%Y-%m-%d')) & Q(priority=1) # 期限が今日より前かつ、優先度が1以上の数をカウント
            ).count()

            task_serializer = self.get_serializer(
                    instance=None, 
                    data=task_data,
                    many=True,
                    )

            task_serializer.is_valid()

            response_data = {
                'tasks': task_serializer.data,
                'due_today_count': due_today_count,
            }

            return Response(response_data) # パラメータ名は「user」になる。

        else: # TODO できればエラーを出したい（raise Http...？)
            
            return Response(status=status.HTTP_204_NO_CONTENT) 
    
    
    @action(detail=False, methods=['get']) 
    def get_tasks_count_for_user(self, request):
        task_data = Task.objects.filter(user=request.GET['id'])
        dt_query = datetime.datetime.now()
        
        count_list = [[0,0,0,0,0,0,0] for i in range(3)]
        
        for i in range(0,7):
            task_data_q = task_data.filter(deadline=dt_query.strftime(r'%Y-%m-%d'))
            count_list[0][i] = task_data_q.filter(priority=1).count()
            count_list[1][i] = task_data_q.filter(priority=2).count()
            count_list[2][i] = task_data_q.filter(priority=3).count()
            
            dt_query = dt_query + datetime.timedelta(days=1)
        
        response_data = {
                'priority_1_count' : count_list[0],
                'priority_2_count' : count_list[1],
                'priority_3_count' : count_list[2],
            } 
        
        return Response(response_data) 


class NoteViewSet(viewsets.ModelViewSet):
    """
    　URL:/notes/[id]
    　Userについて進行中のタスク情報を表示、更新、追加、削除するViewSet。

    """
    serializer_class = NoteSerializer # シリアライザはTaskとして定義する（おまじない）
    
    def _add_note_history(self, pk=None, noteInstance=None, processedFlag=None):
        """Noteのidを指定し、昔のNote情報を履歴番号付きでNoteProcessedに保存する。

        Args:
            request ([type]): [description]
            taskInstance: 更新前のTask
            processedFlag: 1 更新 2 完了 3 削除
        """

        # 履歴として保存するフィールド情報を設定
        noteProcessed_data = {
                'noteProcessedId' : pk,
                'notebody' : noteInstance.notebody,
                'createDateTime' : noteInstance.createDateTime, # 元のNoteのcreateDateTimeが入る
                'updateDateTime' : noteInstance.updateDateTime, # 元のNoteのupdateDateTimeが入る
                'processedFlag' : processedFlag,
                'user' : noteInstance.user.userId, 
            }

        # 過去のNoteProcessedに同じPKのデータが既に保存されているかを見に行く
        noteProcessed_last = NoteProcessed.objects.filter(noteProcessedId=pk).order_by('-historySeq').first()
        if noteProcessed_last is None: # 初保存（＝初更新）の場合
            noteProcessed_data['historySeq'] = 1
            
        else : # 二回目以降の更新の場合
            noteProcessed_data['historySeq'] = noteProcessed_last.historySeq + 1
        
        # 履歴の保存
        noteProcessed_serializer = NoteProcessedSerializer(instance = None, data=noteProcessed_data)
        
        if noteProcessed_serializer.is_valid(raise_exception=True):
            noteProcessed_serializer.save() # Tips serializer.dataを呼んだあとにsave()は呼べない（is_validしたらすぐsaveする）
        

    def get_queryset(self):
            """Noteのidを指定し、Taskを更新する。

            Returns:
                ・Noteの全レコード、またはidで指定された1レコード
            """

            return Note.objects.all()

    def create(self, request):
        """Noteを新規作成する。

        Args:
            request ([type]): [description]
        """

        note_serializer = self.get_serializer(data=request.data)
        
        if note_serializer.is_valid():
            
            self.perform_create(note_serializer)

            return Response(note_serializer.data, status=status.HTTP_201_CREATED)

        else:
            
            print(note_serializer.errors)

            return Response(note_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def update(self, request, pk=None): # updateはmixinモジュールのメソッドをオーバーライドしてる argsとkwargsは可変長変数なので実質任意
        """Noteのidを指定し、Noteを更新する。

        １．指定されたNoteについて、昔の情報を履歴番号付きでNoteProcessedに保存する。
        ２．指定されたNote情報自体を更新する。

        Args:
            request : ＰＯＳＴで受け取ったデータを含む、rest_framework.request.Request

        """

        # ＤＢにある更新前のTask情報を取得（なぜこれで取得できるのかは不明）
        instance = self.get_object() 

        # シリアライズ
        note_serializer = self.get_serializer(instance=instance, data=request.data) # get_serializerは上で定義したserializer_classを呼んでるだけ

        if note_serializer.is_valid(): # Tips is_validだった場合のみその下でserializer.validated_dataが使えるようになる
            
            # 更新前のTask情報をTaskProcessedに保存する
            self._add_note_history(pk=pk, noteInstance=instance, processedFlag=1)
            
            # Task自体を更新
            self.perform_update(note_serializer) # update実行(内部ではserializer.save()が実行される)
            
            response_data = note_serializer.data

        else:

            print(note_serializer.errors)
            
            response_data = note_serializer.errors

        return Response(response_data)


    def destroy(self, request, pk=None):
        """Noteのidを指定し、Noteを完了、または削除する。

        １．指定されたNoteについて、昔の情報を履歴番号付きでNoteProcessedに保存する。
        ２．指定されたNote情報自体を完了、または削除する。

        """

        # ＤＢにある更新前のTask情報を取得
        instance = self.get_object()

        # 更新前のTask情報をTaskProcessedに保存する
        self._add_note_history(pk=pk, noteInstance=instance, processedFlag=2) # TODO ここの実装

        # Task自体は削除
        self.perform_destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT) 


    @action(detail=False, methods=['get']) # detailをどっちにするかはSimpleRouterのコード読むとわかるよ
    def get_notes_for_user(self, request):
        """（自作URL）getをルーティングして、userIdに紐づく進行中タスク全量を返却する

        """
        
        if 'id' in request.GET:

            note_serializer = self.get_serializer(
                instance=None, 
                data=Note.objects.filter(user=request.GET['id']).order_by('id') , 
                many=True
                )

            note_serializer.is_valid()

            return Response(note_serializer.data) # パラメータ名は「user」になる。

        else: # TODO できればエラーを出したい（raise Http...？)
            
            return Response(status=status.HTTP_204_NO_CONTENT) 
