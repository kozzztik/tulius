from django.utils.translation import ugettext_lazy as _
from django.views.generic.simple import direct_to_template, redirect_to
from django.shortcuts import get_object_or_404, get_list_or_404
from django.db.models import Q
from pm.models import PrivateMessage
from pm.forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

@login_required
def index(request, template_name='pm/index.haml'):
	return direct_to_template(request, template_name, locals())

@login_required
def inbox(request, template_name='pm/inbox.haml'):
	private_messages = PrivateMessage.objects.filter(receiver=request.user, removed_by_receiver=False)
	return direct_to_template(request, template_name, locals())

@login_required
def outbox(request, template_name='pm/outbox.haml'):
	private_messages = PrivateMessage.objects.filter(sender=request.user, removed_by_sender=False)
	return direct_to_template(request, template_name, locals())

@login_required
def message_details(request, message_id, template_name='pm/message_details.haml'):
	message = get_object_or_404(
		PrivateMessage,
		Q(sender=request.user) |
		Q(receiver=request.user),
		id = message_id,
	)

	if message.receiver == request.user:
		message.is_read = True
		message.save()
		form = PrivateMessageForm(data=request.POST or None, sender=request.user, receiver=message.sender)
		if form.is_valid():
			form.save()
			messages.success(request, _('answer sent'))
			return redirect_to(request, reverse('pm:outbox'))

	return direct_to_template(request, template_name, locals())

@login_required
def history(request, another_user_id, template_name='pm/message_history.haml'):
	another_user = get_object_or_404(
		User,
		id = another_user_id
	)

	form = PrivateMessageForm(data=request.POST or None, sender=request.user, receiver=another_user)
	if form.is_valid():
		form.save()
		messages.success(request, _('message sent'))
		return redirect_to(request, reverse('pm:history', args = [another_user_id]))

	private_messages = PrivateMessage.objects.filter(
		Q(sender=request.user, receiver__id=another_user_id) |
		Q(receiver__id=another_user_id, sender=request.user)
	).order_by('-created_at')

	return direct_to_template(request, template_name, locals())

@login_required
def message_create(request, another_user_id, template_name='pm/message_create.haml'):
	recipient = get_object_or_404(User, id = another_user_id)
	form = PrivateMessageForm(data=request.POST or None, sender=request.user, receiver=recipient)
	if form.is_valid():
		form.save()
		messages.success(request, _('message sent'))
		return redirect_to(request, reverse('pm:outbox'))
	return direct_to_template(request, template_name, locals())