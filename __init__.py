import requests
import xmltodict
import dicttoxml
import sys
from datetime import datetime, timezone, timedelta
from typing import Union

assert sys.version_info >= (3, 8)

def require(cond, msg):
    if not cond:
        raise Exception(msg)
    
class DongleE3372:
    __ver = (0,1,1)
    __slots__ = ["session", "gateway", "sesInfo", "tokInfo"]
    
    __api_points = {
        "session_tok_info":     "/api/webserver/SesTokInfo"
        , "bacis_information":  "/api/device/basic_information"
        , "status":             "/api/monitoring/status"
        , "module_switch":      "/api/global/module-switch"
        , "send_sms":           "/api/sms/send-sms"
        , "config":             "/config/global/config.xml"
    }
    
    def __init__(self, gateway="http://192.168.8.1") -> None:
        self.session = requests.Session()
        self.gateway = gateway        
        api = self.__api_points["session_tok_info"]
        responce = self.session.get(f"{gateway}{api}")
        session_info = xmltodict.parse(responce.text)
        self.sesInfo = session_info["response"]["SesInfo"]
        self.tokInfo = session_info["response"]["TokInfo"]        
    
    
    @classmethod
    def to_dict(cls, xml_str) -> dict:
        return xmltodict.parse(xml_str)    
       
    
    def get_request(self, api_endpoint: str) -> dict:
        url = "".join([self.gateway, api_endpoint])
        response = self.session.get(url)
        return self.to_dict(response.text) 
    

    def bacis_information(self) -> dict:
        api = self.__api_points["bacis_information"]
        resp = self.get_request(api)
        return resp
        
    def get_status(self) -> dict:
        api = self.__api_points["status"]
        resp = self.get_request(api)
        return resp 
    
    def module_switch(self) -> dict:
        api = self.__api_points["module_switch"]
        resp = self.get_request(api)
        return resp  

    def send_sms(self, phone_num: Union[str, list[str]] , message: str):
        require(len(message) <= 64, "too big message")
        now = self.now_time()
        number = phone_num
        api = self.__api_points["send_sms"]
        data1 = {
            "Index": -1
            , "Phones":{
                "Phone": number
            }
            , "Sca": None
            , "Content": message
            , "Length": len(message)
            , "Reserved": 1
            , "Date": self.ts_2_str(now)
        } 
        xml = dicttoxml.dicttoxml(data1, custom_root='request', attr_type=False, return_bytes=False)        
        res = self.session.post(f"{self.gateway}{api}", data=xml.encode("utf-8"), 
            headers={"__RequestVerificationToken": self.tokInfo})
        response = self.to_dict(res.text)
        return response

    def config(self) -> dict:
        api = "/config/global/config.xml"
        resp = self.get_request(api)
        return resp

    def now_time(self) -> int:
        return int(datetime.now().timestamp())

    def time_2_str(self, time: Union[int, datetime]) -> str:
        #"yyyy-MM-dd HH:mm:ss"
        dt = time
        if isinstance(time, int):
            dt = datetime.fromtimestamp(time)
        str_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        return str_time