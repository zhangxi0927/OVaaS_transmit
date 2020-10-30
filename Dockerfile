# To enable ssh & remote debugging on app service change the base image to the one below
FROM mcr.microsoft.com/azure-functions/python:3.0-python3.6-appservice
# FROM mcr.microsoft.com/azure-functions/python:3.0-python3.6

RUN apt update && \
  apt install -y build-essential cmake git pkg-config libgtk-3-dev \
  libavcodec-dev libavformat-dev libswscale-dev libv4l-dev \
  libxvidcore-dev libx264-dev libjpeg-dev libpng-dev libtiff-dev \
  gfortran openexr libatlas-base-dev python3-dev python3-numpy \
  libtbb2 libtbb-dev libdc1394-22-dev

RUN mkdir ~/opencv_build && cd ~/opencv_build && \
  git clone https://github.com/opencv/opencv.git && \
  git clone https://github.com/opencv/opencv_contrib.git

RUN cd ~/opencv_build/opencv && \
  git checkout 4.5.0-openvino && \
  mkdir build && cd build && \
  cmake -D CMAKE_BUILD_TYPE=RELEASE \
  -D CMAKE_INSTALL_PREFIX=/usr/local \
  -D OPENCV_GENERATE_PKGCONFIG=ON \
  -D OPENCV_EXTRA_MODULES_PATH=~/opencv_build/opencv_contrib/modules .. && \
  make -j4 && \
  make install

RUN export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

RUN rm -rf ~/opencv_build
RUN echo /usr/local/lib > /etc/ld.so.conf.d/opencv.conf && \
  ldconfig -v

RUN pip install --upgrade pip


ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
  AzureFunctionsJobHost__Logging__Console__IsEnabled=true

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY . /home/site/wwwroot