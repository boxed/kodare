from django.contrib.syndication.views import Feed
from kodare.blog.models import *

class BlogFeed(Feed):
    title = "Kodare"
    link = "/blog/"
    description = "Kodare Blog"

    def items(self):
        return Entry.objects.all()[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, entry):
        #'<enclosure url="http://www.youtube.com/v/q2CA9PAIMRg&hl=en_US&fs=1&" type="application/x-shockwave-flash" length="100" />'
        return entry.content