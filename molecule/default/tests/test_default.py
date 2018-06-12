import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_rrentry(host):
    assert ('localhost.' in
            host.check_output('dig +noall +answer NS test.local @localhost'))
    assert ('192.168.1.1' in
            host.check_output('dig +noall +answer A server1.test.local' +
                              ' @localhost')
            )
    assert ('web-server' in
            host.check_output('dig +noall +answer CNAME www.test.local' +
                              ' @localhost')
            )


def test_manual_soa(host):
    soa = host.check_output('dig +noall +answer SOA manual-soa-test.local ' +
                            ' @localhost')
    soa_parts = soa.split()
    # Ensure that manual set SOA is correctly respected
    assert '20101010' in soa_parts[6]
    # Ensure that email address is correctly encoded
    assert 'admin.example.com.' in soa_parts[5]
