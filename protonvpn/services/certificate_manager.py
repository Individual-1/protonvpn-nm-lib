import os

import jinja2
from jinja2 import Environment, FileSystemLoader
from proton.api import Session

from .. import exceptions
from ..constants import (
    CACHED_OPENVPN_CERTIFICATE, OPENVPN_TEMPLATE,
    PROTON_XDG_CACHE_HOME, TEMPLATES
)
from ..enums import ProtocolEnum, ProtocolPortEnum
from ..logger import logger
from . import capture_exception
from .connection_state_manager import ConnectionStateManager


class CertificateManager(ConnectionStateManager):
    def __init__(self):
        super().__init__()

    def generate_vpn_cert(
        self, protocol, session,
        servername, ip_list, cached_cert=CACHED_OPENVPN_CERTIFICATE
    ):
        """Abstract method that generates a vpn certificate.

        Args:
            protocol (ProtocolEnum): ProtocolEnum.TCP, ProtocolEnum.UDP ...
            session (proton.api.Session): the current user session
            servername (string): servername [PT#1]
            ip_list (list): the ips for the selected server
            cached_cert (string): path to where a certificate is to be cached
                (optional)
        Returns:
            string: path to cached certificate
        """
        logger.info("Generating VPN certificate")
        protocol_dict = {
            ProtocolEnum.TCP: self.generate_openvpn_cert,
            ProtocolEnum.UDP: self.generate_openvpn_cert,
            ProtocolEnum.IKEV2: self.generate_strongswan_cert,
            ProtocolEnum.WIREGUARD: self.generate_wireguard_cert
        }

        if not isinstance(protocol, str):
            err_msg = "Incorrect object type, "\
                "str is expected but got {} instead".format(type(protocol))
            logger.error(
                "[!] TypeError: {}. Raising exception.".format(err_msg)
            )
            raise TypeError(err_msg)

        if not isinstance(session, Session):
            err_msg = "Incorrect object type, "\
                "{} is expected "\
                "but got {} instead".format(type(Session), type(protocol))
            logger.error(
                "[!] TypeError: {}. Raising exception.".format(err_msg)
            )
            raise TypeError(err_msg)

        if not isinstance(servername, str):
            err_msg = "Incorrect object type, "\
                "str is expected but got {} instead".format(type(servername))
            logger.error(
                "[!] TypeError: {}. Raising exception.".format(err_msg)
            )
            raise TypeError(err_msg)

        if not isinstance(ip_list, list):
            err_msg = "Incorrect object type, "\
                "list is expected but got {} instead".format(type(ip_list))
            logger.error(
                "[!] TypeError: {}. Raising exception.".format(err_msg)
            )
            raise TypeError(err_msg)

        if len(ip_list) == 0:
            logger.error(
                "[!] ValueError: No servers were provided. Raising exception."
            )
            raise ValueError("No servers were provided")

        self.save_servername(servername)
        self.save_protocol(protocol)

        logger.info("Servername: \"{}\"".format(servername))
        logger.info("Protocol: \"{}\"".format(protocol))

        try:
            return protocol_dict[protocol](
                servername, ip_list,
                cached_cert, protocol
            )
        except KeyError as e:
            logger.exception("[!] IllegalVPNProtocol: {}".format(e))
            raise exceptions.IllegalVPNProtocol(e)
        except jinja2.exceptions.TemplateNotFound as e:
            logger.exception("[!] jinja2.TemplateNotFound: {}".format(e))
            raise jinja2.exceptions.TemplateNotFound(e)
        except Exception as e:
            logger.exception("[!] Unknown exception: {}".format(e))
            capture_exception(e)

    def generate_openvpn_cert(
        self, servername, ip_list,
        cached_cert, protocol
    ):
        """Generates openvpn certificate.

        Args:
            protocol (ProtocolEnum): ProtocolEnum.TCP, ProtocolEnum.UDP ...
            servername (string): servername [PT#1]
            ip_list (list): the ips for the selected server
            cached_cert (string): path to where a certificate is to be cached
        Returns:
            string: path to where a certificate is cached
        """
        logger.info("Generating OpenVPN certificate")
        ports = {
            ProtocolEnum.TCP: ProtocolPortEnum.TCP,
            ProtocolEnum.UDP: ProtocolPortEnum.UDP
        }

        j2_values = {
            "openvpn_protocol": protocol,
            "serverlist": ip_list,
            "openvpn_ports": [ports[protocol]],
        }

        j2 = Environment(loader=FileSystemLoader(TEMPLATES))

        template = j2.get_template(OPENVPN_TEMPLATE)

        if not os.path.isdir(PROTON_XDG_CACHE_HOME):
            os.mkdir(PROTON_XDG_CACHE_HOME)

        with open(cached_cert, "w") as f:
            f.write(template.render(j2_values))

        return cached_cert

    def generate_strongswan_cert(
        self, servername, ip_list,
        cached_cert, _=None
    ):
        """Generates ikev2/strongswan certificate.

        Args:
            servername (string): servername [PT#1]
            ip_list (list): the ips for the selected server
            cached_cert (string): path to where a certificate is to be cached
        Returns:
            bool
        """
        logger.info("Generating strongswan certificate")
        print("Generate Strongswan")
        return True

    def generate_wireguard_cert(
        self, servername, ip_list,
        cached_cert, _=None
    ):
        """Generates wireguard certificate.

        Args:
            servername (string): servername [PT#1]
            ip_list (list): the ips for the selected server
            cached_cert (string): path to where a certificate is to be cached
        Returns:
            bool
        """
        logger.info("Generating Wireguard certificate")
        print("Generate wireguard")
        return True

    @staticmethod
    def delete_cached_certificate(filename):
        """Delete cached certificate.

        Args:
            filename (string): path to cached certificate
        """
        logger.info("Deleting cached certificate")
        os.remove(filename)