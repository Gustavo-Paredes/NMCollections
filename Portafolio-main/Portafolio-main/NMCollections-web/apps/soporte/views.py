from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods
from django.db import transaction
from django.utils import timezone

from .models import SupportThread, SupportMessage


def is_staff(user):
    return user.is_authenticated and user.is_staff


def _get_or_create_open_thread_for_user(user):
    thread = SupportThread.objects.filter(user=user, status='open').first()
    if thread:
        return thread
    with transaction.atomic():
        # Ensure no concurrent open thread creation
        thread = SupportThread.objects.select_for_update().filter(user=user, status='open').first()
        if thread:
            return thread
        return SupportThread.objects.create(user=user, status='open')


@login_required
@require_GET
def api_my_thread(request):
    thread = _get_or_create_open_thread_for_user(request.user)
    return JsonResponse({
        'id': thread.id,
        'status': thread.status,
        'assigned_admin': thread.assigned_admin_id,
    })


@login_required
@require_http_methods(["GET", "POST"])
def api_messages(request, thread_id: int):
    thread = get_object_or_404(SupportThread, id=thread_id)
    user = request.user
    # Permission: only the user owner or staff can access
    if (not user.is_staff) and (thread.user_id != user.id):
        return HttpResponseForbidden("No tienes permiso para este hilo")

    if request.method == 'GET':
        after = request.GET.get('after')
        qs = thread.messages.select_related('sender').all()
        if after:
            try:
                after_id = int(after)
                qs = qs.filter(id__gt=after_id)
            except ValueError:
                pass
        data = [
            {
                'id': m.id,
                'sender_id': m.sender_id,
                'sender_is_admin': m.sender.is_staff,
                'content': m.content,
                'created_at': m.created_at.isoformat(),
            }
            for m in qs
        ]
        return JsonResponse({'messages': data})

    # POST - create a message
    content = (request.POST.get('content') or '').strip()
    if not content:
        return JsonResponse({'error': 'Mensaje vacío'}, status=400)

    msg = SupportMessage.objects.create(
        thread=thread,
        sender=user,
        content=content,
        created_at=timezone.now(),
    )
    # If an admin sends the first message, assign them as the admin for this thread
    if user.is_staff and not thread.assigned_admin_id:
        thread.assigned_admin = user
        thread.updated_at = timezone.now()
        thread.save(update_fields=['assigned_admin', 'updated_at'])
    elif not user.is_staff:
        # Touch thread updated_at for ordering
        thread.updated_at = timezone.now()
        thread.save(update_fields=['updated_at'])

    return JsonResponse({
        'id': msg.id,
        'sender_id': msg.sender_id,
        'sender_is_admin': user.is_staff,
        'content': msg.content,
        'created_at': msg.created_at.isoformat(),
    }, status=201)


@login_required
def user_chat_view(request):
    if request.user.is_staff:
        return redirect('soporte:admin_threads')
    thread = _get_or_create_open_thread_for_user(request.user)
    return render(request, 'soporte/chat.html', {
        'thread': thread,
        'is_admin': False,
    })


@user_passes_test(is_staff)
def admin_threads_view(request):
    threads = SupportThread.objects.select_related('user', 'assigned_admin').order_by('-updated_at')
    return render(request, 'soporte/admin_threads.html', {
        'threads': threads,
    })


@user_passes_test(is_staff)
def admin_thread_chat_view(request, thread_id: int):
    thread = get_object_or_404(SupportThread.objects.select_related('user', 'assigned_admin'), id=thread_id)
    return render(request, 'soporte/chat.html', {
        'thread': thread,
        'is_admin': True,
    })
