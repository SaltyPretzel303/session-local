FROM buildpack-deps:bullseye

ENV BUILD_PATH '/nginx_build'

ENV NGINX_VERSION nginx-1.23.2
# ENV NGINX_RTMP_MODULE_VERSION 1.2.0
ENV NGINX_RTMP_MODULE_VERSION 1.2.2
ENV DEVEL_KIT_VERSION 0.3.1
ENV SET_MISC_VERSION 0.33
ENV HMAC_SECURE_VERSION 0.3
ENV SUB_FILTER_VERSION 0.6.4
# ENV ECHO_VERSION 0.63
ENV PCRE_VERSION 8.45

# Required in order for rtmp-module to be built.
# Other solution would be to remove the -Werror flag from ... nginx/obj/Makefile.
ENV CFLAGS=-Wno-error

# Install dependencies
RUN apt-get update && \
	apt-get install -y ca-certificates openssl libssl-dev && \
	apt-get install python3 pip -y && \
	rm -rf /var/lib/apt/lists/*

# RUN mkdir -p /tmp/build && cd /tmp/build
WORKDIR ${BUILD_PATH}

# Download and decompress Nginx
RUN wget -O nginx.tar.gz https://nginx.org/download/${NGINX_VERSION}.tar.gz && \
	tar -zxf nginx.tar.gz && \
	rm nginx.tar.gz && \
	mv ${NGINX_VERSION} nginx

# Download and decompress RTMP module
RUN wget -O rtmp_module.tar.gz https://github.com/arut/nginx-rtmp-module/archive/v${NGINX_RTMP_MODULE_VERSION}.tar.gz && \
	tar -zxf rtmp_module.tar.gz && \
	rm rtmp_module.tar.gz && \
	mv nginx-rtmp-module-${NGINX_RTMP_MODULE_VERSION} rtmp_module

# Download and decompress devl_kit module
RUN wget -O devel_kit.tar.gz https://github.com/vision5/ngx_devel_kit/archive/v${DEVEL_KIT_VERSION}.tar.gz && \ 
	tar -xf devel_kit.tar.gz && \ 
	rm devel_kit.tar.gz && \
	mv ngx_devel_kit-${DEVEL_KIT_VERSION} devel_kit


RUN wget -O set_misc.tar.gz https://github.com/openresty/set-misc-nginx-module/archive/v${SET_MISC_VERSION}.tar.gz && \
	tar -xf set_misc.tar.gz && \
	rm set_misc.tar.gz && \
	mv set-misc-nginx-module-${SET_MISC_VERSION} set_misc

RUN wget -O hmac_secure.tar.gz https://github.com/nginx-modules/ngx_http_hmac_secure_link_module/archive/${HMAC_SECURE_VERSION}.tar.gz && \
	tar -xf hmac_secure.tar.gz && \
	rm hmac_secure.tar.gz && \
	mv ngx_http_hmac_secure_link_module-${HMAC_SECURE_VERSION} hmac_secure

RUN wget -O sub_filters.tar.gz https://github.com/yaoweibin/ngx_http_substitutions_filter_module/archive/v${SUB_FILTER_VERSION}.tar.gz && \
	tar -xf sub_filters.tar.gz && \
	rm sub_filters.tar.gz && \
	mv ngx_http_substitutions_filter_module-${SUB_FILTER_VERSION} sub_filters

# RUN wget -O echo.tar.gz https://github.com/openresty/echo-nginx-module/archive/refs/tags/v${ECHO_VERSION}.tar.gz && \
# 	tar -xf echo.tar.gz && \
# 	rm echo.tar.gz && \
# 	mv echo-nginx-module-${ECHO_VERSION} echo_module

RUN wget -O pcre.tar.gz https://sourceforge.net/projects/pcre/files/pcre/${PCRE_VERSION}/pcre-${PCRE_VERSION}.tar.gz/download && \
	tar -xf pcre.tar.gz && \
	rm pcre.tar.gz && \
	mv pcre-${PCRE_VERSION} pcre

# Build and install Nginx
# The default puts everything under /usr/local/nginx, so it's needed to change
# it explicitly. Not just for order but to have it in the PATH
RUN	cd nginx && \
		./configure \
		--sbin-path=/usr/local/sbin/nginx \
		--conf-path=/etc/nginx/nginx.conf \
		--error-log-path=/var/log/nginx/error.log \
		--pid-path=/var/run/nginx/nginx.pid \
		--lock-path=/var/lock/nginx/nginx.lock \
		--http-log-path=/var/log/nginx/access.log \
		--http-client-body-temp-path=/tmp/nginx-client-body \
		--with-http_ssl_module \
		--with-http_sub_module \
		--with-http_auth_request_module \
		--with-threads \
		--with-ipv6 \
		--with-pcre=${BUILD_PATH}/pcre \
		--with-pcre-jit \ 
		--with-stream=dynamic \
		--with-stream_ssl_module \
		--add-module=${BUILD_PATH}/rtmp_module \
		--add-module=${BUILD_PATH}/devel_kit \
		--add-module=${BUILD_PATH}/set_misc \
		--add-module=${BUILD_PATH}/hmac_secure \
		--add-module=${BUILD_PATH}/sub_filters \
		--with-debug
		# --add-module=${BUILD_PATH}/echo_module \
		# --with-google_perftools_module \



RUN cd nginx && \
	make -j $(getconf _NPROCESSORS_ONLN) && \
	make install

RUN	mkdir /var/lock/nginx && \
	mkdir /var/www && mkdir /var/www/live
	

# This will install very old verison of ffmpeg. 
# Consider doing custom build or specific version download. 
RUN apt update; apt install ffmpeg -y

# Forward logs to Docker
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
	ln -sf /dev/stderr /var/log/nginx/error.log

RUN useradd nginx

ENTRYPOINT ["nginx","-g","daemon off;"]
