from pybuilder.core import use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")

name = "aws-certificate-management"
default_task = ["clean", "analyze", "publish"]


@init
def set_properties(project):
    pass