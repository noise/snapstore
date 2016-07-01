import os
import subprocess
from charmhelpers.core import hookenv, host
from charmhelpers.core.templating import render
from charmhelpers.fetch import apt_update, apt_install
from charms.reactive import hook, when, when_not, set_state, remove_state
from charms.reactive.bus import get_states


@hook('install')
def install():
    apt_update()
    install_workload()
    set_state('server.start')


@hook('upgrade-charm')
def upgrade():
    service = "snapstore"
    need_restart = False
    if host.service_running(service):
        need_restart = True
    if need_restart:
        host.service_stop(service)
    install_workload()
    if need_restart:
        host.service_start(service)


@when('server.started')
def server_start():
    hookenv.open_port(5000)
    hookenv.status_set('active', 'Ready')


@when_not('server.started')
def start_server():
    host.service_start("snapstore")
    set_state('server.started')


@hook('stop')
def stop_server():
    host.service_start("snapstore")
    remove_state('server.started')


@when('website.available')
def configure_website(website):
    website.configure(5000)


def install_workload():
    dir = os.path.join(hookenv.charm_dir(), "files")
    installer = os.path.join(dir, "install.sh")
    subprocess.check_call(installer)
    local_binary = os.path.join(dir, "run.sh")
    render(source="upstart",
           target="/etc/init/snapstore.conf",
           owner="root",
           perms=0o644,
           context={
               "dir": dir,
               "install_binary": local_binary,
           })
