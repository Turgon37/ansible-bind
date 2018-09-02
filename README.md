Ansible Role Bind DNS server
=========

[![Build Status](https://travis-ci.org/Turgon37/ansible-bind.svg?branch=master)](https://travis-ci.org/Turgon37/ansible-bind)
[![License](https://img.shields.io/badge/license-MIT%20License-brightgreen.svg)](https://opensource.org/licenses/MIT)
[![Ansible Role](https://img.shields.io/badge/ansible%20role-Turgon37.bind-blue.svg)](https://galaxy.ansible.com/Turgon37/bind/)

## Description

:grey_exclamation: Before using this role, please know that all my Ansible roles are fully written and accustomed to my IT infrastructure. So, even if they are as generic as possible they will not necessarily fill your needs, I advice you to carrefully analyse what they do and evaluate their capability to be installed securely on your servers.

This roles configure the bind dns server.

## Requirements

Require Ansible >= 2.4

### Dependencies

## OS Family

This role is available for

  * CentOS 7
  * Debian 8/9

## Features

At this day the role can be used to :

  * install bind9
  * perform basic configuration
  * define static zones with
      * automatic SOA entries and zone's serials numbers computation
      * templating from inventory or a remote url (and checksum check)
  * define slaves zones
  * install updated root server list
  * [local facts](#facts)

## Configuration

The variables that can be passed to this role and a brief description about them are as follows:

| Name                              | Types/Values             | Description                                                              |
| ----------------------------------| -------------------------|--------------------------------------------------------------------------|
| bind__facts                       | Boolean                  | Install the local fact script                                            |
| bind__default_port                | Integer                  | The default port to listen on                                            |
| bind__listen_on                   | String/List of string    | List of network addresses to listen on for IPv4                          |
| bind__listen_on_port              | Integer                  | The default port to listen on for IPv4                                   |
| bind__listen_on_v6                | String/List of string    | List of network addresses to listen on for IPv6                          |
| bind__listen_on_v6_port           | Integer                  | The default port to listen on for IPv6                                   |
| bind__allow_query                 | String/List of string    | List of acls/network allowed to query this server                        |
| bind__allow_query_on              | String/List of string    | List of network addresses to listen for query                            |
| bind__blackhole                   | String/List of string    | List of hosts to not respond to                                          |
| bind__acls                        |                          |                                                                          |
| bind__recursion                   | Boolean                  | Enable or not recursion mode                                             |
| bind__allow_recursion             | String/List of string    | List of acls/network allowed to perform recursives queries to this server|
| bind__allow_recursion_on          | String/List of string    | List of network addresses to listen for recursion queries                |
| bind__empty_contact               | String                   | Default contact address empty zones                                      |
| bind__empty_server                | String                   | Default NS entry for empty zones                                         |
| bind__global_zones                | Dict of zones statements | List of zones intended to be set globally                                |
| bind__group_zones                 | Dict of zones statements | List of zones intended to be set at host groups level                    |
| bind__host_zones                  | Dict of zones statements | List of zones intended to be set at host level                           |
| bind__root_server_source_checksum | String                   | The checksum value of                                                    |

Each zones dict bind__(global|group|host)_zones parameters are merged before being applied by ansible, so it let you to define zones in multiple place of Ansible inventory.


### Zone statements

Each zone statement represent the zone declaration with settings and the zone "body" with DNS entries (if needed)

* In case of a static zone (aka master), you can use the following settings

```
bind__global_zones:
  'zone name':
    type: 'master' to declare a static zone or 'slave' to set a zone
    file: 'auto' to let ansible manage the path to the zone file or specify manually a path
    entries:
      - zone entry statement (see below)
      - zone entry statement
```

* In case of a slave zone, you can use the following settings

```
bind__global_zones:
  'zone name':
    type: 'master' to declare a static zone or 'slave' to set a zone
    file: 'auto' to let ansible manage the path to the zone file or specify manually a path
    masters: String or list of masters servers
    allow_update: Optionnal String or list of servers allowed to perform an update
```

### Zone entry statements

For static zone, you have to define zone entries using the following specifications.
The 'entries' key must be a list of dict.
Each dict (corresponding to an DNS Resource Record) can contains theses keys.


* name: the name of the record, default to empty (to allow declaration of multiple records with same name)
* ttl: default to empty (see bind default ttl value)
* class: default to IN
* type: the type of entry in classical availables types : A, CNAME....
According the the 'type' key, the 'data' key must follow some restrictions (see below)
* data: the content of the entry, take care, if the 'type' value is implemented in this role the data field must be correctly formatted (see paragraph below). Otherwise, the data field will be printed as is in the zone file.
* comment: optionnal comment at the end of the line

Somes examples :

* a simple entry with defaults specifications omitted

```
- name: server1
  type: A
  data: 192.168.1.1
```

* a SOA record with all required values

```
- name: '@'
  type: SOA
  data:
    ns: 'server1'
    email: 'admin@example.com'
    serial:   "00000000"
    refresh:  604800
    retry:    86400
    expiry:   2419200
    negative: 604800
```


### Zone entry type implementations

Some RR types are implemented directly by this role, so you have to format the 'data' field with a correct dict instead of simply set it to a string

This is the list of specifically implemented types :

* [SOA](#soa-type)

#### SOA type

Each DNS zone must have a SOA entry, so this role takes in considerations the two following cases:

* You provided yourself a SOA entry in the 'entries' key of the current zone: your SOA entry will be used, so it must contains all required field !!
* You did not provide a SOA entry for the current zone: Ansible will create one for you, please be sure that you have at least one NS entry, it will be used as SOA NS value. And the serial value will be automatically incremented at each zone changes

If you choose to provide by yourself the SOA record please set all the following keys:

```
- name: '@' # the name of your zone
  type: SOA # mandatory
  data:
    ns: 'server1'                 # the fqdn of your main name server
      email: 'admin@example.com'   # the administrator email, any arobase sign will be converted to dot
      serial:   "00000000"        # The serial (please ensure that it is correctly updated at each zone changes)
      refresh:  604800            # refresh time for slave servers
      retry:    86400             # time between slave retry attempts
      expiry:   2419200           # expiry time considered by slave for this zone
      negative: 604800            # minimum time/default ttl (see implementations according to your version of bind)
```


### Features

* Root server list update

Ansible try to manage list of root servers by it self. To prevent a malicious file to be downloaded it check the checksums of this file against the value of bind__root_server_source_checksum setting.
If it does not match, ansible will fail with an error. To bypass the error set the bind__root_server_source_ignore to true, then the error will be discarded and the file will NOT be downloaded as far.

I personnaly use this role, and then perform, an update of this checksum each time the source file change, so you can keep an eye on my repository. Otherwise you can manage it by yourself.

## Facts

By default the local fact are installed and expose the following variables :


* ```ansible_local.bind.version_full```
* ```ansible_local.bind.version_major```

## Example

### Playbook

Use it in a playbook as follows:

```yaml
- hosts: all
  roles:
    - turgon37.bind
```

### Inventory

To use this role create or update your playbook according the following example :

```
bind__allow_query:
  - '192.168.1.0/24'
  - 'localhost'
bind__listen_on:
  - 192.168.1.10
  - 127.0.0.1
bind__allow_recursion: '192.168.1.0/24'
bind__empty_contact: 'admin@example.com'
bind__global_zones:
  'test.example.local':
    type: 'master'
    file: 'auto'
    entries:
      - { name: '@',                 type: 'NS',     data: 'dns1.example.com.' }
      - { name: 'dns1.example.com.', type: 'A',      data: '192.168.1.10'      }
      - { name: 'srv1',              type: 'A',      data: '192.168.1.210'    }
      - { name: 'srv2',              type: 'A',      data: '192.168.1.211'    }
      - { name: 'storage',           type: 'CNAME',  data: 'srv1'       }
```