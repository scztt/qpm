import git, local, url, quarkname
__all__ = ['git', 'url', 'quarkname', 'local']

def make_endpoint(url_string):
	if git.GitEndpoint.validate(url_string):
		return git.GitEndpoint(url_string)
	elif url.UrlEndpoint.validate(url_string):
		return url.UrlEndpoint(url_string)
	elif local.LocalEndpoint.validate(url_string):
		return local.LocalEndpoint(url_string)
	else:
		return None

