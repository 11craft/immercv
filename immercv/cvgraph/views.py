from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils.text import slugify
from django.views.generic import RedirectView, TemplateView

from immercv.cvgraph.commands import apply_command
from immercv.cvgraph.models import get_node_by_id, Person, Project, Role, \
    Company, Topic, Experience, CV


class CvgraphMeView(RedirectView):

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        try:
            person = Person.for_user(self.request.user)
        except Person.DoesNotExist:
            person = Person.create_for_user(self.request.user)
        return reverse('cvgraph:person_detail', kwargs=dict(
            id=person._id,
            slug=slugify(person.name),
        ))


class CvgraphModelDetailView(TemplateView):

    model = None
    context_name = None

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        node = get_node_by_id(self.model, int(self.kwargs['id']))
        data[self.context_name] = node
        return data

    def get_template_names(self):
        return ['cvgraph/{}_detail.html'.format(self.context_name)]


class CvgraphCompanyDetailView(CvgraphModelDetailView):

    model = Company
    context_name = 'company'


class CvgraphCVDetailView(CvgraphModelDetailView):

    model = CV
    context_name = 'cv'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        spec = data['cv'].spec
        return data

    def get_template_names(self):
        default = super().get_template_names()
        if 'print' in self.request.GET:
            return 'cvgraph/cv_detail_print.html'
        else:
            return default


class CvgraphExperienceDetailView(CvgraphModelDetailView):

    model = Experience
    context_name = 'experience'


class CvgraphPersonDetailView(CvgraphModelDetailView):

    model = Person
    context_name = 'person'


class CvgraphProjectDetailView(CvgraphModelDetailView):

    model = Project
    context_name = 'project'


class CvgraphRoleDetailView(CvgraphModelDetailView):

    model = Role
    context_name = 'role'


class CvgraphTopicDetailView(CvgraphModelDetailView):

    model = Topic
    context_name = 'topic'


class CvgraphChangeView(RedirectView):

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        if self.request.method != 'POST':
            raise Http404()
        else:
            params = self.request.POST.copy()
            del params['csrfmiddlewaretoken']
            apply_command(self.request, params)
            return self.request.META['HTTP_REFERER']
