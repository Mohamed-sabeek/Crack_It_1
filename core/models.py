
from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):
    pass


class AIChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conversation_id = models.CharField(max_length=36, blank=True, null=True, db_index=True)
    messages = models.JSONField(default=list)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        cid = self.conversation_id or "(unassigned)"
        return f"Conversation {cid} by {self.user.username} ({len(self.messages)} messages)"

    class Meta:
        ordering = ['-timestamp']


class Syllabus(models.Model):
    board = models.CharField(max_length=50)
    class_level = models.IntegerField()
    subject = models.CharField(max_length=50)
    content = models.TextField()
    pdf = models.FileField(upload_to="syllabus_pdfs/", null=True, blank=True)

    def __str__(self):
        return f"{self.board} Class {self.class_level} {self.subject}"


class MockTest(models.Model):
    CLASS_CHOICES = [
        (6, "Class 6"),
        (7, "Class 7"),
        (8, "Class 8"),
        (9, "Class 9"),
        (10, "Class 10"),
        (11, "Class 11"),
        (12, "Class 12"),
    ]
    subject = models.CharField(max_length=100, null=True, blank=True)
    class_level = models.PositiveSmallIntegerField(choices=CLASS_CHOICES, null=True, blank=True)
    description = models.TextField()
    date = models.DateField()

    def __str__(self):
        class_str = f"Class {self.class_level}" if self.class_level else "N/A"
        return f"{self.subject} - {class_str}"


class Question(models.Model):
    mock_test = models.ForeignKey(MockTest, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1)  # 'A', 'B', 'C', 'D'

    def __str__(self):
        return f"Question for {self.mock_test.subject} - {self.question_text[:50]}"


class TestAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="test_attempts")
    mock_test = models.ForeignKey(MockTest, on_delete=models.CASCADE, related_name="attempts")
    score = models.IntegerField()
    taken_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.mock_test.subject} - {self.score}%"


class UserAnswer(models.Model):
    attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1)  # 'A', 'B', 'C', or 'D'

    def __str__(self):
        return f"{self.attempt} | Q: {self.question.id} | Selected: {self.selected_option}"


class PreviousPaper(models.Model):
    EXAM_TYPE_CHOICES = [
        ("Prelims", "Prelims"),
        ("Main", "Main"),
    ]
    title = models.CharField(max_length=255)
    year = models.IntegerField()
    exam_type = models.CharField(max_length=10, choices=EXAM_TYPE_CHOICES, null=True, blank=True)
    file = models.FileField(upload_to="papers/")

    def __str__(self):
        etype = self.exam_type if self.exam_type else "No Type"
        return f"{self.title} ({self.year} - {etype})"


class Result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    test_name = models.CharField(max_length=100)
    taken_on = models.DateTimeField(auto_now_add=True)


class Keyword(models.Model):
    SUBJECT_CHOICES = [
        ("Biology(Botany)", "Biology(Botany)"),
        ("Biology(Zoology)", "Biology(Zoology)"),
        ("Chemistry", "Chemistry"),
        ("History", "History"),
        ("Geography", "Geography"),
        ("Economics", "Economics"),
        ("Science", "Science"),
        ("Tamil", "Tamil"),
        ("English", "English"),
        ("Maths", "Maths"),
        ("Political science", "Political science"),
        ("Physics", "Physics"),
    ]
    title = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="E.g., Early Civilizations, Freedom Struggle, etc."
    )
    subject = models.CharField(
        max_length=30,
        choices=SUBJECT_CHOICES,
        null=True,
        blank=True,
        help_text="Select the subject"
    )
    word = models.CharField(max_length=50, blank=True, null=True)
    meaning = models.TextField(help_text="Multi-line notes, mentions, emojis are allowed.")

    def __str__(self):
        return f"{self.subject or 'No Subject'} | {self.title or 'No Title'} | {self.word}"


