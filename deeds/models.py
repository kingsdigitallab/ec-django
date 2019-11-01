import csv
from datetime import datetime, timedelta

from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext as _
from geonames_place.models import Country, Place
from model_utils.models import TimeStampedModel


class BaseAL(TimeStampedModel):
    title = models.CharField(max_length=128, unique=True)

    class Meta:
        abstract = True
        ordering = ['title']

    def __str__(self):
        return self.title


class DeedType(BaseAL):
    pass


class Data(TimeStampedModel):
    deed_type = models.ForeignKey(DeedType, on_delete=models.CASCADE)
    title = models.CharField(max_length=64, unique=True)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    data = models.FileField(
        upload_to='uploads/data/',
        validators=[FileExtensionValidator(allowed_extensions=['csv'])]
    )

    class Meta:
        verbose_name_plural = 'Data'

    def __str__(self):
        return self.title


class Gender(BaseAL):
    pass


class Person(TimeStampedModel):
    name = models.CharField(max_length=128, blank=True, null=True)
    surname = models.CharField(max_length=128, blank=True, null=True)
    gender = models.ForeignKey(
        Gender, blank=True, null=True, on_delete=models.CASCADE)
    age = models.PositiveSmallIntegerField(blank=True, null=True)
    birth_year = models.PositiveSmallIntegerField(blank=True, null=True)
    origins = models.ManyToManyField(
        Place, through='Origin', through_fields=('person', 'place'))

    class Meta:
        ordering = ['surname', 'name', 'age']

    def __str__(self):
        return '{} {}'.format(self.name, self.surname)

    def get_origins(self):
        origins = ''
        for o in self.origin_from.order_by('order'):
            origins = '{} {} {}'.format(
                origins, '>' if origins else '', o.place)

        return origins.strip()

    @property
    def birthplace(self):
        origin_type = OriginType.objects.get(title='birth')
        origins = self.origin_from.filter(origin_type=origin_type)

        if origins:
            return origins.first()

        return None

    @property
    def domicile(self):
        origin_type = OriginType.objects.get(title='domicile')
        origins = self.origin_from.filter(
            origin_type=origin_type).order_by('order')

        if origins:
            return origins.last()

        return None


class OriginType(BaseAL):
    pass


class Origin(TimeStampedModel):
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name='origin_from')
    place = models.ForeignKey(
        Place, on_delete=models.CASCADE, related_name='origin_of')
    origin_type = models.ForeignKey(OriginType, on_delete=models.CASCADE)
    date = models.DateField(blank=True, null=True)
    is_date_computed = models.BooleanField(
        help_text=_('Wether the date was computed using the person birth date '
                    'and the date of the deed')
    )
    order = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return '{}: {}'.format(self.origin_type, self.place)


class Profession(BaseAL):
    pass


class Role(BaseAL):
    pass


class Source(TimeStampedModel):
    data = models.ForeignKey(Data, on_delete=models.CASCADE)
    classmark = models.CharField(max_length=32)
    microfilm = models.CharField(max_length=32)

    class Meta:
        unique_together = ['data', 'classmark', 'microfilm']

    def __str__(self):
        return '{}: {}'.format(self.classmark, self.microfilm)


class Deed(TimeStampedModel):
    deed_type = models.ForeignKey(DeedType, on_delete=models.CASCADE)
    n = models.PositiveSmallIntegerField(blank=True, null=True)
    date = models.DateField(help_text=_('Date of the deed record'))
    place = models.ForeignKey(
        Place, on_delete=models.CASCADE,
        related_name='deeds', help_text=_('Place of the deed record'))
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    parties = models.ManyToManyField(
        Person, through='Party', through_fields=('deed', 'person'))
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['n', 'date', 'place']

    def __str__(self):
        return '{}: {} - {}; {}'.format(
            self.deed_type, self.n, self.date, self.place)


