###############################################################################
#                            Rest Internal Makefile
#
# Author:
#
# Support:
#	pyats-support@cisco.com
#
# Version:
#   v1.0.0
#
# Date:
#   May 2017
#
# About This File:
#   This script will build the Rest package for distribution in PyPI server
#
# Requirements:
#	1. Module name is the same as package name.
#	2. setup.py file is stored within the module folder
###############################################################################

# Variables
PKG_NAME      = rest.connector
BUILDDIR      = $(shell pwd)/__build__
PROD_USER     = pyadm@pyats-ci
PROD_PKGS     = /auto/pyats/packages
STAGING_PKGS  = /auto/pyats/staging/packages
STAGING_EXT_PKGS  = /auto/pyats/staging/packages_external
PYTHON        = python
TESTCMD       = python -m unittest discover tests
DISTDIR       = $(BUILDDIR)/dist

.PHONY: clean package distribute distribute_staging distribute_staging_external\
        develop undevelop populate_dist_dir help docs pubdocs tests

help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo ""
	@echo "package                     : Build the package"
	@echo "test                        : Test the package"
	@echo "distribute                  : Distribute the package to PyPi server"
	@echo "distribute_staging          : Distribute the package to staging area"
	@echo "distribute_staging_external : Distribute the package to external staging area"
	@echo "clean                       : Remove build artifacts"
	@echo "develop                     : Build and install development package"
	@echo "undevelop                   : Uninstall development package"
	@echo "docs                        : Build Sphinx documentation for this package"
	@echo "distribute_docs             : Publish the Sphinx documentation to the official cisco-shared web server for all to see"

docs:
	@echo ""
	@echo "--------------------------------------------------------------------"
	@echo "Building $(PKG_NAME) documentation"
	@echo ""

	@cd docs; make html

	@echo "Completed building docs for preview."
	@echo ""
	@echo "Done."
	@echo ""

pubdocs:
	@echo "Not implemented yet."

test:
	@$(TESTCMD)

package:
	@echo ""
	@echo "--------------------------------------------------------------------"
	@echo "Building $(PKG_NAME) distributable: $@"
	@echo ""

	@mkdir -p $(DISTDIR)

    # NOTE : Only specify --universal if the package works for both py2 and py3
    # https://packaging.python.org/en/latest/distributing.html#universal-wheels
	@./setup.py bdist_wheel --dist-dir=$(DISTDIR)
	@./setup.py sdist --dist-dir=$(DISTDIR)

	@echo ""
	@echo "Completed building: $@"
	@echo ""
	@echo "Done."
	@echo ""

develop:
	@echo ""
	@echo "--------------------------------------------------------------------"
	@echo "Building and installing $(PKG_NAME) development distributable: $@"
	@echo ""

	@pip uninstall -y rest.connector || true
	@pip install f5-icontrol-rest requests_mock requests dict2xml
	@./setup.py develop --no-deps -q

	@echo ""
	@echo "Completed building and installing: $@"
	@echo ""
	@echo "Done."
	@echo ""

undevelop:
	@echo ""
	@echo "--------------------------------------------------------------------"
	@echo "Uninstalling $(PKG_NAME) development distributable: $@"
	@echo ""

	@./setup.py develop --no-deps -q --uninstall

	@echo ""
	@echo "Completed uninstalling: $@"
	@echo ""
	@echo "Done."
	@echo ""

clean:
	@echo ""
	@echo "--------------------------------------------------------------------"
	@echo "Removing make directory: $(BUILDDIR)"
	@rm -rf $(BUILDDIR)
	@echo ""
	@echo "Removing build artifacts ..."
	@./setup.py clean
	@echo ""
	@echo "Done."
	@echo ""

distribute:
	@echo ""
	@echo "--------------------------------------------------------------------"
	@echo "Copying all distributable to $(PROD_PKGS)"
	@test -d $(DISTDIR) || { echo "Nothing to distribute! Exiting..."; exit 1; }
	@ssh -q $(PROD_USER) 'test -e $(PROD_PKGS)/$(PKG_NAME) || mkdir $(PROD_PKGS)/$(PKG_NAME)'
	@scp $(DISTDIR)/* $(PROD_USER):$(PROD_PKGS)/$(PKG_NAME)/
	@echo ""
	@echo "Done."
	@echo ""

distribute_staging:
	@echo ""
	@echo "--------------------------------------------------------------------"
	@echo "Copying all distributable to $(STAGING_PKGS)"
	@test -d $(DISTDIR) || { echo "Nothing to distribute! Exiting..."; exit 1; }
	@ssh -q $(PROD_USER) 'test -e $(STAGING_PKGS)/$(PKG_NAME) || mkdir $(STAGING_PKGS)/$(PKG_NAME)'
	@scp $(DISTDIR)/* $(PROD_USER):$(STAGING_PKGS)/$(PKG_NAME)/
	@echo ""
	@echo "Done."
	@echo ""

distribute_staging_external:
	@echo ""
	@echo "--------------------------------------------------------------------"
	@echo "Copying all distributable to $(STAGING_EXT_PKGS)"
	@test -d $(DISTDIR) || { echo "Nothing to distribute! Exiting..."; exit 1; }
	@ssh -q $(PROD_USER) 'test -e $(STAGING_EXT_PKGS)/$(PKG_NAME) || mkdir $(STAGING_EXT_PKGS)/$(PKG_NAME)'
	@scp $(DISTDIR)/* $(PROD_USER):$(STAGING_EXT_PKGS)/$(PKG_NAME)/
	@echo ""
	@echo "Done."
	@echo ""

changelogs:
	@echo ""
	@echo "--------------------------------------------------------------------"
	@echo "Generating changelog file"
	@echo ""
	@python3 -c "from ciscodistutils.make_changelog import main; main('./docs/changelog/undistributed', './docs/changelog/undistributed.rst')"
	@echo "pyats.contrib changelog created..."
	@echo ""
	@echo "Done."
	@echo ""
