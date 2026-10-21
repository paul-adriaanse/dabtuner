FROM debian:13-slim

# Install core build toolchains, UHD drivers, and GUI-less Soapy components
RUN apt update && apt install -y --no-install-recommends \
#    git pkg-config \
#    build-essential cmake \
#    libusb-1.0-0-dev libuhd-dev librtlsdr-dev libmirisdr-dev \
    uhd-host soapysdr-module-uhd \
    librtlsdr0 rtl-sdr libmirisdr4 \
    soapysdr-tools soapysdr-module-rtlsdr soapysdr-module-rfspace soapysdr0.8-module-mirisdr miri-sdr \
    welle.io iproute2 procps python3 usbutils \
    && apt clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /app
COPY app/ /app/

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8008 8009

ENTRYPOINT ["entrypoint.sh"]
