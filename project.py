#main project : Kumakun (A CLI Detector & Parser)
# Kumakun: A command-line utility that accepts different kinds of input, identifies what the input represents, validates it, parses useful information from it, and presents the result in a structured way.

import sys, re
from urllib.parse import urlsplit
import ipaddress
from tabulate import tabulate
import tldextract

class URL:
    def __init__(self, url):
        self.raw_url = url
        self.parsed = urlsplit(url)
        self.scheme = self.parsed.scheme
        self.netloc = self.parsed.netloc
        self.path = self.parsed.path
        self.query = self.parsed.query
        self.fragment = self.parsed.fragment
        self.user = self.parsed.username
        self.password = self.parsed.password
        self.host = self.parsed.hostname
        self.port = self.parsed.port

class Time:
    def __init__(self, time):
        self.time = time
        self.result = None

def main():
    if len(sys.argv) != 2:
        sys.exit("Insufficient arguments")
    input_type: str = detect(sys.argv[1].strip())
    result = validate(input_type, sys.argv[1].strip())
    parsed: dict = parser(input_type, result, sys.argv[1])
    display(input_type, result, parsed)

#sole purpose in life: detect input_type of input
def detect(n: str):
    if re.fullmatch(r".+@.+\..+", n, re.IGNORECASE):
        return 'email'
    elif re.fullmatch(r"\d+\.\d+\.\d+\.\d+", n):
        return "IPv4"
    elif re.fullmatch(r"(\d{1,2}(?::\d{2})?)\s?(am|pm)?", n, re.IGNORECASE):
        try :
            if isinstance(int(n), int): return "unrecognised"
        except ValueError:
            pass
        return "time"
    elif re.fullmatch(r"https?://(www\.)?.+\.?.+", n):
        return "URL"
    else:
        return 'unrecognised'

#sole purpose in life: check for input_type and send to respective validation functions
def validate(input_type, n: str):
    if input_type == "email":
        return validate_email(n)
    elif input_type == "IPv4":
        return validate_ipv4(n)
    elif input_type == "time":
        return validate_time(n)
    elif input_type == "URL":
        return validate_url(n)
    else:
        return "unrecognised type have no result validation"

#validate email: Valid or Invalid
def validate_email(n: str):
    if re.fullmatch(r"[a-zA-Z0-9!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}\.(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+", n):
        return "Valid"
    else:
        return "Invalid"

#validate ipv4: Valid or Invalid
def validate_ipv4(ip: str):
    try:
        ip = ipaddress.ip_address(ip)
    except ValueError:
        return "Invalid"
    else:
        if ip.version == 4:
            return "Valid"
        else:
            return "Invalid"

#validate time: Valid 12h or 24h or Invalid
def validate_time(time: str):
    if matches:=re.fullmatch(r"(\d{1,2}(?::\d{2})?)\s?(am|pm)?", time, re.IGNORECASE):
        marker = matches.group(2)
        time = matches.group(1)
        if marker == None:
            marker = 'None'
        if ":" not in time.strip():
            time += ":00"
        hr, min = time.split(":")
        min = min.split(" ")[0]
        hr = int(hr)
        min = int(min)
        if 0 <= min <= 59:
            if 1 <= hr <= 12 and marker.strip().lower() in ["am", "pm"]:
                time_obj = Time(time)  #this Time() object will be passed around
                time_obj.time += f" {marker.strip().lower()}"
                time_obj.result = "Valid, 12 hour format"
                return time_obj
            elif 0 <= hr < 24 and marker == "None":
                time_obj = Time(time)
                time_obj.result = "Valid, 24 hour format"
                return time_obj
        else:
            return "Invalid"
    return "Invalid"

#validate url: Valid or Invalid
def validate_url(url_: str):
    try:
        url = URL(url_) #objet of class URL
    except ValueError:
        return "Invalid"

    if url.scheme not in ["http", "https"]:
        return "Invalid"

    if not url.netloc:
        return "Invalid"

    if any(character.isspace() for character in url.raw_url):
        return "Invalid"

    host = url.host

    if host is None:
        return "Invalid"

    if host == "localhost":
        return "Valid"

    if validate_ipv4(host) == "Valid":
        return "Valid"

    labels = host.split(".")

    if len(labels) < 2 or len(host) > 253:
        return "Invalid"

    if not all(
        label
        and len(label) <= 63
        and re.fullmatch(r"[a-zA-Z0-9-]+", label)
        and not label.startswith("-")
        and not label.endswith("-")
        for label in labels
    ):
        return "Invalid"
    return "Valid"

