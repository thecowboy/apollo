#
# Copyright (C) 2011 by Tony Young
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

"""
Apollo security domain administration tool.
"""

import sys
import os

dist_root = os.path.join(os.path.dirname(__file__), "..")

# add the apollo path to the pythonpath
sys.path.insert(1, dist_root)

import inspect

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from apollo.server import skeletonSetup
from apollo.server.models import meta
from apollo.server.models.auth import Group, SecurityDomain, INDIRECTLY_IN_DOMAIN, DIRECTLY_IN_DOMAIN, User

class ASDAT(object):
    def __init__(self):
        skeletonSetup(os.path.join(dist_root, "apollod.conf"))
        self.sess = meta.Session()

    #
    # domain actions
    #
    def action_domlist(self):
        def printDomainTree(domain, level=0):
            print "%s%s" % ("    " * level, domain.name)

            for domain in self.sess.query(SecurityDomain).filter(SecurityDomain.parent_id == domain.id):
                printDomainTree(domain, level+1)

        print "Domain listing:\n"

        for domain in self.sess.query(SecurityDomain).filter(SecurityDomain.parent_id == None):
            printDomainTree(domain)

    def action_dominfo(self, path):
        try:
            domain = SecurityDomain.byPath(path.decode("utf-8"))
        except (NoResultFound, MultipleResultsFound):
            print "Domain %s not found." % path
            sys.exit(1)

        print """\
About security domain %(path)s:

    ID:                 %(id)s
    Name:               %(name)s
    Parent:             %(parent_name)s (%(parent_id)s)
    Direct Members:     NOT IMPLEMENTED
    Indirect Members:   NOT IMPLEMENTED\
""" % {
            "path"          : path,
            "id"            : domain.id,
            "name"          : domain.name,
            "parent_name"   : domain.parent.name,
            "parent_id"     : domain.parent.id
        }

    def action_domadd(self, path):
        raise NotImplementedError("domadd not implemented") # TODO: implement

    def action_domdel(self, path):
        try:
            domain = SecurityDomain.byPath(path.decode("utf-8"))
        except (NoResultFound, MultipleResultsFound):
            print "Domain %s not found." % path
            sys.exit(1)

        affected_domains = []

        def recursiveDomainDelete(domain, path=()):
            affected_domains.append(".".join(path))

            for child in domain.children:
                recursiveDomainDelete(child, path + (child.name,))

            self.sess.delete(domain)

        recursiveDomainDelete(domain, tuple(path.split(".")))
        self.sess.commit()

        print "The following domains were deleted:"
        for domain_name in affected_domains:
            print " * %s" % domain_name

    #
    # groups
    #
    def action_grplist(self):
        print "Group listing:"
        for group in self.sess.query(Group):
            print " * %s" % group.name

    def action_grpinfo(self, group_name):
         try:
             group = self.sess.query(Group).filter(Group.name == group_name.decode("utf-8")).one()
         except (NoResultFound, MultipleResultsFound):
            print "Group \"%s\" not found." % group_name
            sys.exit(1)

         print """\
About group %(name)s:

    ID:                 %(id)s
    Direct Domains:     %(domains)s
    Members:            %(members)s\
""" % {
            "name"          : group.name,
            "id"            : group.id,
            "domains"       : ", ".join([ domain.getPath() for domain in group.security_domains ]) or "(none)",
            "members"       : ", ".join([ user.name for user in group.users ]) or "(none)"
        }

    def action_grpchk(self, group_name, path):
        try:
             group = self.sess.query(Group).filter(Group.name == group_name.decode("utf-8")).one()
        except (NoResultFound, MultipleResultsFound):
            print "Group \"%s\" not found." % group_name
            sys.exit(1)

        try:
            domain = SecurityDomain.byPath(path.decode("utf-8"))
        except (NoResultFound, MultipleResultsFound):
            print "Domain %s not found." % path
            sys.exit(1)

        result = group.inDomain(domain)

        if not result:
            print "Group \"%s\" is not part of domain %s." % (group.name, path)
        elif result == DIRECTLY_IN_DOMAIN:
            print "Group \"%s\" is directly part of domain %s." % (group.name, path)
        elif result == INDIRECTLY_IN_DOMAIN:
            print "Group \"%s\" is indirectly part of domain %s." % (group.name, path)

    def action_grpadd(self, group_name, path):
        try:
             group = self.sess.query(Group).filter(Group.name == group_name.decode("utf-8")).one()
        except (NoResultFound, MultipleResultsFound):
            print "Group \"%s\" not found." % group_name
            sys.exit(1)

        try:
            domain = SecurityDomain.byPath(path.decode("utf-8"))
        except (NoResultFound, MultipleResultsFound):
            print "Domain %s not found." % path
            sys.exit(1)

        if group.inDomain(domain):
            print "Group \"%s\" is already part of domain %s." % (group.name, path)
            return

        group.security_domains.append(domain)
        self.sess.merge(group)
        self.sess.commit()

        print "Group \"%s\" added to domain %s." % (group.name, path)

    def action_grpdel(self, group_name, path):
        try:
             group = self.sess.query(Group).filter(Group.name == group_name.decode("utf-8")).one()
        except (NoResultFound, MultipleResultsFound):
            print "Group \"%s\" not found." % group_name
            sys.exit(1)

        try:
            domain = SecurityDomain.byPath(path.decode("utf-8"))
        except (NoResultFound, MultipleResultsFound):
            print "Domain %s not found." % path
            sys.exit(1)

        if group.inDomain(domain) != DIRECTLY_IN_DOMAIN:
            print "Group \"%s\" is not directly part of domain %s." % (group.name, path)
            return

        group.security_domains.remove(domain)
        self.sess.merge(group)
        self.sess.commit()

        print "Group \"%s\" removed from domain %s." % (group.name, path)

    #
    # users
    #
    def action_usrlist(self):
        print "User listing:"
        for user in self.sess.query(User):
            print " * %s" % user.name

    def action_usrinfo(self, user_name):
         try:
             user = self.sess.query(User).filter(User.name == user_name.decode("utf-8")).one()
         except (NoResultFound, MultipleResultsFound):
            print "User \"%s\" not found." % user_name
            sys.exit(1)

         print """\
About user %(name)s:

    ID:                 %(id)s
    Group:              %(group)s
    Direct Domains:     %(domains)s\
""" % {
            "name"          : user.name,
            "id"            : user.id,
            "group"         : user.group.name,
            "domains"       : ", ".join([ domain.getPath() for domain in user.group.security_domains ]) or "(none)"
        }

    def action_usrchg(self, user_name, group_name):
        try:
            user = self.sess.query(User).filter(User.name == user_name.decode("utf-8")).one()
        except (NoResultFound, MultipleResultsFound):
            print "User \"%s\" not found." % user_name
            sys.exit(1)

        try:
             group = self.sess.query(Group).filter(Group.name == group_name.decode("utf-8")).one()
        except (NoResultFound, MultipleResultsFound):
            print "Group \"%s\" not found." % group_name
            sys.exit(1)

        user.group_id = group.id
        self.sess.merge(user)
        self.sess.commit()
        print "User \"%s\" changed to group \"%s\"." % (user.name, group.name)

    def action_usrchk(self, user_name, path):
        try:
            user = self.sess.query(User).filter(User.name == user_name.decode("utf-8")).one()
        except (NoResultFound, MultipleResultsFound):
            print "User \"%s\" not found." % user_name
            sys.exit(1)

        try:
            domain = SecurityDomain.byPath(path.decode("utf-8"))
        except (NoResultFound, MultipleResultsFound):
            print "Domain %s not found." % path
            sys.exit(1)

        result = user.inDomain(domain)

        if not result:
            print "User \"%s\" is not part of domain %s." % (user.name, path)
        elif result == DIRECTLY_IN_DOMAIN:
            print "User \"%s\" is directly part of domain %s." % (user.name, path)
        elif result == INDIRECTLY_IN_DOMAIN:
            print "User \"%s\" is indirectly part of domain %s." % (user.name, path)

    def action_help(self):
        print >>sys.stderr, """\
Apollo Security Domain Administration Tool

Usage: %s [OPTIONS] COMMAND [ARG1 [ARG2 [...]]]

Commands:
    Domains:
        domlist     List all security domains in a tree.
        dominfo     Get information about a domain.
        domadd      Create a new security domain by path.
        domdel      Delete a security domain by path.

    Groups:
        grplist     List all groups.
        grpinfo     Get information about a group.
        grpchk      Verify that a group is in a security domain.
        grpadd      Add a group to a security domain.
        grpdel      Delete a group from a security domain.

    Users:
        usrlist     List all users.
        usrinfo     Get information about a user.
        usrchg      Change the group of a user.
        usrchk      Verify that a user is in a security domain.\
""" % sys.argv[0]

    def go(self, cmd_name=None, *args):
        if cmd_name is None:
            self.action_help()
            sys.exit()
        cmd = getattr(self, "action_%s" % cmd_name)

        func_man_argnum = len(inspect.getargspec(cmd).args) - 1
        if len(args) != func_man_argnum:
            print >>sys.stderr, "Incorrect number of arguments for %s: got %d, expected %d" % (cmd_name, len(args), func_man_argnum)
            sys.exit(1)

        cmd(*args)

if __name__ == "__main__":
    ASDAT().go(*sys.argv[1:])
