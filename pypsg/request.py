
from typing import Union
import requests
import re

from pypsg.cfg import PyConfig, BinConfig
from pypsg import settings
from pypsg.rad import PyRad

class PSGResponse:
    def __init__(
        self,
        cfg: PyConfig=None,
        rad: PyRad=None
    ):
        self.cfg = cfg
        self.rad = rad
    @classmethod
    def from_bytes(cls,b:bytes):
        pattern = rb'results_([\w]+).txt'
        split_text = re.split(pattern,b)
        names = split_text[1::2]
        content = split_text[2::2]
        data = {}
        for name,dat in zip(names,content):
            data[name] = dat.strip()
        return cls(
            cfg=PyConfig.from_bytes(data['cfg']),
            rad=PyRad.from_bytes(data['rad'])
        )
        


class APICall:
    """
    A class to call the PSG API.

    Parameters
    ----------
    cfg : Config
        The PSG configuration.
    output_type : str or None
        The type of output to ask for.
    app : str or None
        The app to use.
    url : str
        The URL to send the request to.

    Attributes
    ----------
    cfg : Config
        The PSG configuration.
    output_type : str or None
        The type of output to ask for.
    app : str or None
        The app to use.
    url : str
        The URL to send the request to.
    """

    def __init__(
        self,
        cfg: Union[BinConfig, PyConfig],
        output_type:str = None,
        app: str = None,
        url: str = None
    ):
        self.cfg = cfg
        self.type = output_type
        self.app = app
        self.url = url
        if self.url is None:
            self.url = settings.get_setting('url')
        self._validate()

    def _validate(self):
        """
        Validate a class instance.

        Raises
        ------
        TypeError
            If self.cfg is not a Config object.
        TypeError
            If self.type is not a string or None.
        TypeError
            If self.app is not a string or None.
        TypeError
            If self.url is not a string.
        """
        if not isinstance(self.cfg, (PyConfig, BinConfig)):
            raise TypeError('apiCall.cfg must be a PyConfig or BinaryConfig object')
        if not (isinstance(self.type, str) or self.type is None):
            raise TypeError('apiCall.type must be a string or None')
        if not (isinstance(self.app, str) or self.app is None):
            raise TypeError('apiCall.app must be a string or None')
        if not isinstance(self.url, str):
            raise TypeError('apiCall.url must be a string')
    
    @property
    def is_single_file(self):
        if isinstance(self.type,(tuple,list)):
            return False
        if self.type == 'all':
            return False
        return True
        
    def __call__(self) -> bytes:
        """
        Call the PSG API

        Returns
        -------
        bytes
            The reply from PSG.
        """
        data = dict(file=self.cfg.content)
        if self.type is not None:
            data['type'] = self.type
        if self.app is not None:
            data['app'] = self.app
        api_key = settings.get_setting('api_key')
        if api_key is not None:
            data['key'] = api_key
        reply = requests.post(
            url=self.url,
            data=data,
            timeout=settings.REQUEST_TIMEOUT
        )
        if reply.status_code != 200:
            raise requests.exceptions.HTTPError(reply.content)
        if not self.is_single_file:
            return PSGResponse.from_bytes(reply.content)
        elif self.type == 'cfg':
            return PSGResponse(
                cfg=PyConfig.from_bytes(reply.content),
            )
        elif self.type == 'rad':
            return PSGResponse(
                rad=PyRad.from_bytes(reply.content),
            )
        else:
            raise ValueError('Unknown output type')
