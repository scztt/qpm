import qpm
import platform, os, os.path, re
from semantic_version import Version, Spec
from glob import glob

def get_default_locations():
    if platform.system() == 'Darwin':
        return list([
            '/Applications',
            '/usr/local/SuperCollider',
            '/Library/Application Support/SuperCollider/QuarkStore/IDEs',
            '~/Library/Application Support/SuperCollider/QuarkStore/IDEs',
            '/Volumes/Super*/',            
        ])

def find_ide(version='>0.0.0', hint=None, interactive=True):
    print 'Searching for SC versions matching %s...' % version
    versions = find_sc_versions(hint=hint)
    try:
        version_spec = Spec(version)
    except ValueError:
        version_spec = Spec('==' + version)

    matches = list()

    for v in versions:
        semver = versions[v]
        if version_spec.match(semver):
            matches.append(v)

    if matches:
        best_match_ver = version_spec.select(map(lambda m: versions[m], matches))
        for m in matches:
            if best_match_ver is versions[m]:
                best_match = m
                break

        if interactive and len(matches) > 1:
            best_num = -1
            for i, match in enumerate(matches):
                print "[%s] %s (%s)" % (i, match, versions[match])
                if match == best_match: best_num = i

            selection = None
            while not(selection):
                selection = raw_input("Which ide do you want to use for this project? [default: %s]: " % best_num)
                if not(selection): selection = best_num
                try:
                    selection = int(selection)
                    selected_path = matches[selection]
                    return selected_path
                except Exception:
                    selection = None
                    pass
        else:
            return matches[0]

def find_sc_versions(app_name='SuperCollider.app', hint=None, max_depth=4):
    search_paths = get_default_locations()

    if hint:
        search_paths.insert(qpm.validate_path(hint))

    apps = list()
    for path in search_paths:
        path =  os.path.expandvars(os.path.expanduser(path))
        for d in range(0, max_depth):
            glob_path = os.path.join(
                path,
                os.path.join(*(['.'] + ['*'] * d)),
                app_name
            )
            results = glob(glob_path)
            apps.extend(results)

    version_dict = dict()
    for app_path in apps:
        app_path = os.path.abspath(app_path)
        version = determine_version(app_path)
        version_dict[app_path] = version

    return version_dict

def validate_version(old_version):
    # try to coerce version to semver - step through each replacement pattern until success
    patterns = [
        ['\.-?alpha(.*)', '.0-alpha.\\1'],
        ['\.-?beta(.*)', '.0-beta.\\1'],
        ['\.-?rc(.*)', '.0-rc.\\1'],
        [' \(Revision ([0-9a-z]+)\)', '+\\1'],
        ['-Unofficial Build-', '0.0.0-unofficial']
    ]

    try:
        semver = Version(old_version, partial=True)
        return semver
    except ValueError:
        for pat in patterns:
            try:
                new_version = re.sub(pat[0], pat[1], old_version)
                semver = Version(new_version, partial=True)
                return semver
            except ValueError:
                pass

    return Version('0.0.0')


def determine_version(app_path):
    if platform.system() == 'Darwin':
        version = None

        plist = os.path.join(app_path, 'Contents', 'Info.plist')
        with open(plist, 'r') as f:
            plist_contents = f.read()
            minor = re.findall('<key>CFBundleVersion</key>\s*<string>(.*)</string>', plist_contents)
            minor = minor[0] if len(minor) else None

            major = re.findall('<key>CFBundleShortVersionString</key>\s*<string>(.*)</string>', plist_contents)
            major = major[0] if len(major) else None

            version = ''
            if major: version += major + '.'
            if minor: version += minor
            version = re.sub('\.+', '.', version)

        if version:
            version = validate_version(version)
            return version
        else:
            return Version('0.0.0')