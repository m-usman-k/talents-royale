from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.utils import timezone
import json
import smtplib
import logging
import stripe

from .forms import SignupForm, LoginForm, UserSettingsForm, PasswordChangeForm, DeleteAccountForm, ContestantSubmissionForm, ForgotPasswordForm, ResetPasswordForm, EmailChangeForm
from .models import CustomUser, Arena, Contestant, Vote, TokenTransaction, EmailConfirmationToken, Payment
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

# Initialize Stripe
if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY


def get_email_error_message(error):
    """Parse email sending errors and return user-friendly messages"""
    error_str = str(error)
    
    # Gmail authentication errors
    if '535' in error_str or 'BadCredentials' in error_str or 'Username and Password not accepted' in error_str:
        return (
            "Gmail authentication failed. This usually means:\n"
            "1. Your App Password is incorrect or expired\n"
            "2. 2-Step Verification is not enabled on your Google account\n"
            "3. The App Password was not generated correctly\n\n"
            "To fix this:\n"
            "• Go to https://myaccount.google.com/apppasswords\n"
            "• Generate a new App Password for 'Mail'\n"
            "• Update your .env file with the new password (16 characters, no spaces)\n"
            "• Make sure 2-Step Verification is enabled\n"
            "• Restart your Django server after updating .env\n\n"
            "See docs/GMAIL_SETUP.md for detailed instructions."
        )
    
    # Generic SMTP authentication errors
    if 'authentication' in error_str.lower() or '535' in error_str:
        return (
            "Email authentication failed. Please check:\n"
            "• Your email credentials in the .env file\n"
            "• You're using an App Password (not your regular password)\n"
            "• Your email settings are correct\n"
            "• Restart the server after changing .env\n\n"
            "See docs/EMAIL_SETUP.md or docs/GMAIL_SETUP.md for help."
        )
    
    # Connection errors
    if 'connection' in error_str.lower() or 'timeout' in error_str.lower():
        return (
            "Could not connect to email server. Please check:\n"
            "• Your internet connection\n"
            "• Email server settings (EMAIL_HOST, EMAIL_PORT)\n"
            "• Firewall settings\n"
        )
    
    # Return original error if we can't categorize it
    return f"Email error: {error_str}\n\nSee docs/EMAIL_SETUP.md or docs/GMAIL_SETUP.md for setup instructions."


def home_view(request):
    arenas = Arena.objects.filter(is_active=True)[:4]
    context = {
        'arenas': arenas,
        'user_tokens': request.user.tokens if request.user.is_authenticated else 0,
    }
    return render(request, "home.html", context)

def arenas_view(request):
    arenas = Arena.objects.filter(is_active=True)
    user_tokens = request.user.tokens if request.user.is_authenticated else 0
    user_arenas = []
    if request.user.is_authenticated:
        user_arenas = [c.arena.id for c in Contestant.objects.filter(user=request.user, is_active=True)]
    
    context = {
        'arenas': arenas,
        'user_tokens': user_tokens,
        'user_arenas': user_arenas,
    }
    return render(request, "arenas.html", context)

def contestants_view(request):
    # Get active arenas and contestants
    arena_id = request.GET.get('arena', None)
    if arena_id:
        arena = get_object_or_404(Arena, id=arena_id, is_active=True)
        contestants = Contestant.objects.filter(arena=arena, is_active=True).order_by('-votes', '-created_at')
        # Get top 3 contestants for specific arena
        top_contestants = list(contestants[:3])
        other_contestants = list(contestants[3:10])  # Next 7 for the list
    else:
        # Show all contestants from all arenas
        arena = None
        all_arenas = Arena.objects.filter(is_active=True).order_by('token_cost')
        
        # Get top contestant from each arena (top 4 arenas)
        top_contestants = []
        for a in all_arenas[:4]:
            top_from_arena = Contestant.objects.filter(arena=a, is_active=True).order_by('-votes', '-created_at').first()
            if top_from_arena:
                top_contestants.append(top_from_arena)
        
        # Get remaining contestants (excluding the top ones already shown)
        top_contestant_ids = [c.id for c in top_contestants]
        other_contestants = Contestant.objects.filter(
            is_active=True
        ).exclude(id__in=top_contestant_ids).order_by('-votes', '-created_at')[:20]
    
    user_tokens = request.user.tokens if request.user.is_authenticated else 0
    user_votes = {}
    if request.user.is_authenticated:
        user_votes = {v.contestant.id: True for v in Vote.objects.filter(user=request.user)}
    
    context = {
        'arena': arena,
        'arenas': Arena.objects.filter(is_active=True),
        'top_contestants': top_contestants,
        'other_contestants': other_contestants,
        'user_tokens': user_tokens,
        'user_votes': user_votes,
    }
    return render(request, "contestants.html", context)

def howitworks_view(request):
    return render(request, "how-it-works.html")

def finaleroyale_view(request):
    return render(request, "finale-royale.html")

