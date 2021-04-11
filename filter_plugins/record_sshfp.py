# Copyright (c) 2017 Pierre-GINDRAUD
# The MIT License (MIT)


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleFilterError

import base64
import hashlib


# Mapping between SSH Key type in raw SSH strings
g_type_mapping = dict({
    'ssh-rsa': 1,
    'rsa': 1,
    'dsa': 2,
    'ssh-dss': 2,
    'ssh-ecdsa': 3,
    'ecdsa-sha2-nistp256': 3,
    'ssh-ed25519': 4,
    'ed25519': 4
})

# Mapping of fingerprint digests
g_digest_mapping = dict({
    'SHA-1': 1,
    'SHA1': 1,
    'SHA-256': 2,
    'SHA256': 2
})

"""
This filter takes in input SSH public keys in raw format and produce SSHFP entries ready to be put in a dns zone
"""


def sshfp_record_data_from_key(key, key_type, fingerprint_type='SHA-1'):
    """Build a SSFP entry from parts of a ssh key

    Args:
        key : the key part of the ssh public key
        key_type : the type part of the ssh public key, see g_type_mapping above
                    Ex: ssh-rsa
        fingerprint_type : the type of fingerprint to produce, see g_digest_mapping above
    """
    if not isinstance(key, (str)):
        raise AnsibleFilterError('A string was expected')

    if not key_type in g_type_mapping:
        raise AnsibleFilterError("The given SSH key type '{}' is unknown".format(type))

    if isinstance(fingerprint_type, str):
        if fingerprint_type in g_digest_mapping:
            digest_type = g_digest_mapping[fingerprint_type]
        else:
            raise AnsibleFilterError("Unknown digest type '{}'. Available {}".format(fingerprint_type, g_digest_mapping.values()))
    elif isinstance(fingerprint_type, int):
        if fingerprint_type in g_digest_mapping.values():
            digest_type = fingerprint_type
        else:
            raise AnsibleFilterError("Unknown digest type '{}'. Available {}".format(fingerprint_type, g_digest_mapping.values()))
    else:
        raise AnsibleFilterError('Bad value for fingerprint_type argument')

    entry = dict({
        'algorithm': g_type_mapping[key_type],
        'type': digest_type
    })

    try:
        rawkey = base64.b64decode(key)
    except TypeError:
        raise AnsibleFilterError('Failed to base64 decode the given raw key')

    if digest_type == g_digest_mapping['SHA-1']:
        digest_function = hashlib.sha1
    elif digest_type == g_digest_mapping['SHA-256']:
        digest_function = hashlib.sha256
    else:
        raise AnsibleFilterError('Unknown digest type')

    entry['fingerprint'] = digest_function(rawkey).hexdigest().upper()
    return entry

# ---- Ansible filters ----
class FilterModule(object):
    ''' URI filter '''

    def filters(self):
        return {
            'sshfp_record_data_from_key': sshfp_record_data_from_key
        }
