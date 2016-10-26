import os
import requests

from django.core.management.base import BaseCommand

from readthedocs.projects.models import Project
from readthedocs.projects.constants import GITHUB_REGEXS, PROGRAMMING_LANGUAGES

PL_DICT = {}

for slug, name in PROGRAMMING_LANGUAGES:
    PL_DICT[name] = slug


class Command(BaseCommand):
    def handle(self, *args, **options):
        token = os.environ.get('GITHUB_AUTH_TOKEN')
        if not token:
            print 'Invalid GitHub token, exiting'

        for project in Project.objects.filter(programming_language__in=['', 'words']):
            user = repo = ''
            repo_url = project.repo
            for regex in GITHUB_REGEXS:
                match = regex.search(repo_url)
                if match:
                    user, repo = match.groups()
                    break

            if not user:
                print 'No GitHub repo for %s' % repo_url
                continue

            headers = {'Authorization': 'token {token}'.format(token=token)}
            url = 'https://api.github.com/repos/{user}/{repo}/languages'.format(
                user=user,
                repo=repo,
            )

            resp = requests.get(url, headers=headers)
            languages = resp.json()
            sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
            print 'Sorted langs: %s ' % sorted_langs
            top_lang = sorted_langs[0][0]
            if top_lang in PL_DICT:
                slug = PL_DICT[top_lang]
                print 'Setting %s to %s' % (repo_url, slug)
                project.programming_language = slug
                project.save()
            else:
                print 'Language unknown: %s' % top_lang
