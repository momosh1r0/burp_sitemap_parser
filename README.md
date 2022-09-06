# burp_sitemap_parser

Parse burp items saved file and extract urls, cookies, post parameters and get parameters to create a csv file.

### Installation
```
root@Orion:~/burp_sitemap_parser# pip install -r requirements.txt
```

### Usage

```
root@Orion:~/burp_sitemap_parser# python burp-sitemap-parser.py burpsuite-items-export
```

### Result 

SITEMAP:
 - /index.php
   - WC
   - mo
   - me
   - time
 - /login
   - WC
   - username
   - password
   - bind_ip
   - login
 - /js/module/WeChall/wc.js
   - WC
   - v
 - /js/php.js
   - WC
   - v
 - /js/gwf3bb.js
   - WC
   - v
 - /js/module/Heart/hb.js
   - WC
 - /js/gwf3.js
   - WC
   - v
 - /js/jquery-2.1.4.min.js
   - WC
 - /
