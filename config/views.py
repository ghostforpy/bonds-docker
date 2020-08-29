from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from portfolio.utils import get_portfolios_by_user,\
    get_followed_portfolios_by_user
from moex.utils import get_securities_in_portfolios_by_user,\
    get_followed_securities_by_user


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = "pages/home.html"
    login_url = '/about'
    redirect_field_name = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['portfolios'] = get_portfolios_by_user(user)
        context['portfolio_followed'] = get_followed_portfolios_by_user(user)
        context['securities_in_portfolios'] =\
            get_securities_in_portfolios_by_user(user)
        context['security_followed'] = get_followed_securities_by_user(user)
        return context
