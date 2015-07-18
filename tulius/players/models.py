from django.utils.translation import ugettext_lazy as _
from django.db import models

class PlayerStar(models.Model):
    """
    Player star show rule
    """
    class Meta:
        verbose_name = _('player star')
        verbose_name_plural = _('player stars')
        ordering = ['games']
        
    games = models.SmallIntegerField(
        blank=False, 
        null=False, 
        verbose_name=_('Games won')
    )

class StarsCache():    
    stars_count = 0
    stars_list = []

    def flush_stars_cache(self):
        stars = PlayerStar.objects.all()
        self.stars_count = len(stars)
        self.stars_list = []
        for star in stars:
            self.stars_list += [star.games]
            
stars = StarsCache()