@login_required(login_url='/login')
def profile_view(request):
    settings_form = UserSettingsForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)
    delete_form = DeleteAccountForm(request.user)
    email_change_form = EmailChangeForm(request.user)
    
    # Calculate real stats
    user_contestants = Contestant.objects.filter(user=request.user, is_active=True)
    total_votes_received = sum(c.votes for c in user_contestants)
    total_competitions = user_contestants.count()
    
    # Calculate wins (top 3 in any arena)
    wins = 0
    for contestant in user_contestants:
        arena_contestants = Contestant.objects.filter(arena=contestant.arena, is_active=True).order_by('-votes')
        top_3 = list(arena_contestants[:3])
        if contestant in top_3:
            wins += 1
    
    # Calculate rank (average rank across all arenas)
    total_rank = 0
    rank_count = 0
    for contestant in user_contestants:
        arena_contestants = Contestant.objects.filter(arena=contestant.arena, is_active=True).order_by('-votes')
        ranked_list = list(arena_contestants)
        if contestant in ranked_list:
            rank = ranked_list.index(contestant) + 1
            total_rank += rank
            rank_count += 1
    
    avg_rank = int(total_rank / rank_count) if rank_count > 0 else 0
    
    # Get user's highest tier arena
    highest_tier_arena = None
    tier_order = {'elite': 4, 'champion': 3, 'veteran': 2, 'recruit': 1}
    for contestant in user_contestants:
        if highest_tier_arena is None or tier_order.get(contestant.arena.tier, 0) > tier_order.get(highest_tier_arena.tier, 0):
            highest_tier_arena = contestant.arena
    
    # Get user's submissions (contestants) with ranks
    user_submissions = []
    for contestant in user_contestants.order_by('-created_at'):
        arena_contestants = list(Contestant.objects.filter(arena=contestant.arena, is_active=True).order_by('-votes'))
        rank = arena_contestants.index(contestant) + 1 if contestant in arena_contestants else 0
        user_submissions.append({
            'contestant': contestant,
            'rank': rank
        })
    
    # Build recent activity list from real data
    recent_activities = []
    
    # 1. Contestant submissions
    for contestant in user_contestants.order_by('-created_at')[:5]:
        submission_type = 'video' if contestant.video_url or contestant.video_file else 'image'
        recent_activities.append({
            'type': 'submission',
            'date': contestant.created_at,
            'icon': '📹' if submission_type == 'video' else '🖼️',
            'message': f'Submitted {submission_type} to {contestant.arena.name}',
            'contestant': contestant
        })
    
    # 2. Votes received (get votes on user's contestants)
    user_contestant_ids = [c.id for c in user_contestants]
    votes_received = Vote.objects.filter(contestant_id__in=user_contestant_ids).order_by('-created_at')[:5]
    for vote in votes_received:
        recent_activities.append({
            'type': 'vote',
            'date': vote.created_at,
            'icon': '👍',
            'message': f'Received a vote on "{vote.contestant.title}"',
            'contestant': vote.contestant
        })
    
    # 3. Token purchases
    completed_payments = Payment.objects.filter(user=request.user, status='completed').order_by('-completed_at')[:5]
    for payment in completed_payments:
        recent_activities.append({
            'type': 'purchase',
            'date': payment.completed_at or payment.created_at,
            'icon': '🪙',
            'message': f'Purchased {payment.tokens} tokens',
            'amount': payment.amount
        })
    
    # 4. Wins/Top placements (check current rankings for top 3 placements)
    # Only add wins if they're currently in top 3
    for contestant in user_contestants:
        arena_contestants = list(Contestant.objects.filter(arena=contestant.arena, is_active=True).order_by('-votes'))
        if contestant in arena_contestants:
            rank = arena_contestants.index(contestant) + 1
            if rank <= 3:
                # Use the most recent vote date if available, otherwise use submission date
                latest_vote = Vote.objects.filter(contestant=contestant).order_by('-created_at').first()
                win_date = latest_vote.created_at if latest_vote else contestant.created_at
                
                if rank == 1:
                    recent_activities.append({
                        'type': 'win',
                        'date': win_date,
                        'icon': '🏆',
                        'message': f'Won {contestant.arena.name} (1st place)',
                        'contestant': contestant
                    })
                elif rank == 2:
                    recent_activities.append({
                        'type': 'win',
                        'date': win_date,
                        'icon': '🥈',
                        'message': f'Placed 2nd in {contestant.arena.name}',
                        'contestant': contestant
                    })
                elif rank == 3:
                    recent_activities.append({
                        'type': 'win',
                        'date': win_date,
                        'icon': '🥉',
                        'message': f'Placed 3rd in {contestant.arena.name}',
                        'contestant': contestant
                    })
    
    # 5. Tier achievements (when they first reached each tier)
    tier_achievements = {}
    for contestant in user_contestants.order_by('created_at'):
        tier = contestant.arena.tier
        if tier not in tier_achievements:
            tier_names = {
                'recruit': 'Recruit',
                'veteran': 'Veteran',
                'champion': 'Champion',
                'elite': 'Elite'
            }
            tier_icons = {
                'recruit': '🎖️',
                'veteran': '🥈',
                'champion': '🥇',
                'elite': '🏆'
            }
            recent_activities.append({
                'type': 'tier',
                'date': contestant.created_at,
                'icon': tier_icons.get(tier, '⭐'),
                'message': f'Reached {tier_names.get(tier, tier)} tier',
                'tier': tier
            })
            tier_achievements[tier] = True
    
    # Sort activities by date (most recent first) and limit to 10
    recent_activities.sort(key=lambda x: x['date'], reverse=True)
    recent_activities = recent_activities[:10]
    
    # Calculate achievements
    achievements = []
    if highest_tier_arena and highest_tier_arena.tier == 'elite':
        achievements.append({'name': 'Elite Competitor', 'description': 'Reached Elite tier', 'earned': True, 'icon': '🏆'})
    elif highest_tier_arena and highest_tier_arena.tier == 'champion':
        achievements.append({'name': 'Champion Competitor', 'description': 'Reached Champion tier', 'earned': True, 'icon': '🥇'})
    elif highest_tier_arena and highest_tier_arena.tier == 'veteran':
        achievements.append({'name': 'Veteran Competitor', 'description': 'Reached Veteran tier', 'earned': True, 'icon': '🥈'})
    elif highest_tier_arena and highest_tier_arena.tier == 'recruit':
        achievements.append({'name': 'Recruit Competitor', 'description': 'Reached Recruit tier', 'earned': True, 'icon': '🎖️'})
    
    if avg_rank > 0 and avg_rank <= 10:
        achievements.append({'name': 'Top Performer', 'description': f'Placed in top 10 (Rank #{avg_rank})', 'earned': True, 'icon': '⭐'})
    
    if wins > 0:
        achievements.append({'name': 'Winner', 'description': f'Won {wins} competition(s)', 'earned': True, 'icon': '👑'})
    
    # Finale Royale achievement (if in top 3)
    finale_eligible = False
    for contestant in user_contestants:
        arena_contestants = Contestant.objects.filter(arena=contestant.arena, is_active=True).order_by('-votes')
        top_3 = list(arena_contestants[:3])
        if contestant in top_3:
            finale_eligible = True
            break
    
    if finale_eligible:
        achievements.append({'name': 'Finale Royale', 'description': 'Eligible for year-end tournament', 'earned': True, 'icon': '👑'})
    else:
        achievements.append({'name': 'Finale Royale', 'description': 'Enter year-end tournament', 'earned': False, 'icon': '👑'})
    
    # Calculate next goal and progress
    next_goal = None
    goal_progress = 0
    
    if total_competitions == 0:
        # First goal: Make first submission
        next_goal = {
            'title': 'Make Your First Submission',
            'description': 'Join an arena and submit your talent',
            'progress': 0,
            'target': 1,
            'current': 0
        }
    elif not highest_tier_arena:
        # Goal: Join any arena
        next_goal = {
            'title': 'Join Your First Arena',
            'description': 'Enter a competition to start competing',
            'progress': 0,
            'target': 1,
            'current': 0
        }
    elif highest_tier_arena.tier == 'recruit':
        # Goal: Reach Veteran tier
        next_goal = {
            'title': 'Reach Veteran Tier',
            'description': 'Join a Veteran tier arena to advance',
            'progress': 25,
            'target': 1,
            'current': 0
        }
    elif highest_tier_arena.tier == 'veteran':
        # Goal: Reach Champion tier
        next_goal = {
            'title': 'Reach Champion Tier',
            'description': 'Join a Champion tier arena to advance',
            'progress': 50,
            'target': 1,
            'current': 0
        }
    elif highest_tier_arena.tier == 'champion':
        # Goal: Reach Elite tier
        next_goal = {
            'title': 'Reach Elite Tier',
            'description': 'Join an Elite tier arena to unlock Finale Royale',
            'progress': 75,
            'target': 1,
            'current': 0
        }
    elif highest_tier_arena.tier == 'elite':
        # Goal: Reach Finale Royale (top 3 in Elite)
        if finale_eligible:
            next_goal = {
                'title': 'Finale Royale Qualified!',
                'description': 'You\'ve qualified for the year-end tournament',
                'progress': 100,
                'target': 1,
                'current': 1
            }
        else:
            # Calculate progress based on rank in Elite arena
            elite_contestants = Contestant.objects.filter(arena=highest_tier_arena, is_active=True).order_by('-votes')
            elite_ranked = list(elite_contestants)
            user_elite_contestant = None
            for contestant in user_contestants:
                if contestant.arena == highest_tier_arena:
                    user_elite_contestant = contestant
                    break
            
            if user_elite_contestant and user_elite_contestant in elite_ranked:
                current_rank = elite_ranked.index(user_elite_contestant) + 1
                # Progress: closer to top 3 = higher percentage
                # If rank 4-10, show progress based on how close to top 3
                if current_rank <= 3:
                    progress = 100
                elif current_rank <= 10:
                    # Progress from 50% (rank 10) to 99% (rank 4)
                    progress = 100 - ((current_rank - 3) * 7)
                else:
                    # Progress from 0% to 50% for ranks 11+
                    progress = max(0, 50 - ((current_rank - 10) * 5))
                
                next_goal = {
                    'title': 'Reach Finale Royale',
                    'description': f'Place in top 3 (Currently rank #{current_rank})',
                    'progress': progress,
                    'target': 3,
                    'current': current_rank
                }
            else:
                next_goal = {
                    'title': 'Reach Finale Royale',
                    'description': 'Place in top 3 in Elite tier to qualify',
                    'progress': 0,
                    'target': 3,
                    'current': 0
                }
    
    if request.method == 'POST':
        if 'change_email' in request.POST:
            email_change_form = EmailChangeForm(request.user, request.POST)
            if email_change_form.is_valid():
                current_email = request.user.email
                new_email = email_change_form.cleaned_data.get('new_email')
                
                # Get user instance
                user = CustomUser.objects.get(id=request.user.id)
                
                # Update email and mark as unconfirmed
                user.email = new_email
                user.email_confirmed = False
                user.save()
                
                # Invalidate all old tokens
                EmailConfirmationToken.objects.filter(user=user, used=False).update(used=True)
                
                # Create new confirmation token
                confirmation_token = EmailConfirmationToken.objects.create(
                    user=user,
                    token_type='email_change'
                )
                
                # Build confirmation URL and code
                confirmation_url = request.build_absolute_uri(f'/confirm-email/{confirmation_token.token}/')
                confirmation_code = str(confirmation_token.token).replace('-', '').upper()[:8]
                
                # Send confirmation email to NEW email address
                try:
                    email_html = render_to_string('emails/email_confirmation.html', {
                        'username': user.username,
                        'confirmation_url': confirmation_url,
                        'confirmation_code': confirmation_code,
                        'token_type': 'email_change',
                        'new_email': new_email,
                    })
                    
                    send_mail(
                        'Confirm Your New Email - Talents Royale',
                        f'Hello {user.username},\n\nYour email has been changed to {new_email}.\n\nPlease confirm this new email address by visiting: {confirmation_url}\n\nOr use this code: {confirmation_code}\n\nYou must confirm this email before you can log in again.',
                        settings.DEFAULT_FROM_EMAIL,
                        [new_email],
                        html_message=email_html,
                        fail_silently=False,
                    )
                    
                    # Logout user immediately
                    logout(request)
                    messages.success(request, f'Email updated to {new_email}. A confirmation email has been sent. Please check your inbox and confirm your email before logging in again.')
                    return redirect('login')
                    
                except Exception as e:
                    # If email fails, revert the email change
                    user.email = current_email
                    user.email_confirmed = True  # Restore old confirmation status
                    user.save()
                    
                    error_msg = get_email_error_message(e)
                    messages.error(request, f'Failed to send confirmation email. Email was not changed.\n\n{error_msg}')
                    logger.error(f"Email send error during email change: {str(e)}", exc_info=True)
                    email_change_form = EmailChangeForm(request.user)
            else:
                messages.error(request, 'Please correct the errors below.')
        
        elif 'update_settings' in request.POST:
            settings_form = UserSettingsForm(request.POST, request.FILES, instance=request.user)
            if settings_form.is_valid():
                # Just save profile fields (username, bio, photo) - no email handling
                user = settings_form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile')
            else:
                messages.error(request, 'Please correct the errors below.')
        
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                new_password = password_form.cleaned_data['new_password1']
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, 'Password changed successfully! Please log in again.')
                return redirect('login')
            else:
                messages.error(request, 'Please correct the errors below.')
        
        elif 'delete_account' in request.POST:
            delete_form = DeleteAccountForm(request.user, request.POST)
            if delete_form.is_valid():
                # Send goodbye email before deletion
                try:
                    send_mail(
                        'Account Deleted - Talents Royale',
                        f'Hello {request.user.username},\n\nYour Talents Royale account has been successfully deleted.\n\nWe\'re sorry to see you go! If you change your mind, you\'re always welcome to create a new account.\n\nBest regards,\nThe Talents Royale Team',
                        settings.DEFAULT_FROM_EMAIL,
                        [request.user.email],
                        fail_silently=False,
                    )
                except (smtplib.SMTPAuthenticationError, smtplib.SMTPException, Exception) as e:
                    # Continue with deletion even if email fails, but log the error
                    logger.warning(f"Could not send account deletion email: {str(e)}")
                
                username = request.user.username
                request.user.delete()
                messages.success(request, f'Account for {username} has been permanently deleted.')
                return redirect('home')
            else:
                messages.error(request, 'Please correct the errors below.')
    
    context = {
        'settings_form': settings_form,
        'password_form': password_form,
        'delete_form': delete_form,
        'email_change_form': email_change_form,
        'total_votes': total_votes_received,
        'total_competitions': total_competitions,
        'wins': wins,
        'avg_rank': avg_rank,
        'highest_tier_arena': highest_tier_arena,
        'user_submissions': user_submissions,
        'achievements': achievements,
        'next_goal': next_goal,
        'recent_activities': recent_activities,
    }
    
    return render(request, "profile.html", context)

