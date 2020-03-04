#!/usr/bin/env python

import json
import tempfile
import zipfile
import shutil
import os
import click

@click.command(help="Redact user information from slack export archive in prep for slack-export-viewer.")
@click.option("-z", "--archive", type=click.Path(), required=True,
              default='slack.zip',
              help="Path to your Slack export archive (.zip file or directory)")
def main(archive):
    with zipfile.ZipFile(archive, mode='r') as z:
        with z.open('users.json') as f:
            data = json.load(f)
            for i, val in enumerate(data):
                user = "User %d" % i
                data[i]['profile']['display_name'] = user
                data[i]['profile']['email'] = user

                for p in [24,32,48,72,192,512,1024]:
                    data[i]['profile']['image_%d'%p] = 'https://ui-avatars.com/api/?name=User+%d&size=%d'%(i,p)

        with open('users.json', 'w') as f:
            json.dump(data, f, indent=4)

    remove_from_zip(archive, 'users.json')
    with zipfile.ZipFile(archive, mode='a') as z:
        z.write('users.json')


def remove_from_zip(zipfname, *filenames):
    tempdir = tempfile.mkdtemp()
    try:
        tempname = os.path.join(tempdir, 'new.zip')
        with zipfile.ZipFile(zipfname, 'r') as zipread:
            with zipfile.ZipFile(tempname, 'w') as zipwrite:
                for item in zipread.infolist():
                    if item.filename not in filenames:
                        data = zipread.read(item.filename)
                        zipwrite.writestr(item, data)
        shutil.move(tempname, zipfname)
    finally:
        shutil.rmtree(tempdir)

if __name__ == '__main__':
    main()
