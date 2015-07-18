from django.test import TestCase
from .discovery import get_available_themes, get_current_theme
from django.conf import settings
import os

class TestAvailableThemesDicovery(TestCase):
    """
    Tests available themes discovery
    """
    def test_filesystem_discovery(self):
        """
        Tests that given folders returns estimated available themes result
        """
        #1. create sample directory structure
        sample_dir = settings.MEDIA_ROOT + 'test_filesystem_discovery_themes_dir/'
        # check that sample dir doesn't exist yet
        self.assertFalse(os.path.exists(sample_dir))
        # create dir
        os.mkdir(sample_dir)
        # check it exists now
        self.assertTrue(os.path.exists(sample_dir))
        # create some fake theme dirs
        theme_names = ['theme_1', 'theme_2', 'theme_3']
        theme_names.sort() #just in case
        theme_paths = [sample_dir + name for name in theme_names]
        for path in theme_paths:
            os.mkdir(path)
            self.assertTrue(os.path.exists(path))
        #2. check discovery result
        settings.THEMING_ROOT = sample_dir
        self.assertEqual(get_available_themes(), theme_names)
        #3. clean up sample directory structure
        #remove sample dir and subdirs
        for path in theme_paths:
            os.rmdir(path)
            self.assertFalse(os.path.exists(path))
        os.rmdir(sample_dir)
        #check it doesn't exist now
        self.assertFalse(os.path.exists(sample_dir))
