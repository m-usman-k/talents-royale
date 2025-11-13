from django.urls import path
from .views import contestants_view
from .views import signin_view, signup_view, logout_view
from .views import howitworks_view, finaleroyale_view
from .views import home_view, arenas_view, profile_view
from .views import vote_contestant, join_arena, submit_entry, contestant_detail, voting_history, confirm_email, resend_confirmation
from .views import purchase_tokens, create_checkout_session, payment_success, payment_cancel, stripe_webhook
from .views import forgot_password_view, reset_password_view, participation_agreement_view

urlpatterns = [
    path("", home_view, name="home"),
    path("arenas", arenas_view, name="arenas"),
    path("contestants", contestants_view, name="contestants"),
    path("how-it-works", howitworks_view, name="howitworks"),
    path("finale-royale", finaleroyale_view, name="finaleroyale"),
    path("participation-agreement", participation_agreement_view, name="participation_agreement"),
    path("login", signin_view, name="login"),
    path("signup", signup_view, name="signup"),
    path("logout", logout_view, name="logout"),
    path("forgot-password/", forgot_password_view, name="forgot_password"),
    path("reset-password/<uuid:token>/", reset_password_view, name="reset_password"),
    path("profile", profile_view, name="profile"),
    path("api/vote/", vote_contestant, name="vote_contestant"),
    path("api/join-arena/", join_arena, name="join_arena"),
    path("submit-entry/<int:arena_id>/", submit_entry, name="submit_entry"),
    path("contestant/<int:contestant_id>/", contestant_detail, name="contestant_detail"),
    path("voting-history/", voting_history, name="voting_history"),
    path("confirm-email/<uuid:token>/", confirm_email, name="confirm_email"),
    path("resend-confirmation/", resend_confirmation, name="resend_confirmation"),
    path("purchase-tokens/", purchase_tokens, name="purchase_tokens"),
    path("api/create-checkout-session/", create_checkout_session, name="create_checkout_session"),
    path("payment/success/", payment_success, name="payment_success"),
    path("payment/cancel/", payment_cancel, name="payment_cancel"),
    path("webhooks/stripe/", stripe_webhook, name="stripe_webhook"),
]
