from urllib.parse import urlsplit

from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils.text import slugify
from django.views.generic import RedirectView, TemplateView

from immercv.cvgraph.commands import apply_command
from immercv.cvgraph.models import get_node_by_id, Person, Project, Role, \
    Company, Topic, Experience, CV
from immercv.users.models import User

DECODE_NODE_MAP = {
    'experience': Experience,
    'project': Project,
}


def decode_node_url(url):
    node_type, node_id = urlsplit(url).path.split('/')[1:3]
    node_id = int(node_id)
    node_class = DECODE_NODE_MAP[node_type]
    node = get_node_by_id(node_class, node_id)
    return node, node_type


class CvgraphPersonOfFirstUserView(RedirectView):

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        user = User.objects.first()
        print(user)
        if user is None:
            return reverse('about')
        try:
            person = Person.for_user(user)
        except Person.DoesNotExist:
            return reverse('about')
        return reverse('cvgraph:person_detail', kwargs=dict(
            id=person._id,
            slug=slugify(person.name),
        ))


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
        data['cv_items'] = items = []
        for line in (spec or '').splitlines():
            if line == '':
                continue
            template_name, value = line.split(': ', 1)
            template = 'cvgraph/cv/{}/container.html'.format(template_name)
            if value.startswith('http://') or value.startswith('https://'):
                node, node_type = decode_node_url(value)
                text = None
            else:
                node, node_type = None, 'text'
                text = value
            inner_template = 'cvgraph/cv/{}/{}.html'.format(template_name, node_type)
            items.append({
                'template': template,
                'inner_template': inner_template,
                'node': node,
                'text': text,
            })
        return data


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
        if self.request.method != 'POST' or not self.request.user.is_authenticated():
            raise Http404()
        else:
            params = self.request.POST.copy()
            del params['csrfmiddlewaretoken']
            apply_command(self.request, params)
            return self.request.META['HTTP_REFERER']
