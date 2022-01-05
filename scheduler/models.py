from django.db import models


class User(models.Model):
    userId = models.CharField("ユーザーＩＤ", max_length=15, primary_key=True)

    userName = models.CharField("ユーザー名", max_length=48)
    password = models.CharField("パスワード", max_length=25)

# 進行中のタスク
class Task(models.Model):
    
    tasktitle = models.CharField("タスクタイトル", max_length=100)
    detail = models.CharField("タスク詳細", max_length=1000, null=True, blank=True)
    PRIORITY_FIELD  = (
        (1, '重要緊急'),
        (2, '待ち作業'),
        (3, '不要不急'),
    )
    priority = models.IntegerField(
        choices=PRIORITY_FIELD,
        default=1,
    )
    deadline = models.DateField(null=True)

    createDateTime = models.DateTimeField(auto_now_add=True) # Modelのcreate時のみ自動で日付を入れる
    updateDateTime = models.DateTimeField(auto_now=True) #更新時に自動で日付を入れる

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)

# 完了後、もしくは削除後のタスク
class TaskProcessed(models.Model):

    # PK部分（Modelの定義上は違うが）
    taskProcessedId = models.IntegerField()
    historySeq = models.IntegerField()

    tasktitle = models.CharField("タスクタイトル", max_length=100)
    detail = models.CharField("タスク詳細", max_length=1000, null=True, blank=True)
    PRIORITY_FIELD  = (
        (1, '重要緊急'),
        (2, '待ち作業'),
        (3, '不要不急'),
    )
    priority = models.IntegerField(
        choices=PRIORITY_FIELD,
        default=1,
    )
    deadline = models.DateField(null=True)

    # 作成日時、更新日時は元のタスクのものをそのまま使う
    createDateTime = models.DateTimeField()
    updateDateTime = models.DateTimeField(null=True)

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)

    class Meta:
        """複合ＰＫ（のようなもの）を作成（djangoは複合ＰＫをサポートしていない）
        """
        unique_together = (("taskProcessedId","historySeq"),)   

# 表示中のノート
class Note(models.Model):
    
    notebody = models.CharField("ノート", max_length=1000, null=True, blank=True)

    createDateTime = models.DateTimeField(auto_now_add=True) # Modelのcreate時のみ自動で日付を入れる
    updateDateTime = models.DateTimeField(auto_now=True) #更新時に自動で日付を入れる

    PROCESSED_FLAG_FIELD = (
        (1, '更新'),
        (2, '完了'),
        (3, '削除'),
    )
    processedFlag = models.IntegerField(
        choices=PROCESSED_FLAG_FIELD,
        default=1
    )

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)

# ノートの更新履歴（削除後のものも含む
class NoteProcessed(models.Model):

    # PK部分（Modelの定義上は違うが）
    noteProcessedId = models.IntegerField()
    historySeq = models.IntegerField()

    notebody = models.CharField("ノート", max_length=1000, null=True, blank=True)

    # 作成日時、更新日時は元のノートのものをそのまま使う
    createDateTime = models.DateTimeField()
    updateDateTime = models.DateTimeField(null=True)

    PROCESSED_FLAG_FIELD = (
        (1, '更新'),
        (2, '完了'),
        (3, '削除'),
    )
    processedFlag = models.IntegerField(
        choices=PROCESSED_FLAG_FIELD,
        default=1
    )

    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)

    class Meta:
        """複合ＰＫ（のようなもの）を作成（djangoは複合ＰＫをサポートしていない）
        """
        unique_together = (("noteProcessedId","historySeq"),)   

