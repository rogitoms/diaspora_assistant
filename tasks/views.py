import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Task, Step, Message, StatusHistory
from .ai_engine import process_request
from .risk_score import calculate_risk, get_risk_label


# -------------------------------------------------------
# Serve the frontend
# -------------------------------------------------------
def index(request):
    return render(request, "index.html")


# -------------------------------------------------------
# POST /api/submit/
# Main endpoint — takes user request, runs AI, saves to DB
# -------------------------------------------------------
@csrf_exempt
@require_http_methods(["POST"])
def submit_request(request):
    try:
        # 1. Parse request body
        body = json.loads(request.body)
        user_input = body.get("request", "").strip()

        if not user_input:
            return JsonResponse({"error": "Request cannot be empty"}, status=400)

        if len(user_input) < 10:
            return JsonResponse({"error": "Please describe your request in more detail"}, status=400)

        # 2. Send to AI engine — get intent, entities, steps, messages
        ai_result = process_request(user_input)

        # 3. Calculate risk score using intent + entities
        risk_score, risk_breakdown = calculate_risk(
            ai_result["intent"],
            ai_result["entities"]
        )

        # 4. Create Task record in database
        task = Task.objects.create(
            original_request = user_input,
            intent           = ai_result["intent"],
            entities         = ai_result["entities"],
            risk_score       = risk_score,
            risk_breakdown   = risk_breakdown,
            employee_team    = ai_result["employee_team"],
        )

        # 5. Save Steps
        for step in ai_result["steps"]:
            Step.objects.create(
                task        = task,
                step_number = step["step_number"],
                description = step["description"],
            )

        # 6. Save all 3 messages, replace [TASK_CODE] placeholder with real code
        for channel, content in ai_result["messages"].items():
            Message.objects.create(
                task    = task,
                channel = channel,
                content = content.replace("[TASK_CODE]", task.task_code),
            )

        # 7. Return full task data to frontend
        return JsonResponse({
            "success": True,
            "task": serialize_task(task)
        })

    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=422)
    except Exception as e:
        return JsonResponse({"error": f"Something went wrong: {str(e)}"}, status=500)


# -------------------------------------------------------
# GET /api/tasks/
# Returns all tasks for the dashboard
# -------------------------------------------------------
@require_http_methods(["GET"])
def get_tasks(request):
    try:
        tasks = Task.objects.prefetch_related("steps", "messages").order_by("-created_at")
        return JsonResponse({
            "success": True,
            "tasks": [serialize_task(t) for t in tasks]
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# -------------------------------------------------------
# PATCH /api/tasks/<task_code>/status/
# Update task status and save history
# -------------------------------------------------------
@csrf_exempt
@require_http_methods(["PATCH"])
def update_status(request, task_code):
    try:
        body = json.loads(request.body)
        new_status = body.get("status", "").strip()

        valid_statuses = ["Pending", "In Progress", "Completed"]
        if new_status not in valid_statuses:
            return JsonResponse({"error": f"Status must be one of: {valid_statuses}"}, status=400)

        task = Task.objects.get(task_code=task_code)

        if task.status == new_status:
            return JsonResponse({"success": True, "status": task.status})

        # Save status change to history
        StatusHistory.objects.create(
            task       = task,
            old_status = task.status,
            new_status = new_status,
        )

        # Update task
        task.status = new_status
        task.save()

        return JsonResponse({
            "success": True,
            "task_code": task.task_code,
            "status": task.status,
        })

    except Task.DoesNotExist:
        return JsonResponse({"error": f"Task {task_code} not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# -------------------------------------------------------
# Helper — convert Task object to dict for JSON response
# -------------------------------------------------------
def serialize_task(task):
    messages = {m.channel: m.content for m in task.messages.all()}
    steps    = [{"number": s.step_number, "description": s.description, "completed": s.completed}
                for s in task.steps.all()]

    return {
        "task_code":        task.task_code,
        "intent":           task.intent,
        "original_request": task.original_request,
        "entities":         task.entities,
        "risk_score":       task.risk_score,
        "risk_label":       get_risk_label(task.risk_score),
        "risk_breakdown":   task.risk_breakdown,
        "status":           task.status,
        "employee_team":    task.employee_team,
        "created_at":       task.created_at.strftime("%d %b %Y, %I:%M %p"),
        "steps":            steps,
        "messages":         messages,
    }