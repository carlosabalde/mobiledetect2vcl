**mobiledetect2vcl** is a tiny Python script to transform the [Mobile Detect JSON database](https://github.com/serbanghita/Mobile-Detect) into an UA-based mobile detection VCL subroutine easily integrable in any [Varnish Cache](https://www.varnish-cache.org) configuration.

Usage
=====

1. Execute the script, optionally specifying the location of the JSON database, the name of the VCL subroutine, etc. (use the `--help` option for additional options):
    ```
    $ python mobiledetect2vcl.py > /etc/varnish/mobile_detect.vcl
    ```

2. Include the generated VCL in your Varnish Cache configuration, calling the mobile detection subroutine during the `vcl_recv` phase:
    ```
    include "mobile_detect.vcl";

    ...

    sub vcl_recv {
        call mobile_detect;

        if (req.http.X-Mobile-Category) {
            std.log("Mobile category: " + req.http.X-Mobile-Category)
            std.log("Mobile type: " + req.http.X-Mobile-Type)
        }
    }
    ```

3. Use the `X-Mobile-Category` (e.g. 'phones', 'browsers', 'tablets' or 'os') and `X-Mobile-Type` (e.g. 'iPhone', 'BlackBerry', 'iPad', etc.) HTTP headers in the `req` object as you wish. Some ideas:
    - Redirect mobile users to a different location.
    - Normalize the UA header using the device category / type.
    - Forward mobile requests to a specific backend.
    - Cache different versions (i.e. Vary header) of the same URL based on the normalized UAs.
  - ...

4. Optionally, you may also consider:
    - Set up periodical updates of the device detection VCL using a simple cron job.
    - Cache the result of the mobile detection subroutine in an user cookie.
    - Include some logic to bypass the mobile detection using some query string parameter.
    - ...

Thanks
======

A huge thank you to [Serban Ghita](https://github.com/serbanghita) and all the contributors for maintaining the [Mobile Detect database](http://mobiledetect.net/).

Also thanks to other similar projects you may want to consider:

- https://github.com/varnish/varnish-devicedetect
- https://github.com/willemk/varnish-mobiletranslate
