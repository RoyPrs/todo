# -*- coding: utf-8 -*-
#
# todo/common/model_mixins.py
#

"""
Mixins used in Django models.
"""
#
# ValidateOnSaveMixin
#
class ValidateOnSaveMixin:
    def save(self, *args, **kwargs):
        """
        Execute ``full_clean``.

        """
        self.full_clean()
        super().save(*args, **kwargs)
