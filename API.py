#!/usr/bin/env python
# encoding: utf-8

__author__ = 'Dani'

import json
from jsonmodels import models, fields

class PFInput():
    """QoS-Request data structure"""
    class QoS(models.Base):
        """QoS requested parameters"""
        bandwidth = fields.IntField(required=True)
        delay = NotImplemented
        packet_loss = NotImplemented
        jitter = NotImplemented
        utilization = NotImplemented

    class Address(models.Base):
        """Unfinished"""







