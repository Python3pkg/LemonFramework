"""
This file is part of Lemon.

Lemon is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Lemon is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Lemon.  If not, see <http://www.gnu.org/licenses/>.


Copyright (c) 2012 Vicente Ruiz <vruiz2.0@gmail.com>


See http://www.w3.org/Protocols/rfc2616/rfc2616-sec4.html#sec4.5,
    http://www.w3.org/Protocols/rfc2616/rfc2616-sec6.html#sec6.2 and
    http://www.w3.org/Protocols/rfc2616/rfc2616-sec7.html#sec7.1

4.5 General Header Fields

    Cache-Control            ; Section 14.9
    Connection               ; Section 14.10
    Date                     ; Section 14.18
    Pragma                   ; Section 14.32
    Trailer                  ; Section 14.40
    Transfer-Encoding        ; Section 14.41
    Upgrade                  ; Section 14.42
    Via                      ; Section 14.45
    Warning                  ; Section 14.46

6.2 Response Header Fields

    Accept-Ranges           ; Section 14.5
    Age                     ; Section 14.6
    ETag                    ; Section 14.19
    Location                ; Section 14.30
    Proxy-Authenticate      ; Section 14.33

    Retry-After             ; Section 14.37
    Server                  ; Section 14.38
    Vary                    ; Section 14.44
    WWW-Authenticate        ; Section 14.47

7.1 Entity Header Fields

    Allow                    ; Section 14.7
    Content-Encoding         ; Section 14.11
    Content-Language         ; Section 14.12
    Content-Length           ; Section 14.13
    Content-Location         ; Section 14.14
    Content-MD5              ; Section 14.15
    Content-Range            ; Section 14.16
    Content-Type             ; Section 14.17
    Expires                  ; Section 14.21
    Last-Modified            ; Section 14.29


"""
import abc
import cgi
from http.cookies import SimpleCookie

from lemon.http.exceptions import HttpResponseException


class HttpResponse(HttpResponseException, metaclass=abc.ABCMeta):
    """
    A basic HTTP response, with content and dictionary-accessed headers.
    """
    @abc.abstractproperty
    def status_code(self):
        pass

    @abc.abstractproperty
    def status_text(self):
        pass

    def __init__(self, content='', content_type=None):
        # _headers is a mapping of the lower-case name to the original
        # case of the header and the header value.
        self._headers = {}

        # Content-Type
        self.charset = 'utf-8'  # TODO settings
        self.set_content(content, content_type)

        # Cookies
        self._cookies = SimpleCookie()

    def set_content(self, content, content_type=None, content_encoding=None):
        self._content = content or ''

        if content_type:
            # Parsing the string
            self.content_type, pdict = cgi.parse_header(content_type)
            self.charset = pdict.get('charset', self.charset)

        else:
            self.content_type = 'text/html'  # TODO settings

        if type(content) == str:
            content_type = "%s; charset=%s" % (self.content_type, self.charset)
        else:
            content_type = self.content_type
        # Setting header Content-Type
        self['Content-Type'] = content_type

        # Setting header Content-Encoding
        if content_encoding:
            self['Content-Encoding'] = content_encoding

    def set_cookies(self, cookies):
        self._cookies.load(cookies.output(header=''))

    @property
    def status(self):
        return '%s %s' % (self.status_code, self.status_text)

    @property
    def headers(self):
        response_headers = [
            (key, value)
            for key, value in list(self._headers.values())
        ]

        response_headers += [
            ('Set-Cookie', morsel.output(header='').strip())
            for morsel in list(self._cookies.values())
        ]

        return response_headers

    @property
    def content(self):
        if type(self._content) == str:
            content = self._content.encode(self.charset)
        else:
            content = self._content
        return [ content ]

    def __setitem__(self, header, value):
        self._headers[header.lower()] = (header, value)

    def __delitem__(self, header):
        try:
            del self._headers[header.lower()]
        except KeyError:
            pass

    def __getitem__(self, header):
        return self._headers[header.lower()][1]

    def __str__(self):
        return 'HttpResponse <%s, %s>' % (self.status_code, self.status_text)
