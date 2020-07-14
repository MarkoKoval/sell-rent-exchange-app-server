from django.test import TestCase

# Create your tests here.
import  subprocess

subprocess.Popen(['pip', 'freeze'], stdout=open('requirements.txt', 'w'))