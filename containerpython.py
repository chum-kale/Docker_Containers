import os
import sys
import glob
import json

docker_home = '/var/snap/docker/common/var-lib-docker/'
container_id = sys.argv[1]

container_files = glob.glob('{}/containers/{}*'.format(docker_home, container_id))
if len(container_files) == 0:
    print('container not found: {}'.format(container_id))
    sys.exit(1)

container_file = '{}/config.v2.json'.format(container_files[0])

full_container_id = ''
driver = '/var/snap/docker/common/var-lib-docker/'
with open(container_file, 'r') as cf:
    container_info = json.load(cf)
    full_container_id = container_info["ID"]
    driver = container_info["Driver"]

if full_container_id == '':
    print('cannot find full_container_id for container: {}'.format(container_id))
    sys.exit(1)

mount_id_file = '{}/image/{}/layerdb/mounts/{}/mount-id'.format(docker_home, driver, full_container_id)

mount_id = ''
with open(mount_id_file, 'r') as mf:
    mount_id = mf.read()

lower_dir = []
lower_id_file = '{}/{}/{}/lower'.format(docker_home, driver, mount_id)
with open(lower_id_file, 'r') as lf:
    lower_id_symlinks = lf.read()
    for symlink in lower_id_symlinks.split(':'):
        symlink_path = '{}/{}/{}'.format(docker_home, driver, symlink)
        lower_dir.append(os.path.realpath(symlink_path))


data = {
        "LowerDir": ':'.join(lower_dir),
        "MergedDir": "{}/{}/{}/merged".format(docker_home, driver, mount_id),
        "UpperDir": "{}/{}/{}/diff".format(docker_home, driver, mount_id),
        "WorkDir": "{}/{}/{}/work".format(docker_home, driver, mount_id)
        }

print(json.dumps(data, indent=2))


# in /var/lib/docker/containers directory there are directories having name of full_container_id (initial 12 chars match with short container id we see in "docker ps" output)
# E.g. for short container id 3ece8d62c1a5 (the container id we see in docker ps output),
# the container directory is /var/lib/docker/containers/3ece8d62c1a52687f1ec702b3ffced3288f7a25da64efdebe9df54a2efae57d4
# in this directory the file config.v2.json is all the info about the container.
# So the full file path for container config is /var/lib/docker/containers/3ece8d62c1a52687f1ec702b3ffced3288f7a25da64efdebe9df54a2efae57d4/config.v2.json

# We also get the driver name by parsing this file as json - its a dictionary and "Driver" key provides the driver directory 
# Now to populate MergedDir, UpperDir and WorkDir we need mount_id. It is present in var/lib/docker/image/overlay2/layerdb/mounts/<full_container_id>/mount-id
# The content of this file is mount-id which can be used in file paths to generate the merged, diff and work directories...
# MergedDir: /var/lib/docker/overlay2/<mount-id>/merged 
# UpperDir : /var/lib/docker/overlay2/<mount-id>/diff
# WorkDir: /var/lib/docker/overlay2/<mount-id>/work

# LowerDir:
# For lower dir we need to read content of /var/lib/docker/overlay2/<mount-id>/lower file.
# This file has symlink names seprated by ':' character, for example:
# $ sudo cat /var/lib/docker/overlay2/f9fa6368fed7a61935c149b789b7b4c85204f2a02f199791ee20876459168c76/lower
# l/DPON5TOCBL22Y2BFDJAJCYPEOS:l/TMNBRPDXFT76NIPLYQX6S6HMRK:l/OFQK64LE3UI4XQJIITSMTOBX7I:l/MBN3522KN5OSSNPWQY4ARL6X5C:l/54OGZASR24XLC3UUEG2JZO33XL:l/R44NMPJRLDVXJ2A4AYLHUAESOR:l/MDWE6LZVZKO64UOT7UYHL54BUP
# These symlinks are in /var/lib/docker/overlay2/ directory. We need to get realpath for that symlink. E.g.
# $ sudo ls -l /var/lib/docker/overlay2/l/DPON5TOCBL22Y2BFDJAJCYPEOS
# lrwxrwxrwx 1 root root 77 Mar  8 19:11 /var/lib/docker/overlay2/l/DPON5TOCBL22Y2BFDJAJCYPEOS -> ../f9fa6368fed7a61935c149b789b7b4c85204f2a02f199791ee20876459168c76-init/diff 
# 
# So read the content of file /var/lib/docker/overlay2/<mount-id>/lower and split it on ':'.
# Then for each symlink entry get the real path of symlink: /var/lib/docker/overlay2/<symlink>
# Put all of these realpaths back into single string separated by ':' and you have the LowerDir.
