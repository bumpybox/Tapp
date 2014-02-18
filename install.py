import os
import sys


def query_yes_no(question, default="yes"):

    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """

    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")


def setEnv(var, val):

    os.system("SETX {0} {1} /M".format(var, val))


def installMaya():

    #adding Tapp variables
    val = os.path.dirname(os.path.dirname(__file__))
    val += ';' + os.path.join(os.path.dirname(__file__), 'System')

    if 'PYTHONPATH' in os.environ:
        if val in os.environ['PYTHONPATH']:
            print 'Tapp Environment Variables already set!'
        else:
            val += ';' + os.environ['PYTHONPATH']

            setEnv('PYTHONPATH', val)
    else:
        setEnv('PYTHONPATH', val)


def installNuke():

    #adding Tapp variables
    val = os.path.dirname(os.path.dirname(__file__))
    val += ';' + os.path.join(os.path.dirname(__file__), 'System')

    if 'NUKE_PATH' in os.environ:
        if val in os.environ['NUKE_PATH']:
            print 'Tapp Environment Variables already set!'
        else:
            val += ';' + os.environ['NUKE_PATH']

            setEnv('NUKE_PATH', val)
    else:
        setEnv('NUKE_PATH', val)

if __name__ == '__main__':

    #maya install
    if query_yes_no('Install Tapp for Maya?'):

        installMaya()

    #nuke install
    if query_yes_no('Install Tapp for Nuke?'):

        installNuke()
