from django.db.models.fields.files import FileField, FieldFile, FileDescriptor
from django.core.files.base import File, ContentFile
from django.utils import six
from django.db import models
from .storage import SimpleFileStorage
import StringIO
import os
from PIL import Image

class SimpleFieldFile(FieldFile):
    def __init__(self, instance, field, ext):
        self.ext = ext
        self.field = field
        name = self.generate_name(instance)
        super(SimpleFieldFile, self).__init__(instance, field, name)
        self.delayed_delete = False
        
    def _require_file(self):
        if (not self.name) and (not getattr(self, '_file', False)):
            raise ValueError("The '%s' attribute has no file associated with it." % self.field.name)
        
    def generate_name(self, instance):
        return self.field.generate_filename_from_ext(instance, self.ext) if self.ext else None
    
    def _save(self, content):
        name = self.generate_name(self.instance)
        if self.name:
            self.storage.delete(self.name)
        if name:
            self.name = self.storage.save(name, content)
            self._size = content.size
            self._committed = True
        else:
            self.file = content
            self._committed = False

    def save(self, name, content, save=True):
        self.ext = os.path.splitext(name)[1].replace('.', '').lower()
        setattr(self.instance, self.field.name, self.ext)
        self._save(content)
        if save:
            self.instance.save()
            
    save.alters_data = True
    
    def mark_to_delete(self):
        self.ext = None
        self.delayed_delete = True
        
    def post_save(self):
        if (not self._committed) or (self.delayed_delete):
            if self.delayed_delete:
                if self.name:
                    self.delete(save=False)
            else:
                self._save(self._file)
                self.close()
            
class SimpleFileDescriptor(FileDescriptor):
    def __get__(self, instance=None, owner=None):
        if instance is None:
            raise AttributeError(
                "The '%s' attribute can only be accessed from %s instances."
                % (self.field.name, owner.__name__))
        file = instance.__dict__[self.field.name]
        if isinstance(file, six.string_types) or file is None:
            attr = self.field.attr_class(instance, self.field, file)
            instance.__dict__[self.field.name] = attr
        elif isinstance(file, SimpleFieldFile) and not hasattr(file, 'field'):
            file.instance = instance
            file.field = self.field
            file.storage = self.field.storage
        return instance.__dict__[self.field.name]
    def __set__(self, instance, value):
        if isinstance(value, SimpleFieldFile) or (isinstance(value, six.string_types) and value):
            instance.__dict__[self.field.name] = value
        else:
            if not value:
                if self.field.name in instance.__dict__:
                    file_obj = self.__get__(instance)
                    file_obj.mark_to_delete()
                else: 
                    file_obj = None
            elif isinstance(value, File) and not isinstance(value, SimpleFieldFile):
                file_obj = self.__get__(instance)
                file_obj.file = value
                file_obj._committed = False
                file_obj.delayed_delete = False
                file_obj.ext = os.path.splitext(value.name)[1].replace('.', '').lower()
            instance.__dict__[self.field.name] = file_obj
        
class SimpleFileField(FileField):
    attr_class = SimpleFieldFile
    descriptor_class = SimpleFileDescriptor
    
    def __init__(self, storage=None, **kwargs):
        if not storage:
            storage = SimpleFileStorage()
        super(SimpleFileField, self).__init__(storage=storage, **kwargs)
    
    def get_prep_value(self, value):
        "Returns field's value prepared for saving into a database."
        # Need to convert File objects provided via a form to unicode for database insertion
        if value is None:
            return None
        return value.ext or None
    
    def generate_name_from_ext(self, instance, ext):
        if not instance.pk:
            return None
        return "%s.%s" % (instance.pk, ext) if ext else str(instance.pk)
    
    def get_filename(self, instance, filename):
        ext = os.path.splitext(filename)[1].replace('.', '') if filename else None
        return self.generate_name_from_ext(instance, ext)
    
    def generate_filename(self, instance, filename):
        return os.path.join(self.get_directory_name(), self.get_filename(instance, filename))
    
    def generate_filename_from_ext(self, instance, ext):
        name = self.generate_name_from_ext(instance, ext)
        return os.path.join(self.get_directory_name(), name) if name else None

    def post_save(self, instance):
        file_obj = getattr(instance, self.name, None)
        if not file_obj is None:
            file_obj.post_save()

class SimplifiedFileModel(models.Model):
    class Meta:
        abstract = True
        
    def save(self, *args, **kwargs):
        super(SimplifiedFileModel, self).save(*args, **kwargs)
        for field in self._meta.fields:
            if isinstance(field, SimpleFileField):
                field.post_save(self)

class VersionedFieldSubImage(SimpleFieldFile):
    def generate_name(self, instance):
        return self.field.generate_filename_for_version(instance, self.ext, self.version_name)
    
    def __init__(self, instance, field, ext, version_name, version_conv):
        self.version_name = version_name
        self.version_conv = version_conv
        super(VersionedFieldSubImage, self).__init__(instance, field, ext)
        
    def save(self, ext, image):
        self.ext = ext
        if callable(self.version_conv):
            image = self.version_conv(image)
        else:
            image.thumbnail(self.version_conv, Image.ANTIALIAS)
        imageformat = image.format
        image_content = StringIO.StringIO()
        image.save(image_content, format=imageformat)
        content = ContentFile(image_content.getvalue())
        self._save(content)
    save.alters_data = True
    
class VersionedFieldImage(SimpleFieldFile):
    def __init__(self, instance, field, ext):
        super(VersionedFieldImage, self).__init__(instance, field, ext)
        self.versions = field.versions
        self.files = {}
        for version_name in self.versions.iterkeys():
            version_file = VersionedFieldSubImage(instance, field, ext, version_name, self.versions[version_name])
            self.files[version_name] = version_file
    
    def __getitem__(self, key):
        return self.files[key]
        
    def _save(self, content):
        super(VersionedFieldImage, self)._save(content)
        if self._committed:
            for version in self.files.itervalues():
                file_obj = open(self.path, 'rb')
                try:
                    image = Image.open(file_obj)
                    version.save(self.ext, image)
                finally:
                    file_obj.close()

    def save(self, name, content, save=True):
        image = Image.open(content)
        self.ext = image.format.lower()
        setattr(self.instance, self.field.name, self.ext)
        self._save(content)
        if save:
            self.instance.save()

    def delete(self, save=True):
        for version in self.files.itervalues():
            version.delete(save=False)
        super(VersionedFieldImage, self).delete(save=save)

    def mark_to_delete(self):
        super(VersionedFieldImage, self).mark_to_delete()
        for version in self.files.itervalues():
            version.mark_to_delete()
        
    def post_save(self):
        super(VersionedFieldImage, self).post_save()
        for version in self.files.itervalues():
            version.post_save()
            
class VersionedImageField(SimpleFileField):
    attr_class = VersionedFieldImage

    def __init__(self, versions={}, **kwargs):
        self.versions = versions
        super(VersionedImageField, self).__init__(**kwargs)
        
    def generate_name_for_version(self, instance, ext, version):
        if not instance.pk:
            return None
        return "%s_%s.%s" % (instance.pk, version, ext) if ext else str(instance.pk) + '_' + version
    
    def generate_filename_for_version(self, instance, ext, version):
        name = self.generate_name_for_version(instance, ext, version)
        return os.path.join(self.get_directory_name(), name) if name else None
    
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^djfw\.uploader\.fields\.SimpleFileField"])
    add_introspection_rules([], ["^djfw\.uploader\.fields\.VersionedImageField"])
except:
    pass