from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from ...models import *

@receiver(post_save, sender=VideoPost)
def notify_followers_to_new_post(sender, instance, created, **kwargs):
     # Notify on creation if both fields are True
    if created and instance.status and instance.confirm_to_post:
        channel = instance.channel
        followers = Subscription.objects.filter(channel=channel)
        for follow in followers:
            Notification.objects.create(
            user=follow.user,
            message=f"New video posted on {channel.name}: {instance.title}"
        )
    # Notify on update if both fields change to True
    elif not created:
        if instance.confirm_to_post and instance.status:
            channel = instance.channel
            followers = Subscription.objects.filter(channel=channel)
            for follow in followers:
                Notification.objects.create(
                user=follow.user,
                message=f"Video update on {channel.name}: {instance.title}"
            )

@receiver(post_save, sender=Comment)
def notify_user_on_reply(sender, instance, created, **kwargs):
    if instance.uper_comment and instance.confirm_to_comment:
        # This comment is a reply to another comment
        original_comment = instance.uper_comment
        original_user = original_comment.user
        
        # Create a notification for the original comment's user
        Notification.objects.create(
            user=original_user,
            message=f"{instance.user.user.username} replied to your {instance.uper_comment} comment: {instance.comment}",
        )

@receiver(post_save, sender=Subscription)
def notify_on_subscribe(sender, instance, created, **kwargs):
    if created:
        channel = instance.channel
        channel_owner = channel.owner
        channel_admins = AdminsOfChannel.objects.filter(channel=channel)

        # Notify the channel owner
        Notification.objects.create(
            user=channel_owner,
            message=f"{instance.user.user.username} started following the channel {channel.name}."
        )
        
        # Notify the channel admins
        for admin in channel_admins:
            Notification.objects.create(
                user=admin.admin,
                message=f"{instance.user.user.username} started following the channel {channel.name}."
            )

@receiver(post_delete, sender=Subscription)
def notify_on_unsubscribe(sender, instance, **kwargs):
    channel = instance.channel
    channel_owner = channel.owner
    channel_admins = AdminsOfChannel.objects.filter(channel=channel)
        
    # Notify the channel owner
    Notification.objects.create(
        user=channel_owner,
        message=f"{instance.user.user.username} stopped following the channel {channel.name}."
    )
    
    # Notify the channel admins
    for admin in channel_admins:
        Notification.objects.create(
            user=admin.admin,
            message=f"{instance.user.user.username} stopped following the channel {channel.name}."
        )

@receiver(post_save, sender=Like)
def notify_on_like(sender, instance, created, **kwargs):
    if created:
        video_post = instance.video_post
        channel = video_post.channel  # Assuming VideoPost has a ForeignKey to Channel
        channel_owner = channel.owner
        video_post_publisher = video_post.publisher
        
        # Notify the channel owner
        Notification.objects.create(
            user=channel_owner,
            message=f"{instance.user.user.username}  liked the video {video_post.title} in channel {channel.name}."
        )
        
        # Notify the video_post publisher
        Notification.objects.create(
            user=video_post_publisher,
            message=f"{instance.user.user.username}  liked the video {video_post.title} in channel {channel.name}."
        )

@receiver(post_save, sender=Dislike)
def notify_on_dislike(sender, instance, created, **kwargs):
    if created:
        video_post = instance.video_post
        channel = video_post.channel  # Assuming VideoPost has a ForeignKey to Channel
        channel_owner = channel.owner
        video_post_publisher = video_post.publisher
        
        # Notify the channel owner
        Notification.objects.create(
            user=channel_owner,
            message=f"{instance.user.user.username} disliked  the video {video_post.title} in channel {channel.name}."
        )
        
        # Notify the video_post publisher
        Notification.objects.create(
            user=video_post_publisher,
            message=f"{instance.user.user.username} disliked  the video {video_post.title} in channel {channel.name}."
        )


@receiver(post_save, sender=Comment)
def notify_on_comment(sender, instance, created, **kwargs):
    if created:
        video_post = instance.video_post
        channel = video_post.channel
        publisher = video_post.publisher
        channel_owner = channel.owner
        
        # Notify the publisher
        Notification.objects.create(
            user=publisher,
            message=f"{instance.user.user.username} commented on your {channel} channel {video_post} video: {instance.comment}"
        )
        
        # Notify the channel owner
        Notification.objects.create(
            user=channel_owner,
            message=f"{instance.user.user.username} commented on {video_post} video in your {channel} channel: {instance.comment}"
        )

@receiver(post_save, sender=Subscription)
def increment_subscribe_count(sender, instance, created, **kwargs):
    if created:
        channel = instance.channel
        channel.subscribe_count += 1
        channel.save()

@receiver(post_delete, sender=Subscription)
def decrement_subscribe_count(sender, instance, **kwargs):
    channel = instance.channel
    channel.subscribe_count -= 1
    channel.save()

@receiver(post_save, sender=Like)
def increment_counted_like(sender, instance, created, **kwargs):
    if created:
        video_post = instance.video_post
        video_post.counted_like += 1
        
        if Dislike.objects.filter(user=instance.user, video_post=video_post):
            Dislike.objects.filter(user=instance.user, video_post=video_post).delete()
            video_post.counted_dislike -= 1
        video_post.save()

@receiver(post_delete, sender=Like)
def decrement_counted_like(sender, instance, **kwargs):
    video_post = instance.video_post
    video_post.counted_like -= 1
    video_post.save()

@receiver(post_save, sender=Dislike)
def increment_counted_dislike(sender, instance, created, **kwargs):
    if created:
        video_post = instance.video_post
        video_post.counted_dislike += 1
        
        if Like.objects.filter(user=instance.user, video_post=video_post):
            Like.objects.filter(user=instance.user, video_post=video_post).delete()
            video_post.counted_like -= 1
        video_post.save()

@receiver(post_delete, sender=Dislike)
def decrement_counted_dislike(sender, instance, **kwargs):
    video_post = instance.video_post
    video_post.counted_dislike -= 1
    video_post.save()

@receiver(post_save, sender=Save)
def increment_counted_save(sender, instance, created, **kwargs):
    if created:
        video_post = instance.video_post
        video_post.counted_save += 1
        video_post.save()

@receiver(post_delete, sender=Save)
def decrement_counted_save(sender, instance, **kwargs):
    video_post = instance.video_post
    video_post.counted_save -= 1
    video_post.save()