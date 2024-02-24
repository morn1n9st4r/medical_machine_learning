import random
import time
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from main.models import PatientBaseRecord
import datetime

class Command(BaseCommand):
    help = 'Create random users and their patient records'

    #def add_arguments(self, parser):
    #    parser.add_argument('username', type=str, help='The username of the new user')
    #    parser.add_argument('password', type=str, help='The password of the new user')
    #    parser.add_argument('email', type=str, help='The email of the new user')

    def handle(self, *args, **kwargs):
        num_of_users = 49
        for i in range(num_of_users):
            username = 'patient_' + str(random.randint(1000, 9999))
            password = 'Qwerty12345@'
            email = username + '@gmail.com'
            user = User.objects.create_user(username=username, password=password, email=email)
            time.sleep(2)
            PatientBaseRecord.objects.create(
                id=user.id,
                patient = get_object_or_404(User, pk=user.id),
                first_name='fill in',
                last_name='fill in',
                date_of_birth=datetime.datetime.now(),
                gender='O',
                contact_number='fill in',
                emergency_contact_number='not set',
                emergency_contact_first_name='not set',
                emergency_contact_last_name='not set',
                emergency_contact_relationship='not set',
                allergies='None',
                chronic_diseases='None',
                primary_doctor='None',
                notes='',
            )
            print('Successfully created user "%s" and their patient record' % username)

        self.stdout.write(self.style.SUCCESS('Successfully created users "%s" and their patient record' % num_of_users))