from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse
from django.utils.text import slugify

from immercv.cvgraph.models import CV


class CvsSitemap(Sitemap):

    changefreq = 'weekly'
    priority = 0.5

    def items(self):
        return CV.nodes.all()

    def location(self, obj):
        return reverse('cvgraph:cv_detail', kwargs=dict(
            id=obj._id,
            slug=slugify(obj.name),
        ))