def signin_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    
    unconfirmed_email = None
    show_resend_option = False
    
    if request.method == 'POST':
        # Check if this is a resend confirmation request
        if 'resend_confirmation' in request.POST:
            username = request.POST.get('username')
            try:
                user = CustomUser.objects.get(username=username)
                if not user.email_confirmed:
                    try:
                        # Invalidate old tokens
                        EmailConfirmationToken.objects.filter(user=user, token_type='registration', used=False).update(used=True)
                        
                        # Create new confirmation token
                        confirmation_token = EmailConfirmationToken.objects.create(
                            user=user,
                            token_type='registration'
                        )
                        
                        confirmation_code = str(confirmation_token.token).replace('-', '').upper()[:8]
                        confirmation_url = request.build_absolute_uri(f'/confirm-email/{confirmation_token.token}/')
                        
                        email_html = render_to_string('emails/email_confirmation.html', {
                            'username': user.username,
                            'confirmation_url': confirmation_url,
                            'confirmation_code': confirmation_code,
                            'token_type': 'registration',
                        })
                        
                        send_mail(
                            'Confirm Your Email - Talents Royale',
                            f'Hello {user.username},\n\nPlease confirm your email by visiting: {confirmation_url}\n\nOr use this code: {confirmation_code}',
                            settings.DEFAULT_FROM_EMAIL,
                            [user.email],
                            html_message=email_html,
                            fail_silently=False,
                        )
                        messages.success(request, f'A new confirmation email has been sent to {user.email}. Please check your inbox.')
                    except (smtplib.SMTPAuthenticationError, smtplib.SMTPException, Exception) as e:
                        error_msg = get_email_error_message(e)
                        messages.error(request, f'Could not send confirmation email.\n\n{error_msg}')
                        logger.error(f"Email send error: {str(e)}", exc_info=True)
                else:
                    messages.info(request, 'Your email is already confirmed. You can log in.')
            except CustomUser.DoesNotExist:
                messages.error(request, 'User not found.')
            
            form = LoginForm()
            return render(request, "signin.html", {'form': form, 'unconfirmed_email': unconfirmed_email, 'show_resend_option': show_resend_option})
        
        # Regular login attempt
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Check if email is confirmed
            if not user.email_confirmed:
                unconfirmed_email = user.email
                show_resend_option = True
                messages.warning(request, 'Please confirm your email address before logging in. A confirmation email has been sent to your inbox.')
                # Automatically resend confirmation email
                try:
                    # Invalidate old tokens
                    EmailConfirmationToken.objects.filter(user=user, token_type='registration', used=False).update(used=True)
                    
                    # Create new confirmation token
                    confirmation_token = EmailConfirmationToken.objects.create(
                        user=user,
                        token_type='registration'
                    )
                    
                    confirmation_code = str(confirmation_token.token).replace('-', '').upper()[:8]
                    confirmation_url = request.build_absolute_uri(f'/confirm-email/{confirmation_token.token}/')
                    
                    email_html = render_to_string('emails/email_confirmation.html', {
                        'username': user.username,
                        'confirmation_url': confirmation_url,
                        'confirmation_code': confirmation_code,
                        'token_type': 'registration',
                    })
                    
                    send_mail(
                        'Confirm Your Email - Talents Royale',
                        f'Hello {user.username},\n\nPlease confirm your email by visiting: {confirmation_url}\n\nOr use this code: {confirmation_code}',
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        html_message=email_html,
                        fail_silently=False,
                    )
                    messages.info(request, f'A confirmation email has been sent to {user.email}.')
                except (smtplib.SMTPAuthenticationError, smtplib.SMTPException, Exception) as e:
                    error_msg = get_email_error_message(e)
                    messages.error(request, f'Could not send confirmation email.\n\n{error_msg}')
                    logger.error(f"Email send error: {str(e)}", exc_info=True)
                return render(request, "signin.html", {'form': form, 'unconfirmed_email': unconfirmed_email, 'show_resend_option': show_resend_option, 'username': user.username})
            
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            # Redirect to next page if specified, otherwise to profile
            next_page = request.GET.get('next', 'profile')
            return redirect(next_page)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, "signin.html", {'form': form, 'unconfirmed_email': unconfirmed_email, 'show_resend_option': show_resend_option})

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.email_confirmed = False
            user.save()
            
            # Create confirmation token
            confirmation_token = EmailConfirmationToken.objects.create(
                user=user,
                token_type='registration'
            )
            
            # Generate confirmation code (first 8 characters of UUID)
            confirmation_code = str(confirmation_token.token).replace('-', '').upper()[:8]
            
            # Build confirmation URL
            confirmation_url = request.build_absolute_uri(
                f'/confirm-email/{confirmation_token.token}/'
            )
            
            # Send confirmation email
            try:
                email_subject = 'Confirm Your Email - Talents Royale'
                email_html = render_to_string('emails/email_confirmation.html', {
                    'username': user.username,
                    'confirmation_url': confirmation_url,
                    'confirmation_code': confirmation_code,
                    'token_type': 'registration',
                })
                
                send_mail(
                    email_subject,
                    f'Hello {user.username},\n\nPlease confirm your email by visiting: {confirmation_url}\n\nOr use this code: {confirmation_code}\n\nThis link expires in 24 hours.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=email_html,
                    fail_silently=False,
                )
                
                messages.success(request, f'Account created! Please check your email ({user.email}) to confirm your account. The confirmation link expires in 24 hours.')
            except (smtplib.SMTPAuthenticationError, smtplib.SMTPException, Exception) as e:
                error_msg = get_email_error_message(e)
                messages.warning(request, f'Account created, but we couldn\'t send the confirmation email.\n\n{error_msg}')
                # Also log the full error for debugging
                logger.error(f"Email send error: {str(e)}", exc_info=True)
            
            # Don't auto-login, require email confirmation
            messages.info(request, 'Please confirm your email before logging in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignupForm()
    
    return render(request, "signup.html", {'form': form})

def confirm_email(request, token):
    """Handle email confirmation via token"""
    try:
        confirmation_token = get_object_or_404(EmailConfirmationToken, token=token, used=False)
        
        # Check if token is expired
        if confirmation_token.is_expired():
            messages.error(request, 'This confirmation link has expired. Please request a new one.')
            return redirect('login')
        
        user = confirmation_token.user
        
        if confirmation_token.token_type == 'registration':
            # Confirm registration
            user.email_confirmed = True
            user.save()
            confirmation_token.used = True
            confirmation_token.save()
            
            messages.success(request, 'Email confirmed successfully! You can now log in.')
            return redirect('login')
        
        elif confirmation_token.token_type == 'email_change':
            # Legacy email_change tokens - handle them as registration tokens
            # This is for backwards compatibility with old tokens
            user.email_confirmed = True
            user.save()
            confirmation_token.used = True
            confirmation_token.save()
            
            messages.success(request, 'Email confirmed successfully! You can now log in.')
            return redirect('login')
        
    except Exception as e:
        messages.error(request, f'Invalid or expired confirmation link. Error: {str(e)}')
    
    return redirect('home')

@login_required
def resend_confirmation(request):
    """Resend email confirmation"""
    user = request.user
    
    if user.email_confirmed:
        messages.info(request, 'Your email is already confirmed.')
        return redirect('profile')
    
    try:
        # Invalidate old tokens
        EmailConfirmationToken.objects.filter(user=user, token_type='registration', used=False).update(used=True)
        
        # Create new confirmation token
        confirmation_token = EmailConfirmationToken.objects.create(
            user=user,
            token_type='registration'
        )
        
        confirmation_code = str(confirmation_token.token).replace('-', '').upper()[:8]
        confirmation_url = request.build_absolute_uri(f'/confirm-email/{confirmation_token.token}/')
        
        email_html = render_to_string('emails/email_confirmation.html', {
            'username': user.username,
            'confirmation_url': confirmation_url,
            'confirmation_code': confirmation_code,
            'token_type': 'registration',
        })
        
        send_mail(
            'Confirm Your Email - Talents Royale',
            f'Hello {user.username},\n\nPlease confirm your email by visiting: {confirmation_url}\n\nOr use this code: {confirmation_code}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=email_html,
            fail_silently=False,
        )
        
        messages.success(request, f'Confirmation email sent to {user.email}. Please check your inbox.')
    except (smtplib.SMTPAuthenticationError, smtplib.SMTPException, Exception) as e:
        error_msg = get_email_error_message(e)
        messages.error(request, f'Could not send confirmation email.\n\n{error_msg}')
        logger.error(f"Email send error: {str(e)}", exc_info=True)
    
    return redirect('profile')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

def forgot_password_view(request):
    """Handle forgot password requests"""
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            try:
                # Find user by email (case-insensitive)
                user = CustomUser.objects.get(email__iexact=email)
                
                # Invalidate any existing password reset tokens
                EmailConfirmationToken.objects.filter(
                    user=user,
                    token_type='password_reset',
                    used=False
                ).update(used=True)
                
                # Create new password reset token
                reset_token = EmailConfirmationToken.objects.create(
                    user=user,
                    token_type='password_reset'
                )
                
                reset_url = request.build_absolute_uri(f'/reset-password/{reset_token.token}/')
                reset_code = str(reset_token.token).replace('-', '').upper()[:8]
                
                # Send password reset email
                try:
                    email_html = render_to_string('emails/password_reset.html', {
                        'username': user.username,
                        'reset_url': reset_url,
                        'reset_code': reset_code,
                    })
                    
                    send_mail(
                        'Reset Your Password - Talents Royale',
                        f'Hello {user.username},\n\nYou requested to reset your password. Click the link below to reset it:\n\n{reset_url}\n\nOr use this code: {reset_code}\n\nThis link will expire in 24 hours. If you didn\'t request this, please ignore this email.',
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        html_message=email_html,
                        fail_silently=False,
                    )
                    
                    # Always show success message (security: don't reveal if email exists)
                    messages.success(request, 'If an account with that email exists, a password reset link has been sent to your email address.')
                    return redirect('login')
                except (smtplib.SMTPAuthenticationError, smtplib.SMTPException, Exception) as e:
                    error_msg = get_email_error_message(e)
                    messages.error(request, f'Could not send password reset email.\n\n{error_msg}')
                    logger.error(f"Email send error during password reset: {str(e)}", exc_info=True)
            except CustomUser.DoesNotExist:
                # Don't reveal if email exists for security
                messages.success(request, 'If an account with that email exists, a password reset link has been sent to your email address.')
                return redirect('login')
    else:
        form = ForgotPasswordForm()
    
    return render(request, 'forgot_password.html', {'form': form})

def reset_password_view(request, token):
    """Handle password reset with token"""
    if request.user.is_authenticated:
        return redirect('profile')
    
    try:
        reset_token = EmailConfirmationToken.objects.get(
            token=token,
            token_type='password_reset',
            used=False
        )
        
        # Check if token is expired
        if reset_token.is_expired():
            messages.error(request, 'This password reset link has expired. Please request a new one.')
            return redirect('forgot_password')
        
        if request.method == 'POST':
            form = ResetPasswordForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data.get('new_password1')
                user = reset_token.user
                
                # Set new password
                user.set_password(new_password)
                user.save()
                
                # Mark token as used
                reset_token.used = True
                reset_token.save()
                
                messages.success(request, 'Your password has been reset successfully. You can now log in with your new password.')
                return redirect('login')
        else:
            form = ResetPasswordForm()
        
        return render(request, 'reset_password.html', {'form': form, 'token': token})
    
    except EmailConfirmationToken.DoesNotExist:
        messages.error(request, 'Invalid or expired password reset link. Please request a new one.')
        return redirect('forgot_password')

@login_required
@require_POST
def vote_contestant(request):
    """Handle voting for a contestant"""
    try:
        data = json.loads(request.body)
        contestant_id = data.get('contestant_id')
        use_tokens = data.get('use_tokens', False)  # If True, spend tokens for extra vote
        
        contestant = get_object_or_404(Contestant, id=contestant_id, is_active=True)
        user = request.user
        
        # Check if user already voted
        existing_vote = Vote.objects.filter(user=user, contestant=contestant).first()
        
        if existing_vote:
            if not use_tokens:
                return JsonResponse({'success': False, 'message': 'You have already voted for this contestant. Use tokens to vote again.'})
            # User wants to vote again with tokens
            token_cost = 5  # Cost for additional vote
            if user.tokens < token_cost:
                return JsonResponse({'success': False, 'message': f'Insufficient tokens. You need {token_cost} tokens.'})
            
            # Deduct tokens and add vote
            with transaction.atomic():
                user.tokens -= token_cost
                user.save()
                contestant.votes += 1
                contestant.save()
                TokenTransaction.objects.create(
                    user=user,
                    transaction_type='vote',
                    amount=-token_cost,
                    description=f'Additional vote for {contestant.user.username}',
                    related_contestant=contestant
                )
            return JsonResponse({
                'success': True, 
                'message': 'Vote cast successfully!',
                'new_votes': contestant.votes,
                'remaining_tokens': user.tokens
            })
        else:
            # First vote is free
            with transaction.atomic():
                vote = Vote.objects.create(
                    user=user,
                    contestant=contestant,
                    is_free_vote=True,
                    tokens_spent=0
                )
                contestant.votes += 1
                contestant.save()
            
            return JsonResponse({
                'success': True, 
                'message': 'Free vote cast successfully!',
                'new_votes': contestant.votes,
                'remaining_tokens': user.tokens
            })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
def submit_entry(request, arena_id):
    """Page to submit entry for an arena"""
    arena = get_object_or_404(Arena, id=arena_id, is_active=True)
    user = request.user
    
    # Check if user already in this arena
    existing_contestant = Contestant.objects.filter(user=user, arena=arena, is_active=True).first()
    if existing_contestant:
        messages.warning(request, 'You are already participating in this arena.')
        return redirect('arenas')
    
    # Check token balance
    if user.tokens < arena.token_cost:
        messages.error(request, f'Insufficient tokens. You need {arena.token_cost} tokens to join {arena.name}.')
        return redirect('arenas')
    
    # Check if arena is full
    current_participants = Contestant.objects.filter(arena=arena, is_active=True).count()
    if current_participants >= arena.max_participants:
        messages.error(request, 'This arena is full.')
        return redirect('arenas')
    
    if request.method == 'POST':
        form = ContestantSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            # Deduct tokens and create contestant entry
            with transaction.atomic():
                user.tokens -= arena.token_cost
                user.save()
                
                contestant = form.save(commit=False)
                contestant.user = user
                contestant.arena = arena
                contestant.votes = 0
                contestant.save()
                
                TokenTransaction.objects.create(
                    user=user,
                    transaction_type='arena_entry',
                    amount=-arena.token_cost,
                    description=f'Joined {arena.name}',
                    related_arena=arena,
                    related_contestant=contestant
                )
            
            messages.success(request, f'Successfully submitted your entry to {arena.name}!')
            return redirect('contestants')
    else:
        form = ContestantSubmissionForm()
    
    context = {
        'arena': arena,
        'form': form,
        'token_cost': arena.token_cost,
        'user_tokens': user.tokens,
    }
    return render(request, 'submit_entry.html', context)

@login_required
@require_POST
def join_arena(request):
    """Handle joining an arena/tournament - redirects to submission page"""
    try:
        data = json.loads(request.body)
        arena_id = data.get('arena_id')
        
        arena = get_object_or_404(Arena, id=arena_id, is_active=True)
        user = request.user
        
        # Check if user already in this arena
        existing_contestant = Contestant.objects.filter(user=user, arena=arena, is_active=True).first()
        if existing_contestant:
            return JsonResponse({'success': False, 'message': 'You are already participating in this arena.'})
        
        # Check token balance
        if user.tokens < arena.token_cost:
            return JsonResponse({
                'success': False, 
                'message': f'Insufficient tokens. You need {arena.token_cost} tokens to join {arena.name}.'
            })
        
        # Check if arena is full
        current_participants = Contestant.objects.filter(arena=arena, is_active=True).count()
        if current_participants >= arena.max_participants:
            return JsonResponse({'success': False, 'message': 'This arena is full.'})
        
        # Redirect to submission page
        return JsonResponse({
            'success': True, 
            'redirect': f'/submit-entry/{arena_id}/'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

def contestant_detail(request, contestant_id):
    """Display detailed view of a contestant's submission"""
    contestant = get_object_or_404(Contestant, id=contestant_id, is_active=True)
    
    user_tokens = request.user.tokens if request.user.is_authenticated else 0
    has_voted = False
    if request.user.is_authenticated:
        has_voted = Vote.objects.filter(user=request.user, contestant=contestant).exists()
    
    context = {
        'contestant': contestant,
        'user_tokens': user_tokens,
        'has_voted': has_voted,
    }
    return render(request, 'contestant_detail.html', context)

@login_required
def voting_history(request):
    """Display user's voting history"""
    votes = Vote.objects.filter(user=request.user).select_related('contestant', 'contestant__user', 'contestant__arena').order_by('-created_at')
    
    context = {
        'votes': votes,
        'total_votes': votes.count(),
        'free_votes': votes.filter(is_free_vote=True).count(),
        'paid_votes': votes.filter(is_free_vote=False).count(),
    }
    return render(request, 'voting_history.html', context)

@login_required
def purchase_tokens(request):
    """Display token packages for purchase"""
    packages = settings.TOKEN_PACKAGES
    user_tokens = request.user.tokens
    
    context = {
        'packages': packages,
        'user_tokens': user_tokens,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, 'purchase_tokens.html', context)

@login_required
@require_POST
def create_checkout_session(request):
    """Create Stripe Checkout session for token purchase"""
    if not settings.STRIPE_SECRET_KEY:
        return JsonResponse({'error': 'Stripe is not configured. Please contact support.'}, status=400)
    
    try:
        data = json.loads(request.body)
        tokens = int(data.get('tokens'))
        
        # Find the package
        package = None
        for pkg in settings.TOKEN_PACKAGES:
            if pkg['tokens'] == tokens:
                package = pkg
                break
        
        if not package:
            return JsonResponse({'error': 'Invalid token package.'}, status=400)
        
        # Create payment record
        payment = Payment.objects.create(
            user=request.user,
            amount=package['price'],
            tokens=tokens,
            status='pending'
        )
        
        # Create Stripe Checkout session
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'{package["name"]} - {tokens} Tokens',
                            'description': f'Purchase {tokens} tokens for Talents Royale',
                        },
                        'unit_amount': int(package['price'] * 100),  # Convert to cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri(reverse('payment_success')) + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
                metadata={
                    'payment_id': payment.id,
                    'user_id': request.user.id,
                    'tokens': tokens,
                },
                customer_email=request.user.email,
            )
            
            # Update payment with session ID
            payment.stripe_session_id = checkout_session.id
            payment.save()
            
            return JsonResponse({'sessionId': checkout_session.id})
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            payment.status = 'failed'
            payment.save()
            return JsonResponse({'error': f'Payment processing error: {str(e)}'}, status=400)
            
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'An error occurred. Please try again.'}, status=500)

