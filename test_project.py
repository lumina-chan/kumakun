from kumakun import detect
from kumakun import validate
from kumakun import validate_url

def test_detect():
    #email
    assert detect("john-doe@gmail.com") == "email"
    assert detect("hello@example.com blah blah") == "email"
    assert detect("hello") == "unrecognised"
    assert detect("@example.com") == "unrecognised"

    #ipv4
    assert detect("200 .99999.0.1") == "unrecognised"
    assert detect("223.13.4.5") == "IPv4"
    assert detect("meow . woof . cat . dog") == "unrecognised"
    assert detect("....") == "unrecognised"

    #time
    assert detect("cat:dog pm") == "unrecognised"
    assert detect("123:20") == "unrecognised"
    assert detect("5:20") == "time"
    assert detect("12:20 PM") == "time"

    #url
    assert detect("http://example.com") == "URL"
    assert detect("https://example.com/search?q=lumina&test=123") == "URL"
    assert detect("ftps://example.com/page#section1") == "unrecognised"
    assert detect("https://xxxm") == "URL"


def test_validate():
    #email
    assert validate("email","malan@harvard.edu") == "Valid"
    assert validate("email", "malan@cs50.harvard.edu") == "Valid"
    assert validate("email", "dog^.^@meow.com") == "Invalid"
    assert validate("email", "abc@example") == "Invalid"

    #ipv4
    assert validate("IPv4", "192.168.1.1") == "Valid"
    assert validate("IPv4", "0.0.0.0") == "Valid"
    assert validate("IPv4", "255.255.255.255") == "Valid"
    assert validate("IPv4", "256.1.1.1") == "Invalid"
    assert validate("IPv4", "01.2.3.4") == "Invalid"
    assert validate("IPv4", "hello.1.2.3") == "Invalid"
    assert validate("IPv4", "192..1.1") == "Invalid"

    #time
    # time
    time = validate("time", "12:59 PM")
    assert time.result == "Valid, 12 hour format"

    time = validate("time", "0:00")
    assert time.result == "Valid, 24 hour format"

    time = validate("time", "12:30")
    assert time.result == "Valid, 24 hour format"

    time = validate("time", "23:59")
    assert time.result == "Valid, 24 hour format"

    assert validate("time", "5:60") == "Invalid"
    assert validate("time", "0:30 AM") == "Invalid"
    assert validate("time", "25:30") == "Invalid"
    assert validate("time", "5:20 XM") == "Invalid"
    assert validate("time", "5:20 AM PM") == "Invalid"
    assert validate("time", "abc:20") == "Invalid"
    assert validate("time", "13:30 AM") == "Invalid"

    #url
    assert validate("URL", "https://github.com") == "Valid"
    assert validate("URL", "https://cs50.harvard.edu/python/") == "Valid"
    assert validate("URL", "https://example-.com") == "Invalid"


def test_validate_url():
    assert validate_url("https://example.com/a/b/c") == "Valid"
    assert validate_url("https://example.com/search?foo=bar&x=1&hello=world") == "Valid"
    assert validate_url("https://example.com/docs#installation") == "Valid"
    assert validate_url("http://192.168.1.1") == "Valid"
    assert validate_url("http://localhost:8080") == "Valid"
    assert validate_url("https://") == "Invalid"
    assert validate_url("https://.com") == "Invalid"
    assert validate_url("https://example.") == "Invalid"
    assert validate_url("https://.example.com") == "Invalid"
    assert validate_url("ftp://example.com") == "Invalid"
    assert validate_url("file:///home/user/test.txt") == "Invalid"
    assert validate_url("mailto:user@example.com") == "Invalid"
    assert validate_url("https://sub.sub.example.co.uk/path/to/page?x=1&y=2#top") == "Valid"
    assert validate_url("https://....com") == "Invalid"
    assert validate_url("https://example..com") == "Invalid"
    assert validate_url("https://-example.com") == "Invalid"
