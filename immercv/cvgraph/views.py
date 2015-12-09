from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils.text import slugify
from django.views.generic import RedirectView, TemplateView

from immercv.cvgraph.commands import apply_command
from immercv.cvgraph.models import get_by_id, Person, Project


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


class CvgraphPersonDetailView(TemplateView):

    template_name = 'cvgraph/person_detail.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        person = get_by_id(Person, int(self.kwargs['id']))
        data.update(person=person)
        return data


class CvgraphProjectDetailView(TemplateView):

    template_name = 'cvgraph/project_detail.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        project = get_by_id(Project, int(self.kwargs['id']))
        data.update(project=project)
        return data


class CvgraphChangeView(RedirectView):

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        if self.request.method != 'POST':
            raise Http404()
        else:
            params = self.request.POST.copy()
            apply_command(self.request, params)
            return self.request.META['HTTP_REFERER']
