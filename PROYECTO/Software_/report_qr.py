"""Application-entry QR. No default address, report identifier or credentials."""
from io import BytesIO
import os
from urllib.parse import urlsplit, urlunsplit
import ipaddress
import qrcode


def app_link(base_url=None):
    base = os.getenv('IMPULSO_PUBLIC_URL',base_url or '').strip()
    if not base:
        raise ValueError("Falta la URL real de IMPULSO. Configura IMPULSO_PUBLIC_URL; todavía no se genera un QR.")
    parts = urlsplit(base)
    if (parts.scheme not in ('http','https') or not parts.hostname or parts.username or parts.password
            or parts.query or parts.fragment):
        raise ValueError("La URL de IMPULSO debe ser HTTP/HTTPS, sin credenciales, parámetros ni fragmentos.")
    host=parts.hostname.lower()
    if (host=='localhost' or host.endswith(('.localhost','.example','.invalid','.test'))
            or host in ('example.com','example.org','example.net') or any(c in base for c in '<>{}')):
        raise ValueError("Configura una dirección real del servidor; no se admite localhost ni una URL de ejemplo.")
    try:
        address=ipaddress.ip_address(host)
    except ValueError:
        if '.' not in host or parts.scheme!='https':
            raise ValueError("La publicación por dominio requiere una URL HTTPS real.")
    else:
        if address.is_loopback or address.is_unspecified or address.is_multicast or address.is_link_local:
            raise ValueError("La dirección no es accesible desde otro dispositivo.")
        if parts.scheme!='https' and not is_lan_link(base):
            raise ValueError("La publicación en Internet requiere HTTPS; HTTP se reserva para pruebas LAN.")
    try:
        parts.port
    except ValueError as exc:
        raise ValueError("Puerto de la URL no válido.") from exc
    return urlunsplit((parts.scheme,parts.netloc,parts.path.rstrip('/')+'/', '', ''))


def qr_png(url):
    output = BytesIO()
    qrcode.make(url,error_correction=qrcode.constants.ERROR_CORRECT_M,border=4).save(output,format='PNG')
    return output.getvalue()


def is_lan_link(url):
    try:
        address=ipaddress.ip_address(urlsplit(url).hostname or '')
    except ValueError:
        return False
    return any(address in ipaddress.ip_network(net) for net in ('10.0.0.0/8','172.16.0.0/12','192.168.0.0/16','fc00::/7'))
