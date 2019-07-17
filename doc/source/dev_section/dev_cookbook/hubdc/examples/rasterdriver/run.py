import os
filenames = list()
for root, dirs, files in os.walk(os.path.abspath("."), topdown=False):
   for name in files:
       if name == 'run.py':
           continue
       if name.endswith('.py'):
           filenames.append(os.path.join(root, name))
for i, filename in enumerate(filenames):

    print(i+1, filename)
    os.chdir(os.path.dirname(filename))
    os.system('python {}'.format(filename))