@login_required
def payment_success(request):
    """Handle successful payment"""
    session_id = request.GET.get('session_id')
    
    if not session_id:
        messages.error(request, 'Invalid payment session.')
        return redirect('purchase_tokens')
    
    try:
        # Retrieve the session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Find the payment
        payment = Payment.objects.filter(stripe_session_id=session_id).first()
        
        if not payment:
            messages.error(request, 'Payment record not found.')
            return redirect('purchase_tokens')
        
        # Check if payment is already completed
        if payment.status == 'completed':
            messages.info(request, 'This payment has already been processed.')
            return redirect('profile')
        
        # Verify the session is paid
        if session.payment_status == 'paid':
            # Process the payment
            with transaction.atomic():
                payment.status = 'completed'
                payment.completed_at = timezone.now()
                payment.stripe_payment_intent_id = session.payment_intent
                payment.save()
                
                # Add tokens to user
                payment.user.tokens += payment.tokens
                payment.user.save()
                
                # Create transaction record
                TokenTransaction.objects.create(
                    user=payment.user,
                    transaction_type='purchase',
                    amount=payment.tokens,
                    description=f'Purchased {payment.tokens} tokens for ${payment.amount}',
                    related_payment=payment
                )
            
            messages.success(request, f'Payment successful! {payment.tokens} tokens have been added to your account.')
            return redirect('profile')
        else:
            messages.warning(request, 'Payment is still processing. Please wait a moment and refresh.')
            return redirect('purchase_tokens')
            
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error in payment_success: {str(e)}")
        messages.error(request, 'Error verifying payment. Please contact support if tokens were not added.')
        return redirect('purchase_tokens')
    except Exception as e:
        logger.error(f"Error in payment_success: {str(e)}", exc_info=True)
        messages.error(request, 'An error occurred. Please contact support if tokens were not added.')
        return redirect('purchase_tokens')

