import  subprocess

subprocess.Popen(['pip', 'freeze'], stdout=open('requirements.txt', 'w'))