#sole purpose in life: check for type n go to individual parser
def parser(input_type: str,res, n):
    if isinstance(res, Time):
        time_obj = res
        res = res.result
    if "Valid" in res:
        if input_type == "email":
            return parse_email(n)
        elif input_type == "IPv4":
            return parse_ipv4(n)
        elif input_type == "time":
            return parse_time(time_obj)
        elif input_type == "URL":
            return parse_url(n)
    else:
        return {"attributes":"unrecognised type have nothing to display"}

#parse email
def parse_email(email: str):
    local, domain = email.split("@")
    domain_labels = domain.split(".")
    tld = domain_labels[-1]
    return {"email":email, "local":local, "domain":domain, "domain_labels": domain_labels, "tld": tld}

#parse ipv4
def parse_ipv4(ip: str):
    octets = ip.split(".")
    ip = ipaddress.IPv4Address(ip)
    ver = ip.version
    if ip.is_global:
        net_type = "global" 
    elif ip.is_private:
        net_type = "private" 
    else:
        net_type = "undefined"
    loopback = ip.is_loopback
    multicast = ip.is_multicast
    return {"address":ip, "octets":octets, "version":ver, "net_type": net_type, "loopback": loopback, "multicast": multicast} 

#parse time
def parse_time(time_obj):
    fmt = time_obj.result
    time = time_obj.time
    fmt = fmt.split(" ")[1] + "-hour"
    period = None
    if fmt == "12-hour":
        time, period = time.split(" ")
    hrs, mins = time.split(":")
    hrs = int(hrs)
    mins = int(mins)
    if fmt == "12-hour":
        if period.lower() == "am":
            if hrs == 12:
                hrs = 0
        if period.lower() == "pm":
            if hrs != 12:
                hrs+=12
    mins_mid = hrs*60 + mins
    tod = ''
    if 0 <= mins_mid <= 359:
        tod = "night"
    elif 360 <= mins_mid <= 719:
        tod = "morning"
    elif 720 <= mins_mid <= 1019:
        tod = "afternoon"
    elif 1020 <= mins_mid <= 1259:
        tod = "evening"
    elif 1260 <= mins_mid <= 1439:
        tod = "night"
    
    return {"time":time, "hour":hrs, "minute":mins, "format": fmt, "period":period, "time_of_day":tod, "minutes_since_midnight":mins_mid}

#parse url
def parse_url(url_: str):
    url = URL(url_)
    extract = tldextract.TLDExtract(include_psl_private_domains=True)
    x = extract(url.raw_url)
    subdom = x.subdomain
    sld = x.domain
    tld = x.suffix
    data = {
            "url": url.raw_url,
            "scheme":url.scheme,
            "netloc":url.netloc,
            "path":url.path,
            "query":url.query,
            "fragment":url.fragment,
            "username":url.user,
            "password":url.password,
            "hostname":url.host,
            "subdomain":subdom,
            "domain":sld,
            "tld/public suffix":tld,
            "port":url.port
            }
    for key in data:
        if data[key] == '' or data[key] == [] :
            data[key] = None
    return data

#sole pupose in life: display the parsed info (dict, key value pairs)
def display(input_type: str, result, data: dict):
    if isinstance(result, Time):
        result = result. result
    print(f"\nTYPE DETECTED:\n{input_type}")
    print("\n")
    print(f"RESULT VALIDATION:\n{result}")
    final_data = [[key, value if value is not None else "None"] for key, value in data.items()]
    print("\nPARSED INFO:")
    print(tabulate(final_data, headers=["FIELD","VALUE"], tablefmt="heavy_outline", colglobalalign="left", headersglobalalign="center"))  


if __name__ == "__main__":
    main()
