from pybuilder.core import use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")
use_plugin('copy_resources')
use_plugin("filter_resources")
use_plugin('python.integrationtest')
use_plugin('python.cram')

name = "aws-certificate-management"
default_task = ["clean", "analyze", "publish"]


@init
def set_properties(project):
    project.depends_on("awscli")
    project.depends_on("cfn-sphere")
    project.depends_on("boto3")
    project.build_depends_on("dnspython")
    project.build_depends_on("unittest2")
    project.build_depends_on("flake8-respect-noqa")

    project.set_property('integrationtest_inherit_environment', True)
    project.set_property('integrationtest_always_verbose', True)

    # FIXME
    project.set_property("coverage_break_build", False)


@init(environments='teamcity')
def set_properties_for_teamcity_builds(project):
    import os
    project.set_property('teamcity_output', True)
    project.version = '%s.%s' % (project.version,
                                 os.environ.get('BUILD_NUMBER', 0))
    project.default_task = ['clean', 'install_build_dependencies', 'publish']
    project.set_property('install_dependencies_index_url',
                         os.environ.get('PYPIPROXY_URL'))
    project.rpm_release = os.environ.get('RPM_RELEASE', 0)
    project.set_property('copy_resources_target', '$dir_dist')
    project.get_property('copy_resources_glob').extend(['setup.cfg'])
    project.get_property('filter_resources_glob').extend(['**/setup.cfg'])
    # to set ENV variable for the next step(s) - snakepit
    # used by metarunner: Build and Upload RPM Packages with snakepit and rpmbuild
    print "##teamcity[setParameter name='env.pyb_project_version' value='%s']" % (project.version)

