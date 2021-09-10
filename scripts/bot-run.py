#!/usr/bin/env python3
"""
Script for running a simple bot.
"""
import json
import subprocess
from urllib.parse import urljoin
from urllib.request import Request, urlopen


class API:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token

    def request(self, url, method='GET', data=None):
        url = urljoin(self.base_url, url)
        if data:
            data = json.dumps(data).encode('utf-8')
        else:
            data = None

        headers = {
                "Content-type": "application/json",
        }
        if self.token:
            headers['Authorization'] = 'Token ' + self.token

        req = Request(url, data=data, method=method, headers=headers)
        try:
            resp = urlopen(req)
        except Exception as e:
            print(e.reason)
            print(e.read().decode('utf-8'))
            raise
        else:
            return json.load(resp)

    def my_chunks(self):
        me = self.request('me/')['id']
        return self.request('documents/chunks/?user={}'.format(me))


def process_chunk(chunk, api, executable):
    print(chunk['id'])
    head = chunk['head']
    text = api.request(head)['text']
    text = text.encode('utf-8')

    try:
        p = subprocess.run(
            [executable],
            input=text,
            capture_output=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print('Ditching the update. Bot exited with error code {} and output:'.format(e.returncode))
        print(e.stderr.decode('utf-8'))
        return
    result_text = p.stdout.decode('utf-8')
    stderr_text = p.stderr.decode('utf-8')
    api.request(chunk['revisions'], 'POST', {
        "parent": head,
        "description": stderr_text or 'Automatic update.',
        "text": result_text
    })
    # Remove the user assignment.
    api.request(chunk['id'], 'PUT', {
        "user": None
    })


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Runs a bot for Redakcja. '
        'You need to provide an executable which will take current revision '
        'of text as stdin, and output the new version on stdout. '
        'Any output given on stderr will be used as revision description. '
        'If bot exits with non-zero return code, the update will be ditched.'
    )
    parser.add_argument(
        'token', metavar='TOKEN', help='A Redakcja API token.'
    )
    parser.add_argument(
        'executable', metavar='EXECUTABLE', help='An executable to run as bot.'
    )
    parser.add_argument(
        '--api', metavar='API', help='A base URL for the API.',
        default='https://redakcja.wolnelektury.pl/api/',
    )
    args = parser.parse_args()


    api = API(args.api, args.token)

    chunks = api.my_chunks()
    if chunks:
        for chunk in api.my_chunks():
            process_chunk(chunk, api, args.executable)
    else:
        print('No assigned chunks found.')