class Party(TimeStampedModel):
    deed = models.ForeignKey(Deed, on_delete=models.CASCADE)
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name="party_to")
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    profession = models.ForeignKey(
        Profession, blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Parties'


def import_data(data):
    assert data is not None

    if data.deed_type.title == 'birth':
        import_birth(data)

    if data.deed_type.title == 'marriage':
        pass

    if data.deed_type.title == 'death':
        pass


def import_birth(data):
    with open(data.data.path) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            import_birth_record(data, row)


def import_birth_record(data, record):
    source = import_source(data, record)

    deed_date = get_deed_date(record)

    deed_type = DeedType.objects.get(title='birth')
    deed = import_deed(data, deed_type, deed_date, source, record)

    gender, _ = Gender.objects.get_or_create(title='m')
    father = import_person('Father', record, gender, deed_date)
    role = Role.objects.get(title='father')
    add_party(deed, father, role, 'Father', record)

    gender, _ = Gender.objects.get_or_create(title='f')
    mother = import_person('Mother', record, gender, deed_date)
    role = Role.objects.get(title='mother')
    add_party(deed, mother, role, 'Mother', record)


def import_source(data, record):
    assert record is not None

    source, _ = Source.objects.get_or_create(
        data=data,
        classmark=record['Classmark (Etat civil, Volumes)'].strip(),
        microfilm=record['Microfilm classmark'].strip()
    )

    return source


def get_deed_date(record):
    return datetime.strptime(record['Deed date'].strip(), '%d/%m/%Y').date()


def import_deed(data, deed_type, deed_date, source, record):
    n = record['Deed number'].strip()
    if n == '/':
        n = 0

    try:
        n = int(n)
    except ValueError:
        n = 0

    notes = 'Legitimate birth: {}'.format(record['Legitimate birth'].strip())

    deed, _ = Deed.objects.get_or_create(
        deed_type=deed_type, n=n, date=deed_date, place=data.place,
        source=source, notes=notes
    )

    return deed


def import_person(label, record, gender, deed_date):
    name = record['{}\'s first name'.format(label)].strip()
    surname = record['{}\'s surname'.format(label)].strip()
    age = record['{}\'s age'.format(label)].strip()
    birth_date = None
    birth_year = None

    if age:
        birth_date = get_date_of_birth(
            record['Deed date'].strip(), int(age))
        birth_year = birth_date.year
    else:
        age = None

    person, _ = Person.objects.get_or_create(
        name=name, surname=surname, gender=gender, age=age,
        birth_year=birth_year
    )

    add_origins(person, label, deed_date, birth_date, record)

    return person


def get_date_of_birth(deed_date, age):
    assert deed_date is not None
    assert age is not None

    d = datetime.strptime(deed_date, '%d/%m/%Y').date()
    delta = age * timedelta(days=365)

    return (d - delta)


def add_origins(person, label, deed_date, birth_date, record):
    address = record['{}\'s domicile'.format(label)].strip()
    add_origin(person, address, 'EG', 'domicile', date=deed_date, order=5)

    is_date_computed = False

    # estimates the date of birth
    if not birth_date:
        birth_date = get_date_of_birth(
            '{}/{}/{}'.format(deed_date.day, deed_date.month, deed_date.year),
            25)
        is_date_computed = True

    address = '{} {}'.format(
        record['{}\'s birthplace (region or département)'.format(
            label)].strip(),
        record['{}\'s birthplace (locality)'.format(label)].strip())
    address = address.strip()
    add_origin(person, address, 'FR', 'birth',
               date=birth_date, is_date_computed=is_date_computed, order=1)

    # estimates the date of the previous domicile
    pdd = None
    if deed_date and birth_date:
        pdd = birth_date + (deed_date - birth_date) / 2
        is_date_computed = True

    address = '{} {}'.format(
        record['{}\'s previous domicile (region or département)'.format(
            label)].strip(),
        record['{}\'s previous domicile (locality)'.format(label)].strip())
    address = address.strip()
    add_origin(person, address, 'FR', 'domicile',
               date=pdd, is_date_computed=is_date_computed, order=3)


def add_origin(person, address, country_code, origin_type,
               date=None, is_date_computed=False, order=0):
    if address:
        place = get_place(address, country_code)

        if place:
            origin_type = OriginType.objects.get(title=origin_type)
            Origin.objects.get_or_create(
                person=person, place=place, origin_type=origin_type,
                date=date, is_date_computed=is_date_computed, order=order
            )


def get_place(address, country_code):
    return Place.get_or_create_from_geonames(
        address=address, country_code=country_code)


def add_party(deed, person, role, label, record):
    profession = None

    title = record['{}\'s profession'.format(label)].strip()
    if title:
        profession, _ = Profession.objects.get_or_create(title=title)

    Party.objects.get_or_create(
        deed=deed, person=person, role=role, profession=profession)
