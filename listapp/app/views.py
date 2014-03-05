# Create your views here.
from braces.views import LoginRequiredMixin
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic import TemplateView
import requests


grade_naming = {
    'k': 'K',
    'first': '1',
    'second': '2',
    'third': '3',
    'forth': '4',
    'fifth': '5',
    'sixth': '6',
    'seventh': '7',
    'eighth': '8',
    'ninth': '9',
    'tenth': '10',
    'eleventh': '11',
    'twelfth': '12'
}
grade_naming_inv = dict(zip(grade_naming.values(), grade_naming.keys()))

class IndexView(TemplateView):
    template_name = 'index.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(reverse('protected'))
        return super(IndexView, self).dispatch(request, *args, **kwargs)

class ProtectedView(LoginRequiredMixin, TemplateView):
    template_name = 'protected.html'

    def get_context_data(self, **kwargs):
        ctx = super(ProtectedView, self).get_context_data(**kwargs)
        headers = {'content-type': 'application/json'}
        user = self.request.user
        organization = user.organization
        api_res = None
        res = requests.get('http://admin.logintex.me/api/districts/{0}/'.format(organization), headers=headers)
        auth = False
        other_res = []
        sites = map(lambda x: x['domain'], Site.objects.values('domain'))
        if res.status_code == 200:
            api_res = res.json()
            for r in api_res['resources']:
                if r[grade_naming_inv[user.grade]]:
                    if (r['teacher'] and user.role.lower() == 'teacher') or (r['student'] and user.role.lower() == 'student'):
                        other_res.append(dict(name=r['name'], url=r['url']))
                elif user.is_superuser:
                    other_res.append(dict(name=r['name'], url=r['url']))


            ctx['app_auth'] = auth
            ctx['api'] = api_res
            ctx['district_name'] = api_res['district_name']
            ctx['resources'] = api_res['resources']
            ctx['other_resources'] = other_res
            ctx['user'] = user
        return ctx