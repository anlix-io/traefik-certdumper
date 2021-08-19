#!/usr/bin/python
import argparse
import base64
import json
import os

def read_cert(storage_dir, filename):
    cert_path = os.path.join(storage_dir, filename)
    if os.path.exists(cert_path):
        with open(cert_path, 'rb') as cert_file:
            return cert_file.read()
    return None

def has_changes(storage_dir, domain, cert_content):
  cert_dir = os.path.join(storage_dir, '%s' % (domain,))
  data_atual = read_cert(cert_dir, 'cert.pem')
  if(data_atual):
    if(data_atual == cert_content['cert']):
      return False
    else:
      return True
  else:
    return True

def write_cert(storage_dir, domain, cert_content):
  cert_dir = os.path.join(storage_dir, '%s' % (domain,))
  if not os.path.exists(cert_dir):
    os.makedirs(cert_dir)
    os.chown(cert_dir, 1000, 1000)
  keyfile = os.path.join(cert_dir, 'key.pem')
  certfile = os.path.join(cert_dir, 'cert.pem')
  with open(keyfile, 'wb') as cert_file:
      cert_file.write(cert_content['key'])
  os.chmod(keyfile, 0o600)
  os.chown(keyfile, 1000, 1000)

  with open(certfile, 'wb') as cert_file:
      cert_file.write(cert_content['cert'])
  os.chmod(certfile, 0o600)
  os.chown(certfile, 1000, 1000)


def read_certs(acme_json_path):
    with open(acme_json_path) as acme_json_file:
        acme_json = json.load(acme_json_file)

    certs_json = acme_json['Certificates']
    certs = {}
    for cert in certs_json:
        domain = cert['Domain']['Main']
        domain_cert = cert['Certificate']
        domain_key = cert['Key']
        # Only get the first cert (should be the most recent)
        keys={}
        if domain not in certs:
          keys['cert'] = to_pem_data(domain_cert)
          keys['key'] = to_pem_data(domain_key)
        certs[domain] = keys

    return certs

def to_pem_data(json_cert):
    return base64.b64decode(json_cert)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Dump all certificates out of Traefik's acme.json file")
    parser.add_argument('acme_json', help='path to the acme.json file')
    parser.add_argument('dest_dir',
                        help='path to the directory to store the certificate')

    args = parser.parse_args()

    #check cert path for right permissions
    if os.path.exists(args.dest_dir):
      os.chmod(args.dest_dir, 0o755)

    certs = read_certs(args.acme_json)
    print('Found certs for %d domains' % (len(certs),))
    for domain, cert in certs.items():
      if(has_changes(args.dest_dir, domain, cert)):
        print('Writing cert for domain %s' % (domain,))
        write_cert(args.dest_dir, domain, cert)

    print('Done')

