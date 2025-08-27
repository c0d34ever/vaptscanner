import json
from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from .models import Scan
from .tasks import run_vapt_scan


def dashboard(request):
    scans = Scan.objects.all().order_by('-start_time')
    return render(request, 'scans/dashboard.html', {'scans': scans})


def new_scan(request):
    if request.method == 'POST':
        target_url = request.POST.get('target_url')
        if target_url:
            scan = Scan.objects.create(target_url=target_url)
            run_vapt_scan.delay(scan.id)
            return redirect('scan_report', scan_id=scan.id)
    return render(request, 'scans/new_scan.html')


def scan_report(request, scan_id: int):
    scan = get_object_or_404(Scan, id=scan_id)
    findings = scan.findings.all()
    return render(request, 'scans/report.html', {'scan': scan, 'findings': findings})


def _check_api_key(request):
    api_key = request.headers.get('X-API-Key') or request.GET.get('api_key')
    expected = getattr(settings, 'API_KEY', None)
    return api_key and expected and api_key == expected


def api_create_scan(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    if not _check_api_key(request):
        return HttpResponseForbidden('Invalid API key')
    data = json.loads(request.body or '{}')
    target_url = data.get('target_url')
    engine = data.get('engine', 'zap')
    options = data.get('options')
    if not target_url:
        return JsonResponse({'error': 'target_url is required'}, status=400)
    scan = Scan.objects.create(target_url=target_url, engine=engine, options=options)
    run_vapt_scan.delay(scan.id)
    return JsonResponse({'id': scan.id, 'status': scan.status})


def api_get_scan(request, scan_id: int):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    if not _check_api_key(request):
        return HttpResponseForbidden('Invalid API key')
    scan = get_object_or_404(Scan, id=scan_id)
    return JsonResponse({
        'id': scan.id,
        'target_url': scan.target_url,
        'engine': scan.engine,
        'status': scan.status,
        'start_time': scan.start_time,
        'end_time': scan.end_time,
        'report_json': scan.report_json,
        'error_message': scan.error_message,
    }, safe=False)


def api_list_scans(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    if not _check_api_key(request):
        return HttpResponseForbidden('Invalid API key')
    scans = Scan.objects.all().order_by('-start_time')[:100]
    data = [
        {
            'id': s.id,
            'target_url': s.target_url,
            'engine': s.engine,
            'status': s.status,
            'start_time': s.start_time,
            'end_time': s.end_time,
        }
        for s in scans
    ]
    return JsonResponse(data, safe=False)


