from django.db import models
import uuid


def generate_task_code():
    return "DSP-" + str(uuid.uuid4())[:8].upper()


class Task(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Completed", "Completed"),
    ]
    INTENT_CHOICES = [
        ("send_money", "Send Money"),
        ("hire_service", "Hire Service"),
        ("verify_document", "Verify Document"),
        ("airport_transfer", "Airport Transfer"),
        ("check_status", "Check Status"),
    ]
    EMPLOYEE_CHOICES = [
        ("Finance", "Finance"),
        ("Operations", "Operations"),
        ("Legal", "Legal"),
        ("Logistics", "Logistics"),
    ]

    task_code        = models.CharField(max_length=20, unique=True, default=generate_task_code)
    original_request = models.TextField()
    intent           = models.CharField(max_length=50, choices=INTENT_CHOICES)
    entities         = models.JSONField()
    risk_score       = models.IntegerField(default=0)
    risk_breakdown   = models.JSONField(default=dict)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    employee_team    = models.CharField(max_length=50, choices=EMPLOYEE_CHOICES)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.task_code} | {self.intent} | {self.status}"


class Step(models.Model):
    task        = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="steps")
    step_number = models.IntegerField()
    description = models.TextField()
    completed   = models.BooleanField(default=False)

    class Meta:
        ordering = ["step_number"]

    def __str__(self):
        return f"{self.task.task_code} — Step {self.step_number}"


class Message(models.Model):
    CHANNEL_CHOICES = [
        ("whatsapp", "WhatsApp"),
        ("email", "Email"),
        ("sms", "SMS"),
    ]
    task    = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="messages")
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    content = models.TextField()

    class Meta:
        unique_together = ("task", "channel")

    def __str__(self):
        return f"{self.task.task_code} — {self.channel}"


class StatusHistory(models.Model):
    task       = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="history")
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task.task_code}: {self.old_status} → {self.new_status}"