@login_required
def payment_cancel(request):
    """Handle cancelled payment"""
    messages.info(request, 'Payment was cancelled. No charges were made.')
    return redirect('purchase_tokens')

@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    if not settings.STRIPE_WEBHOOK_SECRET:
        logger.warning("Stripe webhook secret not configured")
        return HttpResponse(status=400)
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        logger.error("Invalid payload")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid signature")
        return HttpResponse(status=400)
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session(session)
    elif event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        handle_payment_intent(payment_intent)
    
    return HttpResponse(status=200)

def handle_checkout_session(session):
    """Handle completed checkout session"""
    try:
        payment = Payment.objects.filter(stripe_session_id=session['id']).first()
        
        if not payment:
            logger.warning(f"Payment not found for session {session['id']}")
            return
        
        if payment.status == 'completed':
            logger.info(f"Payment {payment.id} already completed")
            return
        
        # Process the payment
        with transaction.atomic():
            payment.status = 'completed'
            payment.completed_at = timezone.now()
            payment.stripe_payment_intent_id = session.get('payment_intent')
            payment.save()
            
            # Add tokens to user
            payment.user.tokens += payment.tokens
            payment.user.save()
            
            # Create transaction record
            TokenTransaction.objects.create(
                user=payment.user,
                transaction_type='purchase',
                amount=payment.tokens,
                description=f'Purchased {payment.tokens} tokens for ${payment.amount}',
                related_payment=payment
            )
        
        logger.info(f"Payment {payment.id} processed successfully via webhook")
        
    except Exception as e:
        logger.error(f"Error handling checkout session: {str(e)}", exc_info=True)

def handle_payment_intent(payment_intent):
    """Handle successful payment intent"""
    # This can be used for additional verification if needed
    logger.info(f"Payment intent succeeded: {payment_intent['id']}")
