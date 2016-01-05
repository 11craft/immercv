from django.core.urlresolvers import reverse
from django.utils.text import slugify
from django.views.generic import RedirectView

from immercv.cvgraph.models import Person
from immercv.cvgraph.views import CvgraphModelDetailView
from immercv.users.models import User


class CvblogPersonOfFirstUserView(RedirectView):

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
        return reverse('cvblog:person_blog', kwargs=dict(
            id=person._id,
            slug=slugify(person.name),
        ))


class PersonPostsView(CvgraphModelDetailView):

    template_dir = 'cvblog'
    context_name = 'person'
    template_suffix = 'posts'
    model = Person

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        person = data['person']
        # TODO: This is messy... refactor it!
        posts = (
            [dict(title=e.title, publish_date=e.publish_date, content=e.summary, url=reverse('cvgraph:experience_detail', kwargs=dict(id=e._id, slug=slugify(e.title))))
             for e in person.published_experiences()]
            +
            [dict(title=l.title, publish_date=l.publish_date, content=l.summary, url='#')
             for l in person.published_links()]
            +
            [dict(title='A note', publish_date=n.publish_date, content=n.text, url='#')
             for n in person.published_notes()]
        )
        date_and_str = lambda p: (p['publish_date'], p['title'])
        posts.sort(key=date_and_str)
        data['posts'] = posts
        return data
