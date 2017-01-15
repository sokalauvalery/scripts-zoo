import os
import shutil
import warnings

TMP_DIR = os.path.join(os.getcwd(), 'tmp')
FILE_NAME_BACKLIGHT = '==>'


def before_all(context):
    warnings.warn('Tests are not supposed to run in parallel!')
    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)
    os.mkdir(TMP_DIR)


def after_all(context):
    shutil.rmtree(TMP_DIR)
    pass


def before_feature(context, feature):
    os.mkdir(os.path.join(TMP_DIR, os.path.basename(feature.filename)))