class DailyQuiz(models.Model):
    question = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_option = models.CharField(
        max_length=1,
        choices=[('A', 'Option A'), ('B', 'Option B'), ('C', 'Option C'), ('D', 'Option D')],
        help_text="Select the correct option (A, B, C or D)."
    )
    quiz_date = models.DateField(
        help_text="The date this question is assigned to the daily quiz",
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Quiz {self.quiz_date}: {self.question[:50]}..."

    class Meta:
        verbose_name = "Daily Quiz Question"
        verbose_name_plural = "Daily Quiz Questions"
        ordering = ['quiz_date', 'id']


class InterviewQuestion(models.Model):
    DEPARTMENT_CHOICES = [
        ('civil_engineering', 'Civil Engineering'),
        ('mechanical_engineering', 'Mechanical Engineering'),
        ('eee', 'Electrical & Electronics Engineering (EEE)'),
        ('ece', 'Electronics & Communication (ECE)'),
        ('cse_it', 'Computer Science & IT'),
        ('chemical_engineering', 'Chemical Engineering'),
        ('aerospace_engineering', 'Aerospace Engineering'),
        ('biomedical_engineering', 'Biomedical Engineering'),
        ('industrial_engineering', 'Industrial Engineering'),
        ('physics', 'Physics'),
        ('chemistry', 'Chemistry'),
        ('mathematics_statistics', 'Mathematics / Statistics'),
        ('botany', 'Botany'),
        ('zoology', 'Zoology'),
        ('biotechnology_microbiology', 'Biotechnology / Microbiology'),
        ('environmental_science_ecology', 'Environmental Science / Ecology'),
        ('geology_geography', 'Geology / Geography'),
        ('mbbs', 'MBBS'),
        ('bds', 'BDS'),
        ('nursing', 'Nursing'),
        ('pharmacy', 'Pharmacy'),
        ('physiotherapy', 'Physiotherapy'),
        ('public_health', 'Public Health'),
        ('history', 'History'),
        ('political_science', 'Political Science'),
        ('sociology_social_work', 'Sociology / Social Work'),
        ('psychology', 'Psychology'),
        ('philosophy_ethics', 'Philosophy / Ethics'),
        ('languages', 'Languages'),
        ('fine_arts_performing_arts', 'Fine Arts / Performing Arts'),
        ('commerce_accounting', 'Commerce / Accounting'),
        ('business_admin_management', 'Business Admin / Management'),
        ('llb_llm', 'LLB / LLM'),
        ('education', 'Education'),
        ('library_information_science', 'Library & Information Science'),
        ('hotel_management', 'Hotel Management'),
        ('agriculture_horticulture_forestry', 'Agriculture / Horticulture / Forestry'),
        ('veterinary', 'Veterinary'),
        ('economy', 'Economy'),
    ]
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    question = models.TextField()
    answer = models.TextField()

    def __str__(self):
        return f"{self.get_department_display()} - {self.question[:50]}"


class Formula(models.Model):
    SUBJECT_CHOICES = [
        ("Biology", "Biology"),
        ("Chemistry", "Chemistry"),
        ('Biology(Botany)', 'Biology(Botany)'),
        ('Biology(Zoology)', 'Biology(Zoology)'),
        ("Physics", "Physics"),
        ("Maths", "Maths"),
        ("Economics", "Economics"),
        ("History", "History"),
        ("Geography", "Geography"),
        ("Political science", "Political science"),
        ("Science", "Science"),
        ("Tamil", "Tamil"),
        ("English", "English"),
    ]
    subject = models.CharField(max_length=30, choices=SUBJECT_CHOICES)
    heading = models.CharField(max_length=100)
    formula = models.TextField(help_text="Unicode or HTML allowed")

    def __str__(self):
        return f"{self.subject} - {self.heading}"


class DailyQuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="daily_quiz_attempts")
    quiz_date = models.DateField(db_index=True)
    score = models.IntegerField(default=0)
    percent = models.IntegerField(default=0)
    answers = models.JSONField(
        default=list,
        help_text="List of user's answers in order ['A', 'B', 'C', ...]"
    )
    attempted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz_date} - {self.score}/{self.get_total_questions()} ({self.percent}%)"

    def get_total_questions(self):
        """Get total questions for this quiz date"""
        return DailyQuiz.objects.filter(quiz_date=self.quiz_date).count()

    def save(self, *args, **kwargs):
        # Auto-calculate percentage if not set
        if self.score and not self.percent:
            total = self.get_total_questions()
            if total > 0:
                self.percent = int((self.score / total) * 100)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-quiz_date', '-attempted_at']
        unique_together = ('user', 'quiz_date')  # One attempt per user per day
        verbose_name = "Daily Quiz Attempt"
