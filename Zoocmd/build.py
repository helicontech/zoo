import shutil
import os
import subprocess
import sys
import argparse
import shutil

from distutils import dir_util



def run():
    """
    create a new instance of application
    """
    parser = argparse.ArgumentParser(description='Build script')

    parser.add_argument('--build-dir', dest='build_dir', default=os.path.join(os.path.dirname(__file__), 'build'), help='Directory where to put build files.')
    parser.add_argument('--clean', action='store_true', dest='clean', default=False,
                         help='Wipe out build dir before build.')

    args = parser.parse_args()

    build_dir = os.path.abspath(args.build_dir)
    src_dir = os.path.abspath(os.path.dirname(__file__))
    print("Building distribution in: {0}\n".format(build_dir))
    if args.clean:
        print("Clean build.\n")
        if os.path.exists(build_dir):
            dir_util.remove_tree(build_dir)

    if not os.path.isfile(os.path.join(build_dir, 'Scripts', 'python.exe')):
        virtualenv_path = os.path.join(os.path.dirname(sys.executable), r'Scripts\virtualenv.exe')
        subprocess.check_call([virtualenv_path, '{0}'.format(build_dir), '--clear'])

    requirements_txt = os.path.join(src_dir, 'etc', 'requirements.txt')
    pip = os.path.join(build_dir, 'Scripts', 'pip3.4.exe')
    subprocess.check_call([pip, 'install', '-r', requirements_txt])

    python = os.path.join(build_dir, 'Scripts', 'python.exe')
    subprocess.check_call([python, '-m', 'easy_install', "pyyaml"])

    if args.clean:
        easy_install = os.path.join(build_dir, 'Scripts', 'easy_install.exe')
        subprocess.check_call([easy_install, os.path.join(src_dir, 'redist', "pywin32-219.win32-py3.4.exe")])

    print('Starting cxFreeze to build executable\n')
    # TODO: do not use hardcoded strings - they must be parameters
    subprocess.check_call([python, os.path.join(src_dir, 'build_exe.py'), "build", "-b{0}".format(build_dir)])

    print('Copying additional files\n')
    executable_dir = os.path.join(build_dir, 'exe.win32-3.4')
    shutil.copy(os.path.join(src_dir, '7za.exe'), executable_dir)
    etc_dir = os.path.join(executable_dir, 'etc')
    try:
        os.mkdir(etc_dir)
    except:
        pass
    shutil.copy(os.path.join(src_dir, 'etc', 'logging.conf'), os.path.join(executable_dir, 'etc'))

    print("Creating SFX archive")
    # This archive stores complete 'zoocmd' package and is used by feed compiler
    subprocess.check_call([ os.path.join(src_dir, '7za.exe'), 'a', os.path.join(build_dir, 'zoocmd.exe'), os.path.join(executable_dir, '*'), '-sfx'])



if __name__ == '__main__':
    run()

