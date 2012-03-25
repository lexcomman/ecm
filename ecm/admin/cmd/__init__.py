# Copyright (c) 2010-2012 Robin Jarry
#
# This file is part of EVE Corporation Management.
#
# EVE Corporation Management is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# EVE Corporation Management is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# EVE Corporation Management. If not, see <http://www.gnu.org/licenses/>.


from __future__ import with_statement

__date__ = '2012 3 23'
__author__ = 'diabeteman'

import os
import tempfile
import urllib2
import zipfile
import shutil
from os import path

from ecm.admin.util import run_python_cmd, get_logger


#-------------------------------------------------------------------------------
def collect_static_files(instance_dir, options):
    log = get_logger()
    log.info("Gathering static files...")
    switches = '--noinput'
    if os.name != 'nt' and options.symlink_files:
        switches += ' --link'
    run_python_cmd('manage.py collectstatic ' + switches, instance_dir)

#-------------------------------------------------------------------------------
def download_eve_db(instance_dir, eve_db_dir, eve_db_url, eve_zip_archive):
    log = get_logger()
    try:
        tempdir = None
        if eve_zip_archive is None:
            tempdir = tempfile.mkdtemp()
            eve_zip_archive = os.path.join(tempdir, 'EVE.db.zip')
            log.info('Downloading EVE database from %s to %s...', eve_db_url, eve_zip_archive)
            req = urllib2.urlopen(eve_db_url)
            with open(eve_zip_archive, 'wb') as fp:
                shutil.copyfileobj(req, fp)
            req.close()
            log.info('Download complete.')

        if not path.exists(eve_db_dir):
            os.makedirs(eve_db_dir)

        log.info('Expanding %s to %s...', eve_zip_archive, eve_db_dir)
        zip_file_desc = zipfile.ZipFile(eve_zip_archive, 'r')
        for info in zip_file_desc.infolist():
            fname = info.filename
            data = zip_file_desc.read(fname)
            filename = os.path.join(eve_db_dir, fname)
            file_out = open(filename, 'wb')
            file_out.write(data)
            file_out.flush()
            file_out.close()
        zip_file_desc.close()
        log.info('Expansion complete.')
    finally:
        if tempdir is not None:
            log.info('Removing temp files...')
            shutil.rmtree(tempdir)
            log.info('done')