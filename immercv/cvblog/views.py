from datetime import datetime, time

from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.utils.text import slugify
from django.views.generic import RedirectView
from markdown_deux import markdown

from immercv.cvgraph.models import Person, get_node_by_id
from immercv.cvgraph.views import CvgraphModelDetailView
from immercv.users.models import User


class CvblogPersonOfFirstUserView(RedirectView):

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        user = User.objects.first()
        if user is None:
            return reverse('about')
        try:
            person = Person.for_user(user)
        except Person.DoesNotExist:
            return reverse('about')
        return reverse('cvblog:person_posts', kwargs=dict(
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
        data['posts'] = posts_for_person(data['person'])
        return data


class PersonPostsFeed(Feed):

    def get_object(self, request, *args, **kwargs):
        id = kwargs['id']
        person = get_node_by_id(Person, int(id))
        return person

    def title(self, obj):
        return 'Experiences, Links, and Notes from {}'.format(obj.name)

    def link(self, obj):
        return reverse('cvblog:person_posts', kwargs=dict(id=obj._id, slug=slugify(obj.name)))

    def feed_url(self, obj):
        return reverse('cvblog:person_posts_feed', kwargs=dict(id=obj._id, slug=slugify(obj.name)))

    def description(self, obj):
        return 'Published using ImmerCV.'

    def items(self, obj):
        return posts_for_person(obj)

    def item_title(self, item):
        return item['title']

    def item_description(self, item):
        return markdown(item['content'])

    def item_link(self, item):
        return item['url']

    def item_pubdate(self, item):
        return datetime.combine(item['publish_date'], time(9, 0, 0))


def date_and_title(post):
    return post['publish_date'], post['title']


def posts_for_person(person):
    # TODO: This is messy... refactor it!
    posts = (
        [dict(title=e.title, publish_date=e.publish_date, content=e.summary + '\n\n' + (e.body or ''),
              url=reverse('cvgraph:experience_detail',
                          kwargs=dict(id=e._id, slug=slugify(e.title))))
         for e in person.published_experiences()]
        +
        [dict(title=l.title, publish_date=l.publish_date, content=l.summary,
              url=l.url)
         for l in person.published_links()]
        +
        [dict(title='A note', publish_date=n.publish_date, content=n.text,
              url=None)
         for n in person.published_notes()]
    )
    posts.sort(key=date_and_title)
    posts.reverse()
    return posts
