# -*- coding: utf-8 -*-
import base64
import binascii
import contextlib
import datetime
import hmac
import ipaddress
import itertools
import json
import logging
import os
import time
from collections import defaultdict
from hashlib import sha256
from itertools import chain, repeat

import decorator
import passlib.context
import pytz
from lxml import etree
from lxml.builder import E
from psycopg2 import sql

from odoo import api, fields, models, tools, SUPERUSER_ID, _, Command
from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from odoo.http import request
from odoo.modules.module import get_module_resource
from odoo.osv import expression
from odoo.service.db import check_super
# from odoo.tools import partition, frozendict, lazy_property, image_process

_logger = logging.getLogger(__name__)



class AccountMove(models.Model):

    _inherit = 'account.move'


    # def action_post(self):
    #     res = super(AccountMove,self).action_post()
    #     print("\n\n\n>>>>>>>>>>>>>>>res>>>>>>>>>\n\n\n",res)
    #     return res

class ResUsers(models.Model):

    _inherit = 'res.users'

    # @api.model
    # def has_group(self, group_ext_id: str) -> bool:
    #     # use singleton's id if called on a non-empty recordset, otherwise
    #     # context uid

    #     uid = self.id or self._uid
    #     user_group = [data.name for data in self.env.user.groups_id if data.name=='Sale Invoice Confirmation']
    #     if group_ext_id in ['account.group_account_manager','account.group_account_invoice']   and user_group:
    #         return True
    #     return self.with_user(uid)._has_group(group_ext_id)

    @api.readonly
    def has_group(self, group_ext_id: str) -> bool:
        """ Return whether user ``self`` belongs to the given group (given by its
        fully-qualified external ID).

        Note that the group ``"base.group_no_one"`` is only effective in debug
        mode: the method returns ``True`` if the user belongs to the group and
        the current request is in debug mode.
        """


        self.ensure_one()
        if not (self.env.su or self == self.env.user or self.env.user._has_group('base.group_user')):
            # this prevents RPC calls from non-internal users to retrieve
            # information about other users
            raise AccessError(_("You can ony call user.has_group() with your current user."))

        result = self._has_group(group_ext_id)
        if group_ext_id == 'base.group_no_one':
            result = result and bool(request and request.session.debug)
        # uid = self.id or self._uid

        uid = self.id or self._uid
        user_group = [data.name for data in self.env.user.groups_id if data.name=='Sale Invoice Confirmation']
        if group_ext_id in ['account.group_account_manager','account.group_account_invoice'] and user_group:
            return True
        return result


    def _has_group(self, group_ext_id: str) -> bool:
        user_group = [data.name for data in self.env.user.groups_id if data.name=='Sale Invoice Confirmation']
        if group_ext_id == 'account.group_account_manager' and user_group:
            return True
        """ Return whether user ``self`` belongs to the given group.

        :param str group_ext_id: external ID (XML ID) of the group.
           Must be provided in fully-qualified form (``module.ext_id``), as there
           is no implicit module to use..
        :return: True if user ``self`` is a member of the group with the
           given external ID (XML ID), else False.
        """
        group_id = self.env['res.groups']._get_group_definitions().get_id(group_ext_id)
        # for new record don't fill the ormcache
        return group_id in (self._get_group_ids() if self.id else self.groups_id._origin._ids)

    # @api.model
    # @tools.ormcache('self._uid', 'group_ext_id')
    # def _has_group(self, group_ext_id):
    #     user_group = [data.name for data in self.env.user.groups_id if data.name=='Sale Invoice Confirmation']
    #     if group_ext_id == 'account.group_account_manager' and user_group:
    #         return True

    #     """Checks whether user belongs to given group.

    #     :param str group_ext_id: external ID (XML ID) of the group.
    #        Must be provided in fully-qualified form (``module.ext_id``), as there
    #        is no implicit module to use..
    #     :return: True if the current user is a member of the group with the
    #        given external ID (XML ID), else False.
    #     """
    #     assert group_ext_id and '.' in group_ext_id, "External ID '%s' must be fully qualified" % group_ext_id
    #     module, ext_id = group_ext_id.split('.')
    #     self._cr.execute("""SELECT 1 FROM res_groups_users_rel WHERE uid=%s AND gid IN
    #                         (SELECT res_id FROM ir_model_data WHERE module=%s AND name=%s)""",
    #                      (self._uid, module, ext_id))
    #     return bool(self._cr.fetchone())

    # has_group.clear_cache = _has_group.clear_cache
    