# Third Party Stuff
from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, View

from .services import get_token_for_user


class LoginView(FormView):
    """
    Provides the ability to login as a user with a email and password
    """
    success_url = '/'
    form_class = AuthenticationForm  # forms.LoginForm
    redirect_field_name = REDIRECT_FIELD_NAME
    template_name = 'pages/login.html'

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        # Sets a test cookie to make sure the user has cookies enabled
        request.session.set_test_cookie()

        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        auth_login(self.request, form.get_user())

        # If the test cookie worked, go ahead and
        # delete it since its no longer needed
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()

        return super(LoginView, self).form_valid(form)

    def get_success_url(self):
        redirect_to = self.request.POST.get(self.redirect_field_name,
                                            self.request.GET.get(self.redirect_field_name))
        if not is_safe_url(url=redirect_to, host=self.request.get_host()):
            redirect_to = self.success_url
        return redirect_to


class HomeView(LoginRequiredMixin, View):
    template_name = 'pages/home.html'

    def get(self, request):
        return render(request, self.template_name,
                      {'TornadoPort': settings.TORNADO_PORT,
                       'SocketPath': settings.SOCKET_PATH,
                       'AuthToken': get_token_for_user(self.request.user, 'auth')})


login = LoginView.as_view()
home = HomeView.as_view()
