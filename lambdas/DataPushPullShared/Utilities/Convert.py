import json
import datetime
from pytz import timezone
import re

class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class Convert:

    @staticmethod
    def toDict(obj):
        if isinstance(obj, dict):
            return {k: Convert.toDict(v) for k, v in obj.items()}
        elif hasattr(obj, "_ast"):
            return Convert.toDict(obj._ast())
        elif not isinstance(obj, str) and hasattr(obj, "__iter__"):
            return [Convert.toDict(v) for v in obj]
        elif hasattr(obj, "__dict__"):
            return {
                k: Convert.toDict(v)
                for k, v in obj.__dict__.items()
                if not callable(v) and not k.startswith('_')
            }
        else:
            return obj

    @staticmethod
    def toJson(obj):
        if isinstance(obj, dict):
            return json.dumps(obj)
        elif isinstance(obj, object):
            return json.dumps(Convert.toDict(obj))
        else:
            return obj

    @staticmethod
    def toObj(obj):
        if isinstance(obj, list):
            obj = [Convert.toObj(x) for x in obj]
        if not isinstance(obj, dict):
            return obj

        class C(object):
            pass

        o = C()
        for k in obj:
            o.__dict__[k] = Convert.toObj(obj[k])
        return o

    @staticmethod
    def toFloat(obj):
        if obj is None:
            obj = 0.0
        else:
            obj = float(obj)
        return obj

    @staticmethod
    def toInt(obj):
        if obj is None:
            obj = 0
        else:
            obj = int(obj)
        return obj

    @staticmethod
    def dateConverter(o):
        if isinstance(o, datetime.datetime):
            return o.__str__()
    
    @staticmethod
    def dateValidator(date:datetime.datetime):
        if isinstance(date, type(None)):
            return None
        else:
            return date.strftime("%Y-%m-%dT%H:%M:%S.%f")

    @staticmethod
    def format_date(input_date_str: str, from_format: str, to_format: str):
        return datetime.datetime.strptime(input_date_str, from_format).strftime(to_format)
    
    @staticmethod
    def get_msttz():
        return (datetime.datetime.now(timezone('MST')).strftime("%m/%d/%YT%H:%M:%S"))
    
    @staticmethod
    def convert_datetime_timezone(dt, from_timezone, to_timezone, from_format, to_format):
        """
        Convert datetime format and timezone
        """
        dt = timezone(from_timezone).localize(datetime.datetime.strptime(re.sub('[a-zA-Z]','', dt), from_format))
        dt = dt.astimezone(timezone(to_timezone))
        dt = dt.strftime(to_format)
        return dt
    
    @staticmethod
    def generate_time_slots(input_list):
        '''
        Method to tour availability time slots based on input list of dict
        '''
        final_result = []

        for i in range(len(input_list)):
            start, end = input_list[i].values()
            res = []
            start_time = datetime.datetime.strptime(start, '%Y-%m-%dT%H:%M:%S')
            start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
            sth,stm = start_time.hour,start_time.minute
            end_time = datetime.datetime.strptime(end, '%Y-%m-%dT%H:%M:%S')
            end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
            eth,etm = end_time.hour, end_time.minute
            if (abs(sth-eth) in (0,1) and abs(stm-etm) in (15,45)) :
                continue;
            maximum = max(sth,eth)
            if sth == maximum:
                res.append(start_time_str)
                while sth >= eth:
                    if (sth==eth and (stm-etm)<=15) :
                        break;
                    final_time = start_time - datetime.timedelta(minutes = 30)
                    final_time_str = final_time.strftime('%Y-%m-%d %H:%M:%S')
                    res.append(final_time_str)
                    start_time = final_time
                    sth,stm = final_time.hour, final_time.minute
            elif eth == maximum:
                res.append(end_time_str)
                while eth >= sth:
                    if (sth==eth and (etm-stm)<=15) :
                        break;
                    final_time = end_time - datetime.timedelta(minutes = 30)
                    final_time_str = final_time.strftime('%Y-%m-%d %H:%M:%S')
                    res.append(final_time_str)
                    end_time = final_time
                    eth,etm = final_time.hour, final_time.minute
            final_result += res
        return sorted(list(set(final_result)))

    @staticmethod
    def round_to(value: float):
        return(round(value,2))

    @staticmethod
    def get_utc(dates, date_zone):
        utc_dt_list = []
        for date in dates:
            dt = timezone(date_zone).localize(datetime.datetime.strptime(re.sub('[a-zA-Z]','', date), '%Y-%m-%d %H:%M:%S'))
            dt = dt.astimezone(timezone('UTC'))
            dt = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
            utc_dt_list.append(dt)
        return utc_dt_list
