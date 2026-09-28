import json
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .services import RouterEngine

def dashboard_view(request):
    """Renders the main Evaluator Dashboard interface."""
    return render(request, 'gateway/dashboard.html')

@csrf_exempt
def chat_gateway(request):
    """API endpoint receiving user prompts, executing routing logic, and returning telemetry."""
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

    start_time = time.time()

    try:
        data = json.loads(request.body)
        prompt = data.get("prompt", "")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    if not prompt.strip():
        return JsonResponse({"error": "Prompt cannot be empty"}, status=400)

    # Step 1: Run security and complexity evaluation
    analysis = RouterEngine.analyze(prompt)

    # Step 2: Handle blocked threats
    if analysis["action"] == "BLOCK":
        latency = round((time.time() - start_time) * 1000, 2)
        return JsonResponse({
            "status": "Blocked",
            "action": "BLOCK",
            "reason": analysis["reason"],
            "complexity_score": analysis["complexity_score"],
            "latency_ms": f"{latency} ms",
            "estimated_cost": "$0.0000",
            "response": "Request denied by Gateway Security Guardrail."
        }, status=400)

    # Step 3: Route based on analysis output
    if analysis["action"] == "LOCAL_MODEL":
        model_used = "Local Cluster (Phi-3 / Llama-3-8B)"
        cost_est = "$0.0000"
        ai_response = f"[LOCAL GPU RESPONSE]: Successfully processed simple task locally."
    else:
        model_used = "Cloud Endpoint (GPT-4o / Claude 3.5)"
        cost_est = "$0.0150"
        ai_response = f"[CLOUD API RESPONSE]: High-complexity task requiring external cloud reasoning."

    latency = round((time.time() - start_time) * 1000, 2)

    # Step 4: Return full telemetry payload
    return JsonResponse({
        "status": "Success",
        "action": analysis["action"],
        "routed_to": model_used,
        "complexity_score": analysis["complexity_score"],
        "reason": analysis["reason"],
        "latency_ms": f"{latency} ms",
        "estimated_cost": cost_est,
        "response": ai_response
    })