from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils.text import slugify
from django.views.generic import RedirectView, TemplateView

from immercv.cvgraph.commands import apply_command
from immercv.cvgraph.models import get_node_by_id, Person, Project, Role


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


class CvgraphPersonDetailView(CvgraphModelDetailView):

    model = Person
    context_name = 'person'


class CvgraphProjectDetailView(CvgraphModelDetailView):

    model = Project
    context_name = 'project'


class CvgraphRoleDetailView(CvgraphModelDetailView):

    model = Role
    context_name = 'role'


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
