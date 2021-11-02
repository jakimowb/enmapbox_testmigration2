# see https://docs.docker.com/docker-cloud/builds/advanced/
# using ARG in FROM requires min v17.05.0-ce
ARG DOCKER_TAG=latest

FROM  qgis/qgis:final-3_22_0  # latest
MAINTAINER Benjamin Jakimow <benjamin.jakimow@geo.hu-berlin.de>

LABEL Description="Docker container with QGIS" Vendor="QGIS.org"

# build timeout in seconds, so no timeout by default
ARG BUILD_TIMEOUT=360000

COPY . /enmap-box

ENV QT_QPA_PLATFORM=offscreen
ENV XDG_RUNTIME_DIR='/tmp/runtime-root'

RUN mkdir /tmp/runtime-root && \
    # h5py is build against serial interface of HDF5-1.10.4. For parallel processing or newer versions see \
    # https://docs.h5py.org/en/latest/faq.html#building-from-git \
    # https://www.hdfgroup.org/downloads/hdf5/source-code/ \
    # and to an extent https://stackoverflow.com/questions/34119670/hdf5-library-and-header-mismatch-error
    HDF5_LIBDIR=/usr/lib/x86_64-linux-gnu/hdf5/serial HDF5_INCLUDEDIR=/usr/include/hdf5/serial pip install --no-binary=h5py h5py>=3.5.0 && \
    cd enmap-box && \
    python3 -m pip install -r requirements_docker.txt && \
    python3 scripts/setup_repository.py && \
    python3 scripts/create_plugin.py && \
    mkdir -p ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins && \
    cp -r deploy/enmapboxplugin ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins && \
#    cp -r enmapboxtestdata ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/enmapboxplugin/enmapbox && \
    qgis_process plugins enable enmapboxplugin

RUN rm -rf enmap-box
CMD ["qgis_process"]