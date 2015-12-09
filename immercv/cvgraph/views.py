from django.core.urlresolvers import reverse
from django.utils.text import slugify
from django.views.generic import RedirectView, TemplateView
from neomodel import db

from immercv.cvgraph.models import get_by_id, Person


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
